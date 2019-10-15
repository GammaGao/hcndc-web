# !/usr/bin/python
# -*- coding: utf-8 -*-
from impala.dbapi import connect


class ImpalaLink(object):
    """mysql数据库操作类"""

    def __init__(self, host, port, user, password, database, auth_mechanism='NOSASL'):
        self.conn = connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            auth_mechanism=auth_mechanism,
            timeout=10
        )

    def execute(self, sql, args):
        """执行"""
        cursor = self.conn.cursor()
        if args and isinstance(args, list):
            cursor.executemany(sql, args)
        else:
            cursor.execute(sql, args)
        return cursor

    def insert(self, sql, args=None):
        """插入记录"""
        cursor = None
        try:
            cursor = self.execute(sql, args)
            row_id = cursor.lastrowid
            return row_id
        except:
            raise
        finally:
            cursor and cursor.close()

    def update(self, sql, args=None):
        """更新记录"""
        cursor = None
        try:
            cursor = self.execute(sql, args)
            row_count = cursor.rowcount
            if not row_count:
                return 0
            return row_count
        except:
            raise
        finally:
            cursor and cursor.close()

    def delete(self, sql, args=None):
        """删除记录"""
        cursor = None
        try:
            cursor = self.execute(sql, args)
            row_count = cursor.rowcount
            return row_count
        except:
            raise
        finally:
            cursor and cursor.close()

    def query(self, sql, args=None):
        """查询"""
        cursor = None
        try:
            cursor = self.execute(sql, args)
            return cursor.fetchall()
        except:
            raise
        finally:
            cursor and cursor.close()

    def query_one(self, sql, args=None):
        """查询返回一条数据"""
        cursor = None
        try:
            cursor = self.execute(sql, args)
            return cursor.fetchone()
        except:
            raise
        finally:
            cursor and cursor.close()


if __name__ == '__main__':
    # hive, 无密码, 无kerberos
    opts = {
        'host': '172.16.163.5',
        'port': 10000,
        'auth_mechanism': 'PLAIN'
    }

    # impala, 无密码, 无kerberos
    # opts = {
    #     'host': '172.16.163.5',
    #     'port': 21050
    # }

    # impala, 有密码, 有kerberos
    # opts = {
    #     'host': '172.16.163.216',
    #     'port': 21050,
    #     'auth_mechanism': 'PLAIN',
    #     'user': 'hive',
    #     'password': 'hive@devtest'
    # }

    # hive, 有密码, 有kerberos
    # opts = {
    #     'host': '172.16.163.216',
    #     'port': 10000,
    #     'auth_mechanism': 'PLAIN',
    #     'user': 'hive',
    #     'password': 'hive@devtest'
    # }
    client = ImpalaLink(opts)
    result = client.query('show databases')
    print(result)
