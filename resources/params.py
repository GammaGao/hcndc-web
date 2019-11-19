# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from verify.params import ParamsVerify
from verify.permission import PermissionVerify
from operations.params import ParamsOperation
from filters.params import ParamsFilter
from document.params import *


class ParamsList(Resource):
    @staticmethod
    @params_list_request
    @ParamsFilter.filter_list_data(result=list, total=int)
    @ParamsOperation.get_params_list(param_type=int, param_name=str, param_index=list, source_id=int, is_deleted=int,
                                     page=int, limit=int)
    @ParamsVerify.verify_get_params_list(param_type=int, param_name=str, param_index=str, source_id=int, is_deleted=int,
                                         page=int, limit=int)
    def get():
        """获取参数列表"""
        params = Response(
            param_type=int(get_arg('param_type', 0)),
            param_name=get_arg('param_name', ''),
            param_index=get_arg('param_index', ''),
            source_id=int(get_arg('source_id', 0)),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取参数列表[params: %s]' % str(params))
        return params


class ParamsAdd(Resource):
    @staticmethod
    @params_add_request
    @ParamsFilter.filter_add_data(param_id=int)
    @ParamsOperation.add_params_detail(param_type=int, param_name=str, param_index=str, source_id=int, param_value=str,
                                       param_desc=str, param_mark=int, user_id=int)
    @ParamsVerify.verify_add_param(param_type=int, param_name=str, param_index=str, source_id=int, param_value=str,
                                   param_desc=str, param_mark=int, user_id=int)
    @PermissionVerify.verify_write_permission(param_type=int, param_name=str, param_index=str, source_id=int,
                                              param_value=str, param_desc=str, param_mark=int)
    def post():
        """新增参数"""
        payload = get_payload()
        params = Response(
            param_type=int(payload.get('param_type', 0)),
            param_name=payload.get('param_name', ''),
            param_index=payload.get('param_index', ''),
            source_id=int(payload.get('source_id', 0)),
            param_value=payload.get('param_value', ''),
            param_desc=payload.get('param_desc', ''),
            param_mark=int(payload.get('param_mark', 0))
        )
        log.info('新增参数[params: %s]' % str(params))
        return params


class ParamsDetail(Resource):
    @staticmethod
    @ParamsFilter.filter_detail_data(result=dict)
    @ParamsOperation.get_params_detail(param_id=int)
    def get(param_id):
        """获取参数"""
        params = Response(param_id=param_id)
        log.info('获取参数[params: %s]' % str(params))
        return params

    @staticmethod
    @params_update_request
    @ParamsFilter.filter_update_data(param_id=int)
    @ParamsOperation.update_params_detail(param_id=int, param_type=int, param_name=str, param_index=str, source_id=int,
                                          param_value=str, param_desc=str, param_mark=int, is_deleted=int, user_id=int)
    @ParamsVerify.verify_update_param(param_id=int, param_type=int, param_name=str, param_index=str, source_id=int,
                                      param_value=str, param_desc=str, param_mark=int, is_deleted=int, user_id=int)
    @PermissionVerify.verify_write_permission(param_id=int, param_type=int, param_name=str, param_index=str,
                                              source_id=int, param_value=str, param_desc=str, param_mark=int,
                                              is_deleted=int)
    def put(param_id):
        """修改参数"""
        payload = get_payload()
        params = Response(
            param_id=param_id,
            param_type=int(payload.get('param_type', 0)),
            param_name=payload.get('param_name', ''),
            param_index=payload.get('param_index', ''),
            source_id=int(payload.get('source_id', 0)),
            param_value=payload.get('param_value', ''),
            param_desc=payload.get('param_desc', ''),
            param_mark=int(payload.get('param_mark', 0)),
            is_deleted=int(payload.get('is_deleted', 0))
        )
        log.info('修改参数[params: %s]' % str(params))
        return params

    @staticmethod
    @ParamsFilter.filter_delete_data(param_id=int)
    @ParamsOperation.delete_params_detail(param_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(param_id=int)
    def delete(param_id):
        """删除参数"""
        params = Response(param_id=param_id)
        log.info('删除参数[params: %s]' % str(params))
        return params


class ParamsTest(Resource):
    @staticmethod
    @params_test_request
    @ParamsFilter.filter_test_data(result=str, msg=str, flag=int)
    @ParamsOperation.test_params_detail(source_id=int, param_value=str)
    @ParamsVerify.verify_test_param(source_id=int, param_value=str)
    def post():
        """测试SQL参数"""
        payload = get_payload()
        params = Response(
            source_id=int(payload.get('source_id', 0)),
            param_value=payload.get('param_value', '')
        )
        log.info('SQL参数测试[params: %s]' % params)
        return params


class ParamsListAll(Resource):
    @staticmethod
    @ParamsFilter.filter_all_list_data(result=list)
    @ParamsOperation.get_params_list_all()
    def get():
        """获取所有参数"""
        params = Response()
        log.info('获取所有参数')
        return params


class ParamsIndex(Resource):
    @staticmethod
    @ParamsFilter.filter_all_index_data(result=list)
    @ParamsOperation.get_params_index_all()
    def get():
        """获取所有参数目录"""
        params = Response()
        log.info('获取所有参数目录')
        return params


class ParamsAction(Resource):
    @staticmethod
    @ParamsFilter.filter_delete_params_may(msg=str)
    @ParamsOperation.delete_params_may(param_id_arr=list, user_id=int)
    @ParamsVerify.verify_delete_many_params(param_id_arr=list, user_id=int)
    @PermissionVerify.verify_execute_permission(param_id_arr=list)
    def delete():
        """批量删除参数"""
        payload = get_payload()
        params = Response(
            param_id_arr=payload.get('param_id_arr', [])
        )
        log.info('批量删除任务流[params: %s]' % str(params))
        return params


ns = api.namespace('params', description='参数')
ns.add_resource(ParamsList, '/list/api/')
ns.add_resource(ParamsAdd, '/add/api/')
ns.add_resource(ParamsDetail, '/detail/api/<int:param_id>/')
ns.add_resource(ParamsAction, '/action/api/')
ns.add_resource(ParamsTest, '/test/api/')
ns.add_resource(ParamsListAll, '/list/all/api/')
ns.add_resource(ParamsIndex, '/index/api/')
