# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort
from server.status import make_result
from server.decorators import make_decorator, Response
from configs import db, log
from models.datasource import DataSourceModel
from models.params import ParamsModel
from util.db_util import test_db_conn


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
    def test_datasource_link(source_id):
        """测试数据源连接"""
        detail = DataSourceModel.get_datasource_detail(db.etl_db, source_id)

        data = test_db_conn(detail['source_type'], detail['auth_type'], detail['source_host'], detail['source_port'],
                            detail['source_database'], detail['source_user'], detail['source_password'])
        if data['tag']:
            DataSourceModel.update_datasource_status(db.etl_db, source_id, 0)
        else:
            DataSourceModel.update_datasource_status(db.etl_db, source_id, 1)
        return Response(tag=data['tag'], msg=data['msg'])

    @staticmethod
    @make_decorator
    def add_datasource_detail(source_name, source_type, auth_type, source_host, source_port,
                              source_database, source_user, source_password, source_desc, user_id):
        """新增数据源"""
        source_id = DataSourceModel.add_datasource_detail(db.etl_db, source_name, source_type, auth_type,
                                                          source_host, source_port, source_database, source_user,
                                                          source_password, source_desc, user_id)
        return Response(source_id=source_id)

    @staticmethod
    @make_decorator
    def delete_datasource_detail(source_id, user_id):
        """删除数据源"""
        prep_count = ParamsModel.get_param_by_source_id(db.etl_db, source_id)
        if prep_count:
            abort(400, **make_result(status=400, msg='数据源在任务参数表中存在%s个依赖, 不可删除' % prep_count))
        DataSourceModel.delete_datasource_detail(db.etl_db, source_id, user_id)
        return Response(source_id=source_id)

    @staticmethod
    @make_decorator
    def get_datasource_detail(source_id):
        """获取数据源详情"""
        result = DataSourceModel.get_datasource_detail(db.etl_db, source_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_datasource_detail(source_id, source_name, source_type, auth_type, source_host, source_port,
                                 source_database, source_user, source_password, source_desc, is_deleted, user_id):
        """修改数据源"""
        if is_deleted == 1:
            prep_count = ParamsModel.get_param_by_source_id(db.etl_db, source_id)
            if prep_count:
                abort(400, **make_result(status=400, msg='数据源在任务参数表中存在%s个依赖, 不可设置失效' % prep_count))
        DataSourceModel.update_datasource_detail(db.etl_db, source_id, source_name, source_type, auth_type, source_host,
                                                 source_port, source_database, source_user, source_password,
                                                 source_desc, user_id, is_deleted)
        return Response(source_id=source_id)

    @staticmethod
    @make_decorator
    def get_datasource_list_all():
        """获取所有数据源"""
        result = DataSourceModel.get_datasource_list_all(db.etl_db)
        return Response(result=result)
