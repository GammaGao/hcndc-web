#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class MysqlConn(object):
    """mysql连接类"""

    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.retry = 0

        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        # 自动提交
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
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
        except:
            raise

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
        'host': '172.16.163.8',
        'port': 5432,
        'user': 'admin',
        'password': '123456',
        'database': 'etl_test'
    }
    cursor = MysqlConn(**opts)
    result = cursor.update('SELECT * FROM "public"."sys_dept" limit 10;')
    print(result)
