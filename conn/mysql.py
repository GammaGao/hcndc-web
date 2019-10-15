#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import pymysql.cursors
# import mysql.connector


class MysqlConn(object):
    """mysql连接类"""

    def __init__(self, host, port, user, password, database, cursorclass=False, sscursor=False, **kwargs):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.cursorclass = cursorclass
        self.sscursor = sscursor
        self.retry = 0

        if cursorclass:
            cursorclass = pymysql.cursors.DictCursor
        else:
            cursorclass = pymysql.cursors.Cursor

        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            passwd=password,
            db=database,
            charset='utf8',
            autocommit=True,
            # local_infile=False,
            cursorclass=cursorclass,
            connect_timeout=10
        )

        if sscursor:
            self.cursor = self.conn.cursor(pymysql.cursors.SSCursor)
        else:
            self.cursor = self.conn.cursor()

    def get_conn(self):
        return self.conn

    def run(self, sql, args=None):
        """执行sql"""
        try:
            if args and isinstance(args, list):
                self.cursor.executemany(sql, args)
            else:
                self.cursor.execute(sql, args)
            return self.cursor
        except (pymysql.err.OperationalError, BrokenPipeError):
            if not self.retry:
                self.retry = 1
                # 大表超时处理
                self.__init__(self.host, self.port, self.user, self.password, self.database, self.cursorclass,
                              self.sscursor)
                self.run(sql, args)

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

    def query_many(self, sql, num=5000, args=None):
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


if __name__ == '__main__':
    opts = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'hcndc',
        'cursorclass': True
    }
    cursor = MysqlConn(**opts)
    result = cursor.query_one('SHOW DATABASES')
    print(result)
