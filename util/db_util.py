# !/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

from configs import log
from conn.mysql import MysqlConn
# from conn.mongo import MongoLinks
from conn.mssql import MssqlConn
from conn.impala import ImpalaLink


def get_db_data_one(source_type, source_host, source_port, source_user, source_password, source_database, auth_type,
                    param_value):
    """
    连接数据源获取数据
    :param source_type: 数据库类型: 1.mysql, 2.mongo, 3.mssql, 4.hive, 5.impala
    :param source_host: 数据库ip或域名
    :param source_port: 数据库端口
    :param source_user: 用户名
    :param source_password: 密码
    :param source_database: 数据库库名
    :param auth_type: 认证方式(仅hive和impala使用):0.无,1.NOSASL,2.PLAIN,3.GSSAPI,4.LDAP
    :param param_value: SQL查询
    """
    # 用户名
    if not source_user:
        source_user = None
    # 密码
    if not source_password:
        source_password = None
    # 数据库库名
    if not source_database:
        source_database = None
    try:
        # mysql
        if source_type == 1:
            cursor = MysqlConn(source_host, source_port, source_user, source_password, source_database)
            result = cursor.query_one(param_value)
        # mongo
        # elif source_type == 2:
        #     MongoLinks(source_host, source_port, source_database, source_user, source_password)
        # mssql
        elif source_type == 3:
            cursor = MssqlConn(source_host, source_port, source_user, source_password, source_database)
            result = cursor.query_one(param_value)
            result = str(result.values()[0]) if result else ''
        # hive / impala
        else:
            cursor = ImpalaLink(source_host, source_port, source_user, source_password, source_database, auth_type)
            result = cursor.query_one(param_value)
        if isinstance(result, tuple):
            result = str(result[0])
        elif isinstance(result, dict):
            result = str([i for i in result.values()][0] if result.values() else '')
        else:
            result = ''
        return {'result': result, 'msg': '成功', 'flag': 0}
    except Exception as e:
        log.error('测试数据源连接异常: [error: %s]' % e, exc_info=1)
        return {'result': '', 'msg': traceback.format_exc(), 'flag': 1}


def test_db_conn(source_type, auth_type, source_host, source_port, source_database, source_user, source_password):
    """
    测试数据源连接
    :param source_type: 数据库类型: 1.mysql, 2.mongo, 3.mssql, 4.hive, 5.impala
    :param auth_type: 认证方式(仅hive和impala使用):0.无,1.NOSASL,2.PLAIN,3.GSSAPI,4.LDAP
    :param source_host: 数据库ip或域名
    :param source_port: 数据库端口
    :param source_database: 数据库库名
    :param source_user: 用户名
    :param source_password: 密码
    :return: BOOLEAN
    """
    # 用户名
    if not source_user:
        source_user = None
    # 密码
    if not source_password:
        source_password = None
    # 数据库库名
    if not source_database:
        source_database = None
    try:
        # mysql
        if source_type == 1:
            MysqlConn(source_host, source_port, source_user, source_password, source_database)
        # mongo
        # elif source_type == 2:
        #     MongoLinks(source_host, source_port, source_database, source_user, source_password)
        # mssql
        elif source_type == 3:
            MssqlConn(source_host, source_port, source_user, source_password, source_database)
        # hive / impala
        else:
            ImpalaLink(source_host, source_port, source_user, source_password, source_database, auth_type)
        return {'tag': True, 'msg': '成功'}
    except Exception as e:
        log.error('测试数据源连接异常: [error: %s]' % e, exc_info=1)
        return {'tag': False, 'msg': traceback.format_exc()}
