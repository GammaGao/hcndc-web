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


# class FtpEventCallBack(Resource):
#     @staticmethod
#     @callback_request
#     @ExecuteFilter.filter_callback(msg=str)
#     @ExecuteOperation.get_execute_job(exec_id=int, interface_id=int, job_id=int, status=str)
#     @ExecuteVerify.verify_callback(exec_id=int, interface_id=int, job_id=int, status=str)
#     def get():
#         """执行服务任务回调"""
#         params = Response(
#             exec_id=int(get_arg('exec_id', 0)),
#             interface_id=int(get_arg('interface_id', 0)),
#             job_id=int(get_arg('job_id', 0)),
#             status=get_arg('status', '')
#         )
#         log.info('获取执行服务任务回调[params: %s]' % str(params))
#         return params

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


# class FtpEventAction(Resource):
# @staticmethod
# @ftp_event_run_request
# @DispatchFilter.filter_run_dispatch(dispatch_id=list)
# @DispatchOperation.run_dispatch(dispatch_id=list, run_date=str, date_format=str, is_after=int)
# @FtpVerify.verify_run_dispatch(dispatch_id=list, run_date=str, date_format=str, is_after=int)
# @PermissionVerify.verify_execute_permission(dispatch_id=list, run_date=str, date_format=str, is_after=int)
# def post():
#     """立即执行调度任务"""
#     payload = get_payload()
#     params = Response(
#         dispatch_id=payload.get('dispatch_id', []),
#         run_date=payload.get('run_date', ''),
#         date_format=payload.get('date_format', ''),
#         is_after=int(payload.get('is_after', 1))
#     )
#     log.info('立即执行调度任务[params: %s]' % str(params))
#     return params
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

class FtpTest(Resource):
    @staticmethod
    @ftp_event_test_request
    @FtpEventFilter.filter_test_data(status=int, msg=str)
    @FtpEventOperation.test_ftp_event_link(ftp_id=int, ftp_type=int, ftp_host=str, ftp_port=int, ftp_user=str,
                                           ftp_passwd=str, data_path=str)
    @FtpEventVerify.verify_test_ftp_event_link(ftp_id=int, ftp_type=int, ftp_host=str, ftp_port=int, ftp_user=str,
                                               ftp_passwd=str, data_path=str)
    def post():
        """测试FTP文件目录是否存在"""
        payload = get_payload()
        params = Response(
            ftp_id=int(payload.get('ftp_id', 0)),
            ftp_type=int(payload.get('ftp_type', 0)),
            ftp_host=payload.get('ftp_host', ''),
            ftp_port=int(payload.get('ftp_port', 0)),
            ftp_user=payload.get('ftp_user', ''),
            ftp_passwd=payload.get('ftp_passwd', ''),
            data_path=payload.get('data_path', '')
        )
        log.info('测试FTP文件目录是否存在[params: %s]' % str(params))
        return params


ns = api.namespace('ftp_event', description='文件事件')
ns.add_resource(FtpEventList, '/list/api/')
ns.add_resource(FtpEventDetail, '/detail/api/<int:ftp_event_id>/')
# ns.add_resource(DispatchAction, '/action/api/')
ns.add_resource(FtpEventAdd, '/add/api/')
ns.add_resource(FtpTest, '/test/api/')
# ns.add_resource(DispatchAlertAdd, '/alert/add/api/')
# ns.add_resource(DispatchAlertDetail, '/alert/detail/api/<int:dispatch_id>/')
