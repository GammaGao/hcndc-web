# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import traceback

from server.decorators import make_decorator, Response
from configs import db, log
from models.datasource import DataSourceModel
from conn.mysql import MysqlConn
from conn.mongo import MongoLinks
from conn.mssql import MssqlConn
from conn.impala import ImpalaLink


class DataSourceOperation(object):
    @staticmethod
    @make_decorator
    def get_datasource_list(source_name, source_type, source_host, is_deleted, page, limit):
        """获取数据源列表"""
        condition = []
        if source_name:
            condition.append('source_name LIKE "%%%%%s%%%%"' % source_name)
        if source_host:
            condition.append('source_host LIKE "%%%%%s%%%%"' % source_host)
        if source_type:
            condition.append('source_type = %s' % source_type)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = DataSourceModel.get_datasource_list(db.etl_db, condition, page, limit)
        total = DataSourceModel.get_datasource_list_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def test_datasource_link(source_type, auth_type, collection_name, source_host, source_port, source_database,
                             source_user, source_password, check_sql):
        """测试数据源连接"""
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
                cursor.query_one(check_sql)
            # mongo
            elif source_type == 2:
                cursor = MongoLinks(source_host, source_port, source_database, collection_name, source_user,
                                    source_password)
                cursor.collection.find(json.loads(check_sql.replace("'", '"')))
            # mssql
            elif source_type == 3:
                cursor = MssqlConn(source_host, source_port, source_user, source_password, source_database)
                cursor.query_one(check_sql)
            # hive / impala
            else:
                cursor = ImpalaLink(source_host, source_port, source_user, source_password, source_database, auth_type)
                cursor.query_one(check_sql)
            return Response(tag=True, msg='成功')
        except Exception as e:
            log.error('测试数据源连接异常: [error: %s]' % e, exc_info=1)
            return Response(tag=False, msg=traceback.format_exc())

    @staticmethod
    @make_decorator
    def add_datasource_detail(source_name, source_type, auth_type, collection_name, source_host, source_port,
                              source_database, source_user, source_password, check_sql, source_desc, user_id):
        """新增数据源"""
        datasource_id = DataSourceModel.add_datasource_detail(db.etl_db, source_name, source_type, auth_type,
                                                              collection_name, source_host, source_port,
                                                              source_database, source_user, source_password, check_sql,
                                                              source_desc, user_id)
        return Response(datasource_id=datasource_id)
