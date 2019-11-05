# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from document.interface import *
from filters.interface import InterfaceFilter
from operations.interface import InterfaceOperation
from verify.interface import InterfaceVerify
from verify.permission import PermissionVerify


class InterfaceList(Resource):
    @staticmethod
    @interface_list_request
    @interface_list_response_success
    @InterfaceFilter.filter_list_data(result=list, total=int)
    @InterfaceOperation.get_interface_list(interface_name=str, start_time=int, end_time=int, interface_type=int,
                                           is_deleted=int, page=int, limit=int)
    @InterfaceVerify.verify_get_interface_list(interface_name=str, start_time=int, end_time=int, interface_type=int,
                                               is_deleted=int, page=int, limit=int)
    def get():
        """获取工作流列表"""
        params = Response(
            interface_name=get_arg('interface_name', ''),
            start_time=int(get_arg('start_time', 0)),
            end_time=int(get_arg('end_time', 0)),
            interface_type=int(get_arg('interface_type', 0)),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取工作流列表[params: %s]' % str(params))
        return params


class InterfaceGraph(Resource):
    @staticmethod
    @InterfaceFilter.filter_interface_graph_data(job_nodes=list)
    @InterfaceOperation.get_interface_graph(interface_id=int)
    @InterfaceVerify.verify_get_interface_graph(interface_id=int)
    def get(interface_id):
        """获取工作流拓扑结构"""
        params = Response(interface_id=interface_id)
        log.info('获取工作流拓扑结构[params: %s]' % str(params))
        return params


class InterfaceDetail(Resource):
    @staticmethod
    @InterfaceFilter.filter_interface_detail_data(detail=dict)
    @InterfaceOperation.get_interface_detail(interface_id=int)
    @InterfaceVerify.verify_get_interface_detail(interface_id=int)
    def get(interface_id):
        """获取工作流详情"""
        params = Response(interface_id=interface_id)
        log.info('获取工作流详情[params: %s]' % str(params))
        return params

    @staticmethod
    @interface_update_request
    @InterfaceFilter.filter_update_interface_detail(interface_id=int)
    @InterfaceOperation.update_interface_detail(interface_id=int, interface_name=str, interface_desc=str, retry=int,
                                                user_id=int, is_deleted=int)
    @InterfaceVerify.verify_update_interface_detail(interface_id=int, interface_name=str, interface_desc=str, retry=int,
                                                    user_id=int, is_deleted=int)
    @PermissionVerify.verify_write_permission(interface_id=int, interface_name=str, interface_desc=str, retry=int,
                                              is_deleted=int)
    def put(interface_id):
        """修改工作流详情"""
        payload = get_payload()
        params = Response(
            interface_id=interface_id,
            interface_name=payload.get('interface_name', ''),
            interface_desc=payload.get('interface_desc', ''),
            retry=int(payload.get('retry', 0)),
            is_deleted=int(payload.get('is_deleted', 0))
        )
        log.info('修改工作流详情[params: %s]' % str(params))
        return params

    @staticmethod
    @InterfaceFilter.filter_delete_interface(interface_id=int)
    @InterfaceOperation.delete_interface(interface_id=int, user_id=int)
    @InterfaceVerify.verify_delete_interface(interface_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(interface_id=int)
    def delete(interface_id):
        """删除工作流"""
        params = Response(interface_id=interface_id)
        log.info('删除工作流[params: %s]' % str(params))
        return params


class InterfaceAdd(Resource):
    @staticmethod
    @interface_add_request
    @InterfaceFilter.filter_add_interface(interface_id=int)
    @InterfaceOperation.add_interface(interface_name=str, interface_desc=str, retry=int, user_id=int)
    @InterfaceVerify.verify_add_interface(interface_name=str, interface_desc=str, retry=int, user_id=int)
    @PermissionVerify.verify_write_permission(interface_name=str, interface_desc=str, retry=int)
    def post():
        """新增工作流"""
        payload = get_payload()
        params = Response(
            interface_name=payload.get('interface_name', ''),
            interface_desc=payload.get('interface_desc', ''),
            retry=int(payload.get('retry', 0))
        )
        log.info('新增工作流[params: %s]' % str(params))
        return params


class InterfaceIDList(Resource):
    @staticmethod
    @InterfaceFilter.filter_get_interface_id_list(result=list)
    @InterfaceOperation.get_interface_id_list()
    def get():
        """获取工作流id列表"""
        params = Response()
        log.info('获取工作流id列表')
        return params


ns = api.namespace('interface', description='工作流')
ns.add_resource(InterfaceList, '/list/api/')
ns.add_resource(InterfaceGraph, '/graph/api/<int:interface_id>/')
ns.add_resource(InterfaceDetail, '/detail/api/<int:interface_id>/')
ns.add_resource(InterfaceAdd, '/add/api/')
ns.add_resource(InterfaceIDList, '/id/list/api/')
