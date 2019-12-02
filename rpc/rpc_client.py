# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
from itertools import chain
from configs import log
import rpyc
from rpyc.utils.classic import obtain
import queue
from gevent.queue import LifoQueue


class Connection(object):
    """rpc连接对象"""

    def __init__(self, host, port):
        """新建RPC连接"""
        self.conn = rpyc.connect(host, port, config={'allow_pickle': True})
        self.rpc = self.conn.root
        self.pid = os.getpid()

    def disconnect(self):
        """关闭RPC连接"""
        self.conn and self.conn.close()


class ConnectionPool(object):
    """rpc连接池"""

    def __init__(self, connection_class=Connection, max_connections=None, **connection_kwargs):
        """初始化"""
        max_connections = max_connections or 2 ** 31
        if not isinstance(max_connections, int) or max_connections < 0:
            raise ValueError('"max_connections" must be a positive integer')
        self.connection_class = connection_class
        self.connection_kwargs = connection_kwargs
        self.max_connections = max_connections
        self.reset()

    def reset(self):
        """重置连接池"""
        # 进程id
        self.pid = os.getpid()
        # 已生成连接数
        self._created_connections = 0
        # 可使用连接
        self._available_connections = []
        # 使用中连接
        self._in_use_connections = set()
        # 线程锁
        self._check_lock = threading.Lock()

    def _checkpid(self):
        """检查进程同步"""
        if self.pid != os.getpid():
            with self._check_lock:
                if self.pid == os.getpid():
                    return
                self.disconnect()
                self.reset()

    def get_connection(self, command_name, *keys, **options):
        """获取rpc连接"""
        self._checkpid()
        try:
            # 获取rpc连接
            connection = self._available_connections.pop()
        except IndexError:
            # 生成连接
            connection = self.make_connection()
        # 添加使用中连接
        self._in_use_connections.add(connection)
        return connection

    def make_connection(self):
        """新建rpc连接"""
        if self._created_connections >= self.max_connections:
            raise ConnectionError("Too many connections")
        self._created_connections += 1
        return self.connection_class(**self.connection_kwargs)

    def release(self, connection):
        """向连接池释放rpc连接"""
        self._checkpid()
        if connection.pid != self.pid:
            return
        self._in_use_connections.remove(connection)
        self._available_connections.append(connection)

    def disconnect(self):
        """断开rpc连接池中所有连接"""
        all_conns = chain(self._available_connections, self._in_use_connections)
        for connection in all_conns:
            connection.disconnect()

class BlockingConnectionPool(ConnectionPool):
    """ 分布式线程安全连接池
    Thread-safe blocking connection pool::
    # >>> from redis.client import Redis
    # >>> client = Redis(connection_pool=BlockingConnectionPool())
    It performs the same function as the default
    ``:py:class: ~redis.connection.ConnectionPool`` implementation, in that,
    it maintains a pool of reusable connections that can be shared by
    multiple redis clients (safely across threads if required).
    The difference is that, in the event that a client tries to get a
    connection from the pool when all of connections are in use, rather than
    raising a ``:py:class: ~redis.exceptions.ConnectionError`` (as the default
    ``:py:class: ~redis.connection.ConnectionPool`` implementation does), it
    makes the client wait ("blocks") for a specified number of seconds until
    a connection becomes available.
    Use ``max_connections`` to increase / decrease the pool size::
    # >>> pool = BlockingConnectionPool(max_connections=10)
    Use ``timeout`` to tell it either how many seconds to wait for a connection
    to become available, or to block forever:
    # Block forever.
    # >>> pool = BlockingConnectionPool(timeout=None)
    # Raise a ``ConnectionError`` after five seconds if a connection is
    # not available.
    # >>> pool = BlockingConnectionPool(timeout=5)
    """
    def __init__(self, max_connections=50, timeout=20,
                 connection_class=Connection, queue_class=LifoQueue,
                 **connection_kwargs):
        self.queue_class = queue_class
        self.timeout = timeout
        super(BlockingConnectionPool, self).__init__(
            connection_class=connection_class,
            max_connections=max_connections,
            **connection_kwargs)

    def reset(self):
        self.pid = os.getpid()
        self._check_lock = threading.Lock()
        # Create and fill up a thread safe queue with ``None`` values.
        self.pool = self.queue_class(self.max_connections)
        while True:
            try:
                self.pool.put_nowait(None)
            except queue.Full:
                break
        # Keep a list of actual connection instances so that we can
        # disconnect them later.
        self._connections = []

    def make_connection(self):
        "Make a fresh connection."
        connection = self.connection_class(**self.connection_kwargs)
        self._connections.append(connection)
        return connection

    def get_connection(self, command_name, *keys, **options):
        """
        Get a connection, blocking for ``self.timeout`` until a connection
        is available from the pool.
        If the connection returned is ``None`` then creates a new connection.
        Because we use a last-in first-out queue, the existing connections
        (having been returned to the pool after the initial ``None`` values
        were added) will be returned before ``None`` values. This means we only
        create new connections when we need to, i.e.: the actual number of
        connections will only increase in response to demand.
        """
        # Make sure we haven't changed process.
        self._checkpid()
        # Try and get a connection from the pool. If one isn't available within
        # self.timeout then raise a ``ConnectionError``.
        connection = None
        try:
            connection = self.pool.get(block=True, timeout=self.timeout)
        except queue.Empty:
            # Note that this is not caught by the redis client and will be
            # raised unless handled by application code. If you want never to
            raise ConnectionError("No connection available.")
        # If the ``connection`` is actually ``None`` then that's a cue to make
        # a new connection to add to the pool.
        if connection is None:
            connection = self.make_connection()
            log.info('获取链接: %s' % id(connection))
        return connection

    def release(self, connection):
        "Releases the connection back to the pool."
        # Make sure we haven't changed process.
        self._checkpid()
        if connection.pid != self.pid:
            return
        # Put the connection back into the pool.
        try:
            self.pool.put_nowait(connection)
        except queue.Full:
            # perhaps the pool has been reset() after a fork? regardless,
            # we don't want this connection
            pass

    def disconnect(self):
        "Disconnects all connections in the pool."
        for connection in self._connections:
            connection.disconnect()


class RPCClient(object):
    def __init__(self, host, port):
        self.connection_pool = ConnectionPool(connection_class=Connection, host=host, port=port)

    def close(self):
        """关闭RPC连接池"""
        self.connection_pool.disconnect()

    def __getattr__(self, name):
        return lambda *args, **kwargs: self(name, *args, **kwargs)

    def __call__(self, name, *args, **kwargs):
        for _ in range(10):
            connection = self.connection_pool.get_connection('')
            try:
                result = connection.rpc.__getattr__(name)(*args, **kwargs)
                return obtain(result)
            except Exception as e:
                self.connection_pool.disconnect()
                self.connection_pool.reset()
                log.warn('调用RPC失败: [error: %s]' % e, exc_info=True)
                continue
            finally:
                self.connection_pool.release(connection)
                break
