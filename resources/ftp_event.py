# !/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_restplus.resource import Resource
from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from document.ftp_event import *
from filters.ftp_event import FtpEventFilter
from operations.ftp_event import FtpEventOperation
from verify.ftp_event import FtpEventVerify
from verify.permission import PermissionVerify


class FtpEventList(Resource):
    @staticmethod
    @ftp_event_list_request
    @FtpEventFilter.filter_get_ftp_event(result=list, total=int)
    @FtpEventOperation.get_ftp_event_list(event_name=str, status=int, page=int, limit=int)
    @FtpEventVerify.verify_get_ftp_event_list(event_name=str, status=int, page=int, limit=int)
    def get():
        """获取文件事件列表"""
        params = Response(
            event_name=get_arg('event_name', ''),
            status=int(get_arg('status', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取文件事件列表[params: %s]' % str(params))
        return params


class FtpEventDetail(Resource):
    @staticmethod
    @FtpEventFilter.filter_get_ftp_event_detail(result=dict)
    @FtpEventOperation.get_ftp_event_detail(ftp_event_id=int)
    @FtpEventVerify.verify_get_ftp_event_detail(ftp_event_id=int)
    def get(ftp_event_id):
        """获取文件事件详情"""
        params = Response(ftp_event_id=ftp_event_id)
        log.info('获取文件事件详情[params: %s]' % str(params))
        return params

    @staticmethod
    @ftp_event_update_request
    @FtpEventFilter.filter_update_ftp_event_detail(ftp_event_id=int)
    @FtpEventOperation.update_ftp_event_detail(ftp_event_id=int, event_name=str, event_desc=str, ftp_id=int,
                                               data_path=str, file_name=str, interface_id=str, start_time=int,
                                               end_time=int, interval_value=int, date_time=str, old_status=int,
                                               new_status=int, user_id=int)
    @FtpEventVerify.verify_update_ftp_event_detail(ftp_event_id=int, event_name=str, event_desc=str, ftp_id=int,
                                                   data_path=str, file_name=str, interface_id=str, start_time=int,
                                                   end_time=int, interval_value=int, date_time=str, old_status=int,
                                                   new_status=int, user_id=int)
    @PermissionVerify.verify_schedule_permission(ftp_event_id=int, event_name=str, event_desc=str, ftp_id=int,
                                                 data_path=str, file_name=str, interface_id=str, start_time=int,
                                                 end_time=int, interval_value=int, date_time=str, old_status=int,
                                                 new_status=int)
    def put(ftp_event_id):
        """修改文件事件详情"""
        payload = get_payload()
        params = Response(
            ftp_event_id=ftp_event_id,
            event_name=payload.get('event_name', ''),
            event_desc=payload.get('event_desc', ''),
            ftp_id=int(payload.get('ftp_id', 0)),
            data_path=payload.get('data_path', ''),
            file_name=payload.get('file_name', ''),
            interface_id=payload.get('interface_id', ''),
            start_time=int(payload.get('start_time', 0)),
            end_time=int(payload.get('end_time', 24)),
            interval_value=int(payload.get('interval_value', 0)),
            date_time=payload.get('date_time', ''),
            old_status=int(payload.get('old_status', 0)),
            new_status=int(payload.get('new_status', 0))
        )
        log.info('修改文件事件详情[params: %s]' % str(params))
        return params


class FtpEventAdd(Resource):
    @staticmethod
    @ftp_event_add_request
    @FtpEventFilter.filter_add_dispatch(ftp_event_id=int)
    @FtpEventOperation.add_ftp_event_detail(event_name=str, event_desc=str, ftp_id=int, data_path=str, file_name=str,
                                            interface_id=str, start_time=int, end_time=int, interval_value=int,
                                            date_time=str, user_id=int)
    @FtpEventVerify.verify_add_ftp_event_detail(event_name=str, event_desc=str, ftp_id=int, data_path=str,
                                                file_name=str, interface_id=str, start_time=int, end_time=int,
                                                interval_value=int, date_time=str, user_id=int)
    @PermissionVerify.verify_schedule_permission(event_name=str, event_desc=str, ftp_id=int, data_path=str,
                                                 file_name=str, interface_id=str, start_time=int, end_time=int,
                                                 interval_value=int, date_time=str)
    def post():
        """新增调度"""
        payload = get_payload()
        params = Response(
            event_name=payload.get('event_name', ''),
            event_desc=payload.get('event_desc', ''),
            ftp_id=int(payload.get('ftp_id', 0)),
            data_path=payload.get('data_path', ''),
            file_name=payload.get('file_name', ''),
            interface_id=payload.get('interface_id', ''),
            start_time=int(payload.get('start_time', 0)),
            end_time=int(payload.get('end_time', 24)),
            interval_value=int(payload.get('interval_value', 0)),
            date_time=payload.get('date_time', ''),
        )
        log.info('新增调度[params: %s]' % str(params))
        return params


# class DispatchAction(Resource):
#     @staticmethod
#     @dispatch_run_request
#     @DispatchFilter.filter_run_dispatch(dispatch_id=list)
#     @DispatchOperation.run_dispatch(dispatch_id=list, run_date=str, date_format=str, is_after=int)
#     @FtpVerify.verify_run_dispatch(dispatch_id=list, run_date=str, date_format=str, is_after=int)
#     @PermissionVerify.verify_execute_permission(dispatch_id=list, run_date=str, date_format=str, is_after=int)
#     def post():
#         """立即执行调度任务"""
#         payload = get_payload()
#         params = Response(
#             dispatch_id=payload.get('dispatch_id', []),
#             run_date=payload.get('run_date', ''),
#             date_format=payload.get('date_format', ''),
#             is_after=int(payload.get('is_after', 1))
#         )
#         log.info('立即执行调度任务[params: %s]' % str(params))
#         return params
#
#     @staticmethod
#     @dispatch_action_request
#     @DispatchFilter.filter_action_dispatch(dispatch_id=list)
#     @DispatchOperation.action_dispatch(dispatch_id=list, action=int, user_id=int)
#     @FtpVerify.verify_action_dispatch(dispatch_id=list, action=int, user_id=int)
#     @PermissionVerify.verify_execute_permission(dispatch_id=list, action=int)
#     def patch():
#         """暂停/恢复调度任务"""
#         payload = get_payload()
#         params = Response(
#             dispatch_id=payload.get('dispatch_id', []),
#             action=int(payload.get('action', 0))
#         )
#         log.info('暂停/恢复调度任务[params: %s]' % str(params))
#         return params
#
#     @staticmethod
#     @dispatch_delete_request
#     @DispatchFilter.filter_delete_dispatch_detail(dispatch_id=list)
#     @DispatchOperation.delete_dispatch_detail(dispatch_id=list)
#     @FtpVerify.verify_delete_dispatch_detail(dispatch_id=list, user_id=int)
#     @PermissionVerify.verify_execute_permission(dispatch_id=list)
#     def delete():
#         """删除调度详情"""
#         payload = get_payload()
#         params = Response(dispatch_id=payload.get('dispatch_id', []))
#         log.info('删除调度详情[params: %s]' % str(params))
#         return params
#
#

#
#
# class DispatchAlertAdd(Resource):
#     @staticmethod
#     @dispatch_alert_add_request
#     @DispatchAlertFilter.filter_add_dispatch_alert(dispatch_id=int)
#     @DispatchAlertOperation.add_dispatch_alert(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int, conf_id_f=int,
#                                                user_id=int, send_mail_s=str, send_mail_f=str)
#     @FtpVerify.verify_add_dispatch_alert(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
#                                                    conf_id_f=int, user_id=int, send_mail_s=str, send_mail_f=str)
#     @PermissionVerify.verify_schedule_permission(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
#                                                  conf_id_f=int, send_mail_s=str, send_mail_f=str)
#     def post():
#         """新增调度预警"""
#         payload = get_payload()
#         params = Response(
#             dispatch_id=int(payload.get('dispatch_id', 0)),
#             alert_s=int(payload.get('alert_s', 0)),
#             alert_f=int(payload.get('alert_f', 0)),
#             conf_id_s=int(payload.get('conf_id_s', 0)),
#             conf_id_f=int(payload.get('conf_id_f', 0)),
#             send_mail_s=payload.get('send_mail_s', ''),
#             send_mail_f=payload.get('send_mail_f', '')
#         )
#         log.info('新增执行流预警[params: %s]' % str(params))
#         return params
#
#
# class DispatchAlertDetail(Resource):
#     @staticmethod
#     @DispatchAlertFilter.filter_get_dispatch_alert_detail(result=list)
#     @DispatchAlertOperation.get_dispatch_alert_detail(dispatch_id=int)
#     @FtpVerify.verify_get_dispatch_alert_detail(dispatch_id=int)
#     def get(dispatch_id):
#         """获取调度预警详情"""
#         params = Response(dispatch_id=dispatch_id)
#         log.info('获取调度预警详情[params: %s]' % str(params))
#         return params
#
#     @staticmethod
#     @dispatch_alert_update_request
#     @DispatchAlertFilter.filter_update_dispatch_alert(dispatch_id=int)
#     @DispatchAlertOperation.update_dispatch_alert_detail(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
#                                                          alert_id_s=int, alert_id_f=int, conf_id_f=int, user_id=int,
#                                                          send_mail_s=str, send_mail_f=str)
#     @FtpVerify.verify_update_dispatch_alert_detail(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
#                                                              alert_id_s=int, alert_id_f=int, conf_id_f=int, user_id=int,
#                                                              send_mail_s=str, send_mail_f=str)
#     @PermissionVerify.verify_schedule_permission(dispatch_id=int, alert_s=int, alert_f=int, conf_id_s=int,
#                                                  alert_id_s=int, alert_id_f=int, conf_id_f=int, send_mail_s=str,
#                                                  send_mail_f=str)
#     def put(dispatch_id):
#         """修改调度预警详情"""
#         payload = get_payload()
#         params = Response(
#             dispatch_id=dispatch_id,
#             alert_s=int(payload.get('alert_s', 0)),
#             alert_f=int(payload.get('alert_f', 0)),
#             alert_id_s=int(payload.get('alert_id_s', -1)),
#             alert_id_f=int(payload.get('alert_id_f', -1)),
#             conf_id_s=int(payload.get('conf_id_s', 0)),
#             conf_id_f=int(payload.get('conf_id_f', 0)),
#             send_mail_s=payload.get('send_mail_s', ''),
#             send_mail_f=payload.get('send_mail_f', '')
#         )
#         log.info('修改调度预警详情[params: %s]' % str(params))
#         return params
#
#
# class DispatchTest(Resource):
#     @staticmethod
#     @DispatchAlertOperation.test(dispatch_id=int)
#     def get(dispatch_id):
#         params = Response(dispatch_id=dispatch_id)
#         return params


ns = api.namespace('ftp_event', description='文件事件')
ns.add_resource(FtpEventList, '/list/api/')
ns.add_resource(FtpEventDetail, '/detail/api/<int:ftp_event_id>/')
# ns.add_resource(DispatchAction, '/action/api/')
ns.add_resource(FtpEventAdd, '/add/api/')
# ns.add_resource(DispatchTest, '/test/<int:dispatch_id>/')
# ns.add_resource(DispatchAlertAdd, '/alert/add/api/')
# ns.add_resource(DispatchAlertDetail, '/alert/detail/api/<int:dispatch_id>/')
