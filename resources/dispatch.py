# !/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_restplus.resource import Resource
from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from document.dispatch import *
from filters.dispatch import DispatchFilter, DispatchAlertFilter
from operations.dispatch import DispatchOperation, DispatchAlertOperation
from verify.dispatch import DispatchVerify, DispatchAlertVerify
from verify.permission import PermissionVerify


class CrontabSearch(Resource):
    @staticmethod
    @cron_request
    @DispatchFilter.filter_cron_data(run_times=list)
    @DispatchOperation.crontab_next_time(sched=str, query_times=int)
    def get():
        """获取调度时间"""
        params = Response(
            sched=get_arg('sched'),
            query_times=int(get_arg('queryTimes', 10))
        )
        log.info('获取调度时间[params: %s]' % str(params))
        return params


class DispatchList(Resource):
    @staticmethod
    @dispatch_list_request
    @DispatchFilter.filter_get_dispatch(result=list, total=int)
    @DispatchOperation.get_dispatch_list(interface_id=int, dispatch_name=str, status=int, page=int, limit=int)
    @DispatchVerify.verify_get_dispatch_list(interface_id=int, dispatch_name=str, status=int, page=int, limit=int)
    def get():
        """获取调度列表"""
        params = Response(
            interface_id=int(get_arg('interface_id', 0)),
            dispatch_name=get_arg('dispatch_name', ''),
            status=int(get_arg('status', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取调度列表[params: %s]' % str(params))
        return params


class DispatchDetail(Resource):
    @staticmethod
    @DispatchFilter.filter_get_dispatch_detail(result=dict)
    @DispatchOperation.get_dispatch_detail(dispatch_id=int)
    @DispatchVerify.verify_get_dispatch_detail(dispatch_id=int)
    def get(dispatch_id):
        """获取调度详情"""
        params = Response(dispatch_id=dispatch_id)
        log.info('获取调度详情[params: %s]' % str(params))
        return params

    @staticmethod
    @dispatch_update_request
    @DispatchFilter.filter_update_dispatch_detail(dispatch_id=int)
    @DispatchOperation.update_dispatch_detail(dispatch_id=int, interface_id=int, dispatch_name=str, minute=str,
                                              dispatch_desc=str, hour=str, day=str, month=str, week=str,
                                              user_id=int, old_status=int, new_status=int)
    @DispatchVerify.verify_update_dispatch_detail(dispatch_id=int, interface_id=int, dispatch_name=str, minute=str,
                                                  dispatch_desc=str, hour=str, day=str, month=str, week=str,
                                                  user_id=int, old_status=int, new_status=int)
    @PermissionVerify.verify_schedule_permission(dispatch_id=int, interface_id=int, dispatch_name=str, minute=str,
                                                 dispatch_desc=str, hour=str, day=str, month=str, week=str,
                                                 old_status=int, new_status=int)
    def put(dispatch_id):
        """修改调度详情"""
        payload = get_payload()
        params = Response(
            dispatch_id=dispatch_id,
            interface_id=int(payload.get('interface_id', '')),
            dispatch_name=payload.get('dispatch_name', ''),
            dispatch_desc=payload.get('dispatch_desc', ''),
            minute=payload.get('minute', ''),
            hour=payload.get('hour', 0),
            day=payload.get('day', ''),
            month=payload.get('month', ''),
            week=payload.get('week', ''),
            old_status=int(payload.get('old_status', 0)),
            new_status=int(payload.get('new_status', 0))
        )
        log.info('修改调度详情[params: %s]' % str(params))
        return params

    @staticmethod
    @DispatchFilter.filter_run_dispatch(dispatch_id=int)
    @DispatchOperation.run_dispatch(dispatch_id=int)
    @DispatchVerify.verify_run_dispatch(dispatch_id=int)
    @PermissionVerify.verify_execute_permission(dispatch_id=int)
    def post(dispatch_id):
        """立即执行调度任务"""
        params = Response(dispatch_id=dispatch_id)
        log.info('立即执行调度任务[params: %s]' % str(params))
        return params

    @staticmethod
    @dispatch_action_request
    @DispatchFilter.filter_action_dispatch(dispatch_id=int)
    @DispatchOperation.action_dispatch(dispatch_id=int, action=int, user_id=int)
    @DispatchVerify.verify_action_dispatch(dispatch_id=int, action=int, user_id=int)
    @PermissionVerify.verify_execute_permission(dispatch_id=int, action=int)
    def patch(dispatch_id):
        """暂停/恢复调度任务"""
        payload = get_payload()
        params = Response(
            dispatch_id=dispatch_id,
            action=int(payload.get('action', 0))
        )
        log.info('暂停/恢复调度任务[params: %s]' % str(params))
        return params

    @staticmethod
    @DispatchFilter.filter_delete_dispatch_detail(dispatch_id=int)
    @DispatchOperation.delete_dispatch_detail(dispatch_id=int, user_id=int)
    @DispatchVerify.verify_delete_dispatch_detail(dispatch_id=int, user_id=int)
    @PermissionVerify.verify_schedule_permission(dispatch_id=int)
    def delete(dispatch_id):
        """删除调度详情"""
        params = Response(dispatch_id=dispatch_id)
        log.info('删除调度详情[params: %s]' % str(params))
        return params


class DispatchAdd(Resource):
    @staticmethod
    @dispatch_add_request
    @DispatchFilter.filter_add_dispatch(dispatch_id=int)
    @DispatchOperation.add_dispatch_detail(interface_id=int, dispatch_name=str, dispatch_desc=str, minute=str,
                                           hour=str, day=str, month=str, week=str, user_id=int)
    @DispatchVerify.verify_add_dispatch(interface_id=int, dispatch_name=str, dispatch_desc=str, minute=str,
                                        hour=str, day=str, month=str, week=str, user_id=int)
    @PermissionVerify.verify_schedule_permission(interface_id=int, dispatch_name=str, dispatch_desc=str, minute=str,
                                                 hour=str, day=str, month=str, week=str)
    def post():
        """新增调度"""
        payload = get_payload()
        params = Response(
            interface_id=int(payload.get('interface_id', '')),
            dispatch_name=payload.get('dispatch_name', ''),
            dispatch_desc=payload.get('dispatch_desc', ''),
            minute=payload.get('minute', ''),
            hour=payload.get('hour', 0),
            day=payload.get('day', ''),
            month=payload.get('month', ''),
            week=payload.get('week', '')
        )
        log.info('新增调度[params: %s]' % str(params))
        return params


class DispatchAlertAdd(Resource):
    @staticmethod
    @dispatch_alert_add_request
    @DispatchAlertFilter.filter_add_dispatch_alert(dispatch_id=int)
    @DispatchAlertOperation.add_dispatch_alert(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int, conf_id_f=int,
                                               user_id=int, send_mail_s=str, send_mail_f=str)
    @DispatchAlertVerify.verify_add_dispatch_alert(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
                                                   conf_id_f=int, user_id=int, send_mail_s=str, send_mail_f=str)
    @PermissionVerify.verify_schedule_permission(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
                                                 conf_id_f=int, send_mail_s=str, send_mail_f=str)
    def post():
        """新增调度预警"""
        payload = get_payload()
        params = Response(
            dispatch_id=int(payload.get('dispatch_id', 0)),
            alert_s=int(payload.get('alert_s', 0)),
            alert_f=int(payload.get('alert_f', 0)),
            conf_id_s=int(payload.get('conf_id_s', 0)),
            conf_id_f=int(payload.get('conf_id_f', 0)),
            send_mail_s=payload.get('send_mail_s', ''),
            send_mail_f=payload.get('send_mail_f', '')
        )
        log.info('新增执行流预警[params: %s]' % str(params))
        return params


class DispatchAlertDetail(Resource):
    @staticmethod
    @DispatchAlertFilter.filter_get_dispatch_alert_detail(result=list)
    @DispatchAlertOperation.get_dispatch_alert_detail(dispatch_id=int)
    @DispatchAlertVerify.verify_get_dispatch_alert_detail(dispatch_id=int)
    def get(dispatch_id):
        """获取调度预警详情"""
        params = Response(dispatch_id=dispatch_id)
        log.info('获取调度预警详情[params: %s]' % str(params))
        return params

    @staticmethod
    @dispatch_alert_update_request
    @DispatchAlertFilter.filter_update_dispatch_alert(dispatch_id=int)
    @DispatchAlertOperation.update_dispatch_alert_detail(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
                                                         alert_id_s=int, alert_id_f=int, conf_id_f=int, user_id=int,
                                                         send_mail_s=str, send_mail_f=str)
    @DispatchAlertVerify.verify_update_dispatch_alert_detail(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
                                                             alert_id_s=int, alert_id_f=int, conf_id_f=int, user_id=int,
                                                             send_mail_s=str, send_mail_f=str)
    @PermissionVerify.verify_schedule_permission(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
                                                 alert_id_s=int, alert_id_f=int, conf_id_f=int, send_mail_s=str,
                                                 send_mail_f=str)
    def put(dispatch_id):
        """修改调度预警详情"""
        payload = get_payload()
        params = Response(
            dispatch_id=dispatch_id,
            alert_s=int(payload.get('alert_s', 0)),
            alert_f=int(payload.get('alert_f', 0)),
            alert_id_s=int(payload.get('alert_id_s', -1)),
            alert_id_f=int(payload.get('alert_id_f', -1)),
            conf_id_s=int(payload.get('conf_id_s', 0)),
            conf_id_f=int(payload.get('conf_id_f', 0)),
            send_mail_s=payload.get('send_mail_s', ''),
            send_mail_f=payload.get('send_mail_f', '')
        )
        log.info('修改调度预警详情[params: %s]' % str(params))
        return params


ns = api.namespace('dispatch', description='调度')
ns.add_resource(CrontabSearch, '/search/')
ns.add_resource(DispatchList, '/list/api/')
ns.add_resource(DispatchDetail, '/detail/api/<int:dispatch_id>/')
ns.add_resource(DispatchAdd, '/add/api/')
ns.add_resource(DispatchAlertAdd, '/alert/add/api/')
ns.add_resource(DispatchAlertDetail, '/alert/detail/api/<int:dispatch_id>/')
