# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from configs import log, api
from server.decorators import Response
from server.request import get_arg, get_payload
from operations.params_index import ParamsIndexOperation
from filters.params_index import ParamsIndexFilter
from document.params_index import *
from verify.params_index import ParamsIndexVerify
from verify.permission import PermissionVerify


class ParamsIndexList(Resource):
    @staticmethod
    @ParamsIndexFilter.filter_list_data(menu_list=list)
    @ParamsIndexOperation.get_params_index_list()
    def get():
        """获取参数目录数据结构"""
        return Response()


class ParamsIndexAdd(Resource):
    @staticmethod
    @params_index_add_request
    @ParamsIndexFilter.filter_add_data(index_id=int)
    @ParamsIndexOperation.add_params_index(parent_id=int, index_name=str, index_desc=str, index_mark=int, user_id=int)
    @ParamsIndexVerify.verify_add_param_index(parent_id=int, index_name=str, index_desc=str, index_mark=int,
                                              user_id=int)
    @PermissionVerify.verify_write_permission(parent_id=int, index_name=str, index_desc=str, index_mark=int)
    def post():
        """新增参数菜单"""
        payload = get_payload()
        params = Response(
            parent_id=int(payload.get('parent_id', 0)),
            index_name=payload.get('index_name', ''),
            index_desc=payload.get('index_desc', ''),
            index_mark=int(payload.get('index_mark', 0))
        )
        log.info('新增参数菜单[params: %s]' % str(params))
        return params


class ParamsIndexDetail(Resource):
    @staticmethod
    @ParamsIndexFilter.filter_update_data(index_id=int)
    @ParamsIndexOperation.update_params_index(index_id=int, index_name=str, user_id=int)
    @ParamsIndexVerify.verify_update_param_index(index_id=int, index_name=str, user_id=int)
    @PermissionVerify.verify_write_permission(index_id=int, index_name=str)
    def put(index_id):
        """修改参数菜单"""
        payload = get_payload()
        params = Response(
            index_id=index_id,
            index_name=payload.get('index_name', '')
        )
        log.info('修改参数菜单[params: %s]' % str(params))
        return params

    @staticmethod
    @ParamsIndexFilter.filter_delete_data(index_id=int)
    @ParamsIndexOperation.delete_params_index(index_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(index_id=int)
    def delete(index_id):
        """删除参数菜单"""
        return Response(index_id=index_id)


ns = api.namespace('params_index', description='参数目录')
ns.add_resource(ParamsIndexList, '/list/api/')
ns.add_resource(ParamsIndexAdd, '/add/api/')
ns.add_resource(ParamsIndexDetail, '/detail/api/<int:index_id>/')
