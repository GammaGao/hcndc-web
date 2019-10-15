#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymssql


class MssqlConn(object):
    """数据库连接类"""

    def __init__(self, host, port, user, password, database, cursorclass=False):
        if cursorclass:
            as_dict = True
        else:
            as_dict = False

        self.conn = pymssql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8',
            autocommit=True,
            login_timeout=10,
            as_dict=as_dict
        )

        self.cursor = self.conn.cursor()

    def get_conn(self):
        return self.conn

    def run(self, sql, args=None):
        """执行sql"""
        if args and isinstance(args, list):
            self.cursor.executemany(sql, args)
        else:
            self.cursor.execute(sql, args)
        return self.cursor

    def insert(self, sql, args=None):
        """写入"""
        cursor = self.run(sql, args)
        row_id = cursor.lastrowid
        return row_id

    def update(self, sql, args=None):
        """更新"""
        cursor = self.run(sql, args)
        row_id = cursor.rowcount
        return row_id

    def delete(self, sql, args=None):
        """删除"""
        cursor = self.run(sql, args)
        row_count = cursor.rowcount
        return row_count

    def query(self, sql, args=None):
        """查询"""
        cursor = self.run(sql, args)
        return cursor.fetchall()

    def query_one(self, sql, args=None):
        """查询一条数据"""
        cursor = self.run(sql, args)
        return cursor.fetchone()

    def query_many(self, sql, num=50000, args=None):
        """批量查询"""
        cursor = self.run(sql, args)
        result = cursor.fetchmany(num)
        while result:
            for i in result:
                yield i
            result = cursor.fetchmany(num)

    def query_columns(self, sql, args=None):
        """查询字段名"""
        cursor = self.run(sql, args)
        return [i[0] for i in cursor.description]
