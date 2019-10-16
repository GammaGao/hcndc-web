# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from server.decorators import Response
from configs import log
from server.request import get_arg, get_payload
from document.datasource import *
from operations.datasource import DataSourceOperation
from verify.datasource import DataSourceVerify
from verify.permission import PermissionVerify
from filters.datasource import DataSourceFilter


class DataSourceList(Resource):
    @staticmethod
    @datasource_list_request
    @DataSourceFilter.filter_list_data(result=list, total=int)
    @DataSourceOperation.get_datasource_list(source_name=str, source_type=int, source_host=str, is_deleted=int,
                                             page=int, limit=int)
    @DataSourceVerify.verify_get_datasource_list(source_name=str, source_type=int, source_host=str, is_deleted=int,
                                                 page=int, limit=int)
    def get():
        """获取数据源列表"""
        params = Response(
            source_name=get_arg('source_name', ''),
            source_type=int(get_arg('source_type', 0)),
            source_host=get_arg('source_host', ''),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取数据源列表[params: %s]' % str(params))
        return params


class DataSourceTest(Resource):
    @staticmethod
    @datasource_test_request
    @DataSourceFilter.filter_test_data(tag=bool, msg=str)
    @DataSourceOperation.test_datasource_link(source_type=int, auth_type=str, source_host=str, source_port=int,
                                              source_database=str, source_user=str, source_password=str)
    @DataSourceVerify.verify_test_datasource_link(source_type=int, auth_type=int, source_host=str, source_port=int,
                                                  source_database=str, source_user=str, source_password=str)
    def post():
        """测试数据源连接"""
        payload = get_payload()
        params = Response(
            source_type=int(payload.get('source_type', 0)),
            auth_type=int(payload.get('auth_type', 0)),
            source_host=payload.get('source_host', ''),
            source_port=int(payload.get('source_port', 0)),
            source_database=payload.get('source_database', ''),
            source_user=payload.get('source_user', ''),
            source_password=payload.get('source_password', '')
        )
        log.info('测试数据源连接[params: %s]' % str(params))
        return params


class DataSourceAdd(Resource):
    @staticmethod
    @datasource_add_detail_request
    @DataSourceFilter.filter_add_data(source_id=int)
    @DataSourceOperation.add_datasource_detail(source_name=str, source_type=int, auth_type=int, source_host=str,
                                               source_port=int, source_database=str, source_user=str,
                                               source_password=str, source_desc=str, user_id=int)
    @DataSourceVerify.verify_add_datasource_detail(source_name=str, source_type=int, auth_type=int, source_host=str,
                                                   source_port=int, source_database=str, source_user=str,
                                                   source_password=str, source_desc=str, user_id=int)
    @PermissionVerify.verify_write_permission(source_name=str, source_type=int, auth_type=int, source_host=str,
                                              source_port=int, source_database=str, source_user=str,
                                              source_password=str, source_desc=str)
    def post():
        """新增数据源"""
        payload = get_payload()
        params = Response(
            source_name=payload.get('source_name', ''),
            source_type=int(payload.get('source_type', 0)),
            auth_type=int(payload.get('auth_type', 0)),
            source_host=payload.get('source_host', ''),
            source_port=int(payload.get('source_port', 0)),
            source_database=payload.get('source_database', ''),
            source_user=payload.get('source_user', ''),
            source_password=payload.get('source_password', ''),
            source_desc=payload.get('source_desc', '')
        )
        log.info('新增数据源[params: %s]' % str(params))
        return params


class DataSourceDetail(Resource):
    @staticmethod
    @DataSourceFilter.filter_delete_data(source_id=int)
    @DataSourceOperation.delete_datasource_detail(source_id=int, user_id=int)
    @DataSourceVerify.verify_delete_datasource(source_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(source_id=int)
    def delete(source_id):
        """删除数据源"""
        params = Response(source_id=source_id)
        log.info('删除数据源[params: %s]' % str(params))
        return params

    @staticmethod
    @DataSourceFilter.filter_get_detail_data(result=dict)
    @DataSourceOperation.get_datasource_detail(source_id=int)
    @DataSourceVerify.verify_get_datasource_detail(source_id=int)
    def get(source_id):
        """获取数据源详情"""
        params = Response(source_id=source_id)
        log.info('获取数据源详情[params: %s]' % str(params))
        return params

    @staticmethod
    @DataSourceFilter.filter_update_data(source_id=int)
    @DataSourceOperation.update_datasource_detail(source_id=int, source_name=str, source_type=int, auth_type=int,
                                                  source_host=str, source_port=int, source_database=str,
                                                  source_user=str, source_password=str, source_desc=str,
                                                  is_deleted=int, user_id=int)
    @DataSourceVerify.verify_update_datasource_detail(source_id=int, source_name=str, source_type=int, auth_type=int,
                                                      source_host=str, source_port=int, source_database=str,
                                                      source_user=str, source_password=str, source_desc=str,
                                                      is_deleted=int, user_id=int)
    @PermissionVerify.verify_write_permission(source_id=int, source_name=str, source_type=int, auth_type=int,
                                              source_host=str, source_port=int, source_database=str,
                                              source_user=str, source_password=str, source_desc=str,
                                              is_deleted=int)
    def put(source_id):
        """修改数据源"""
        payload = get_payload()
        params = Response(
            source_id=source_id,
            source_name=payload.get('source_name', ''),
            source_type=int(payload.get('source_type', 0)),
            auth_type=int(payload.get('auth_type', 0)),
            source_host=payload.get('source_host', ''),
            source_port=int(payload.get('source_port', 0)),
            source_database=payload.get('source_database', ''),
            source_user=payload.get('source_user', ''),
            source_password=payload.get('source_password', ''),
            source_desc=payload.get('source_desc', ''),
            is_deleted=int(payload.get('is_deleted', 0))
        )
        log.info('修改数据源[params: %s]' % str(params))
        return params


ns = api.namespace('datasource', description='数据源')
ns.add_resource(DataSourceList, '/list/api/')
ns.add_resource(DataSourceTest, '/test/api/')
ns.add_resource(DataSourceAdd, '/add/api/')
ns.add_resource(DataSourceDetail, '/detail/api/<int:source_id>/')
