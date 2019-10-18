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
    @ParamsOperation.get_params_list(param_type=int, param_name=str, source_id=int, is_deleted=int, page=int, limit=int)
    @ParamsVerify.verify_get_params_list(param_type=int, param_name=str, source_id=int, is_deleted=int, page=int,
                                         limit=int)
    def get():
        """获取参数列表"""
        params = Response(
            param_type=int(get_arg('param_type', 0)),
            param_name=get_arg('param_name', ''),
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
    @ParamsOperation.add_params_detail(param_type=int, param_name=str, source_id=int, param_value=str, param_desc=str,
                                       user_id=int)
    @ParamsVerify.verify_add_param(param_type=int, param_name=str, source_id=int, param_value=str, param_desc=str,
                                   user_id=int)
    @PermissionVerify.verify_write_permission(param_type=int, param_name=str, source_id=int, param_value=str,
                                              param_desc=str)
    def post():
        """新增参数"""
        payload = get_payload()
        params = Response(
            param_type=int(payload.get('param_type', 0)),
            param_name=payload.get('param_name', ''),
            source_id=int(payload.get('source_id', 0)),
            param_value=payload.get('param_value', ''),
            param_desc=payload.get('param_desc', '')
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
    @ParamsOperation.update_params_detail(param_id=int, param_type=int, param_name=str, source_id=int, param_value=str,
                                          param_desc=str, is_deleted=int, user_id=int)
    @ParamsVerify.verify_update_param(param_id=int, param_type=int, param_name=str, source_id=int, param_value=str,
                                      param_desc=str, is_deleted=int, user_id=int)
    @PermissionVerify.verify_write_permission(param_id=int, param_type=int, param_name=str, source_id=int,
                                              param_value=str, param_desc=str, is_deleted=int)
    def put(param_id):
        """修改参数"""
        payload = get_payload()
        params = Response(
            param_id=param_id,
            param_type=int(payload.get('param_type', 0)),
            param_name=payload.get('param_name', ''),
            source_id=int(payload.get('source_id', 0)),
            param_value=payload.get('param_value', ''),
            param_desc=payload.get('param_desc', ''),
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


ns = api.namespace('params', description='参数')
ns.add_resource(ParamsList, '/list/api/')
ns.add_resource(ParamsAdd, '/add/api/')
ns.add_resource(ParamsDetail, '/detail/api/<int:param_id>/')
