# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from filters.base import ExecFilter, AlertFilter
from operations.base import ExecHostOperation, AlertOperation
from verify.base import ExecHostVerify, AlertVerify
from verify.permission import PermissionVerify
from document.base import *


class ExecHostList(Resource):
    @staticmethod
    @exec_host_request
    @ExecFilter.filter_exec_host_list_data(result=list, total=int)
    @ExecHostOperation.get_exec_host_list(server_name=str, server_host=str, is_deleted=int, page=int, limit=int)
    @ExecHostVerify.verify_get_exec_host_list(server_name=str, server_host=str, is_deleted=int, page=int, limit=int)
    def get():
        """获取执行服务器列表"""
        params = Response(
            server_name=get_arg('server_name', ''),
            server_host=get_arg('server_host', ''),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取执行服务器列表[params: %s]' % str(params))
        return params


class ExecHostDetail(Resource):
    @staticmethod
    @ExecFilter.filter_exec_host_detail_data(result=dict)
    @ExecHostOperation.get_exec_host_detail(server_id=int)
    @ExecHostVerify.verify_get_exec_host_detail(server_id=int)
    def get(server_id):
        """获取执行服务器详情"""
        params = Response(server_id=server_id)
        log.info('获取执行服务器详情[params: %s]' % str(params))
        return params

    @staticmethod
    @exec_host_update_request
    @ExecFilter.filter_exec_host_update(server_id=int)
    @ExecHostOperation.update_exec_host_detail(server_id=int, server_host=str, server_name=str, is_deleted=int,
                                               user_id=int)
    @ExecHostVerify.verify_update_exec_host_detail(server_id=int, server_host=str, server_name=str, is_deleted=int,
                                                   user_id=int)
    @PermissionVerify.verify_write_permission(server_id=int, server_host=str, server_name=str, is_deleted=int)
    def put(server_id):
        """修改执行服务器详情"""
        payload = get_payload()
        params = Response(
            server_id=server_id,
            server_host=payload.get('server_host', ''),
            server_name=payload.get('server_name', ''),
            is_deleted=int(payload.get('is_deleted', 0))
        )
        log.info('修改执行服务器详情[params: %s]' % str(params))
        return params

    @staticmethod
    @ExecFilter.filter_exec_host_delete(server_id=int)
    @ExecHostOperation.delete_exec_host_detail(server_id=int, user_id=int)
    @ExecHostVerify.verify_delete_exec_host_detail(server_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(server_id=int)
    def delete(server_id):
        """删除执行服务器详情"""
        params = Response(server_id=server_id)
        log.info('删除执行服务器详情[params: %s]' % str(params))
        return params


class ExecHostAdd(Resource):
    @staticmethod
    @ExecFilter.filter_exec_host_add(host_id=int)
    @ExecHostOperation.add_exec_host(server_host=str, server_name=str, user_id=int)
    @ExecHostVerify.verify_add_exec_host(server_host=str, server_name=str, user_id=int)
    @PermissionVerify.verify_write_permission(server_host=str, server_name=str)
    def post():
        """新增执行服务器"""
        payload = get_payload()
        params = Response(
            server_host=payload.get('server_host', ''),
            server_name=payload.get('server_name', '')
        )
        log.info('新增执行服务器[params: %s]' % str(params))
        return params


class AlertList(Resource):
    @staticmethod
    @alert_conf_list_request
    @alert_conf_list_response_success
    @AlertFilter.filter_list_data(result=list, total=int)
    @AlertOperation.get_alert_list(alert_channel=int, conf_name=str, is_deleted=int, page=int, limit=int)
    @AlertVerify.verify_get_alert_conf_list(alert_channel=int, conf_name=str, is_deleted=int, page=int, limit=int)
    def get():
        """获取预警配置列表"""
        params = Response(
            alert_channel=int(get_arg('alert_channel', 0)),
            conf_name=get_arg('conf_name', ''),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取预警配置列表[params: %s]' % str(params))
        return params


class AlertListAll(Resource):
    @staticmethod
    @AlertFilter.filter_list_all_data(result=list)
    @AlertOperation.get_alert_list_all()
    def get():
        """获取预警配置列表(全)"""
        params = Response()
        log.info('获取预警配置列表(全)[params: %s]' % str(params))
        return params


class AlertDetail(Resource):
    @staticmethod
    @AlertFilter.filter_delete_data(conf_id=int)
    @AlertOperation.delete_alert_detail(conf_id=int, user_id=int)
    @AlertVerify.verify_delete_alert_conf(conf_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(conf_id=int)
    def delete(conf_id):
        """删除预警配置"""
        params = Response(conf_id=conf_id)
        log.info('删除预警配置[params: %s]' % str(params))
        return params

    @staticmethod
    @alert_conf_detail_response_success
    @AlertFilter.filter_get_detail_data(result=dict)
    @AlertOperation.get_alert_detail_detail(conf_id=int)
    @AlertVerify.verify_get_alert_conf_detail(conf_id=int)
    def get(conf_id):
        """获取预警配置详情"""
        params = Response(conf_id=conf_id)
        log.info('获取预警配置详情[params: %s]' % str(params))
        return params

    @staticmethod
    @alert_conf_detail_update_request
    @AlertFilter.filter_update_detail_data(conf_id=int)
    @AlertOperation.update_alert_detail(conf_id=int, alert_channel=int, conf_name=str, param_config=str,
                                        param_host=str, param_port=int, param_pass=str, is_deleted=int, user_id=int)
    @AlertVerify.verify_update_alert_conf_detail(conf_id=int, alert_channel=int, conf_name=str, param_config=str,
                                                 param_host=str, param_port=int, param_pass=str, is_deleted=int,
                                                 user_id=int)
    @PermissionVerify.verify_write_permission(conf_id=int, alert_channel=int, conf_name=str, param_config=str,
                                              param_host=str, param_port=int, param_pass=str, is_deleted=int)
    def put(conf_id):
        """修改预警配置详情"""
        payload = get_payload()
        params = Response(
            conf_id=conf_id,
            alert_channel=int(payload.get('alert_channel', 0)),
            conf_name=payload.get('conf_name', ''),
            param_config=payload.get('param_config', ''),
            param_host=payload.get('param_host', ''),
            param_port=int(payload.get('param_port', 0)),
            param_pass=payload.get('param_pass', ''),
            is_deleted=int(payload.get('is_deleted', 0))
        )
        log.info('修改预警配置详情[params: %s]' % str(params))
        return params


class AlertAdd(Resource):
    @staticmethod
    @alert_conf_detail_add_request
    @AlertFilter.filter_add_detail_data(conf_id=int)
    @AlertOperation.add_alert_detail(alert_channel=int, conf_name=str, param_config=str, param_host=str,
                                     param_pass=str, param_port=int, user_id=int)
    @AlertVerify.verify_add_alert_conf(alert_channel=int, conf_name=str, param_config=str, param_host=str,
                                       param_pass=str, param_port=int, user_id=int)
    @PermissionVerify.verify_write_permission(alert_channel=int, conf_name=str, param_config=str, param_host=str,
                                              param_port=int, param_pass=str)
    def post():
        """新增预警配置"""
        payload = get_payload()
        params = Response(
            alert_channel=int(payload.get('alert_channel', 0)),
            conf_name=payload.get('conf_name', ''),
            param_config=payload.get('param_config', ''),
            param_host=payload.get('param_host', ''),
            param_port=int(payload.get('param_port', 0)),
            param_pass=payload.get('param_pass', '')
        )
        log.info('修改预警配置详情[params: %s]' % str(params))
        return params


ns = api.namespace('base', description='配置')
ns.add_resource(ExecHostList, '/exec/host/list/api/')
ns.add_resource(ExecHostDetail, '/exec/host/detail/api/<int:server_id>/')
ns.add_resource(ExecHostAdd, '/exec/host/add/api/')
ns.add_resource(AlertList, '/alert/list/api/')
ns.add_resource(AlertListAll, '/alert/list/all/api/')
ns.add_resource(AlertDetail, '/alert/detail/api/<int:conf_id>/')
ns.add_resource(AlertAdd, '/alert/add/api/')
