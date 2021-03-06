# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from filters.execute import ExecuteFilter
from operations.execute import ExecuteOperation
from verify.execute import ExecuteVerify
from verify.permission import PermissionVerify
from document.execute import *


class ExecuteCallBack(Resource):
    @staticmethod
    @callback_request
    @ExecuteFilter.filter_callback(msg=str)
    @ExecuteOperation.get_execute_job(exec_id=int, interface_id=int, job_id=int, status=str)
    @ExecuteVerify.verify_callback(exec_id=int, interface_id=int, job_id=int, status=str)
    def get():
        """执行服务任务回调"""
        params = Response(
            exec_id=int(get_arg('exec_id', 0)),
            interface_id=int(get_arg('interface_id', 0)),
            job_id=int(get_arg('job_id', 0)),
            status=get_arg('status', '')
        )
        log.info('获取执行服务任务回调[params: %s]' % str(params))
        return params


class ExecuteFlow(Resource):
    @staticmethod
    @execute_flow_request
    @ExecuteFilter.filter_get_execute_flow(result=list, total=int)
    @ExecuteOperation.get_execute_flow(interface_id=int, interface_index=list, run_status=int, run_date=str,
                                       page=int, limit=int)
    @ExecuteVerify.verify_get_execute_flow(interface_id=int, interface_index=str, run_status=int, run_date=str,
                                           page=int, limit=int)
    def get():
        """获取任务流最新日志"""
        params = Response(
            interface_id=int(get_arg('interface_id', 0)),
            interface_index=get_arg('interface_index', ''),
            run_status=int(get_arg('run_status', 0)),
            run_date=get_arg('run_date', ''),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取任务流最新日志[params: %s]' % str(params))
        return params


class ExecuteFlowHistory(Resource):
    @staticmethod
    @execute_history_request
    @ExecuteFilter.filter_get_execute_flow_history(result=list, total=int)
    @ExecuteOperation.get_execute_flow_history(dispatch_id=int, run_date=str, run_status=int, page=int, limit=int)
    @ExecuteVerify.verify_get_execute_flow_history(dispatch_id=int, run_date=str, run_status=int, page=int, limit=int)
    def get():
        """获取任务流调度历史日志"""
        params = Response(
            dispatch_id=int(get_arg('dispatch_id', 0)),
            run_date=get_arg('run_date', ''),
            run_status=int(get_arg('run_status', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取调度历史日志[params: %s]' % str(params))
        return params


class ExecuteInterfaceList(Resource):
    @staticmethod
    @ExecuteFilter.filter_get_execute_interface_list(result=list)
    @ExecuteOperation.get_execute_interface_list(exec_id=int)
    @ExecuteVerify.verify_get_execute_interface_list(exec_id=int)
    def get():
        """获取该执行下的任务流列表"""
        params = Response(
            exec_id=int(get_arg('exec_id', 0))
        )
        log.info('获取该执行下的任务流列表[params: %s]' % str(params))
        return params


class ExecuteJob(Resource):
    @staticmethod
    @execute_job_request
    @ExecuteFilter.filter_get_execute_job_log_list(result=list, total=int)
    @ExecuteOperation.get_execute_job_log_list(job_id=int, start_time=int, end_time=int, run_status=int,
                                               page=int, limit=int)
    @ExecuteVerify.verify_get_execute_job_log_list(job_id=int, start_time=int, end_time=int, run_status=int,
                                                   page=int, limit=int)
    def get():
        """获取手动执行任务日志"""
        params = Response(
            job_id=int(get_arg('job_id', 0)),
            start_time=int(get_arg('start_time', 0)),
            end_time=int(get_arg('end_time', 0)),
            run_status=int(get_arg('run_status', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取手动执行任务日志[params: %s]' % str(params))
        return params


class ExecuteHistoryJob(Resource):
    @staticmethod
    @execute_job_history_request
    @ExecuteFilter.filter_get_execute_job_log_list(result=list, total=int)
    @ExecuteOperation.get_execute_job_log_history(job_id=int, exec_type=int, start_time=int, end_time=int,
                                                  run_status=str, page=int, limit=int)
    @ExecuteVerify.verify_get_execute_job_history(job_id=int, exec_type=int, start_time=int, end_time=int,
                                                  run_status=str, page=int, limit=int)
    def get():
        """获取任务历史日志列表"""
        params = Response(
            job_id=int(get_arg('job_id', 0)),
            exec_type=int(get_arg('exec_type', 0)),
            start_time=int(get_arg('start_time', 0)),
            end_time=int(get_arg('end_time', 0)),
            run_status=get_arg('run_status', ''),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取任务历史日志列表[params: %s]' % str(params))
        return params


class ExecuteFlowDetail(Resource):
    @staticmethod
    @ExecuteFilter.filter_get_execute_flow_detail(result=list)
    @ExecuteOperation.get_execute_flow_detail(exec_id=int)
    @ExecuteVerify.verify_get_execute_flow_detail(exec_id=int)
    def get(exec_id):
        """获取任务流执行详情"""
        params = Response(exec_id=exec_id)
        log.info('获取执行详情[params: %s]' % str(params))
        return params


class ExecuteAction(Resource):
    @staticmethod
    @execute_stop_requests
    @ExecuteFilter.filter_stop_execute_job(msg=list)
    @ExecuteOperation.stop_execute_job(exec_id=list)
    @ExecuteVerify.verify_stop_execute(exec_id=list, user_id=int)
    @PermissionVerify.verify_execute_permission(exec_id=list)
    def delete():
        """中止执行任务"""
        payload = get_payload()
        params = Response(exec_id=payload.get('exec_id', []))
        log.info('中止执行任务[params: %s]' % str(params))
        return params

    @staticmethod
    @execute_restart_requests
    @ExecuteFilter.filter_restart(msg=str)
    @ExecuteOperation.restart_execute_job(exec_id=list)
    @ExecuteVerify.verify_restart_execute(exec_id=list, user_id=int)
    @PermissionVerify.verify_execute_permission(exec_id=list)
    def post():
        """断点续跑"""
        payload = get_payload()
        params = Response(
            exec_id=payload.get('exec_id', [])
        )
        log.info('执行任务断点续跑[params: %s]' % str(params))
        return params

    @staticmethod
    @execute_reset_requests
    @ExecuteFilter.filter_reset(exec_id=list)
    @ExecuteOperation.reset_execute_job(exec_id=list)
    @ExecuteVerify.verify_reset_execute(exec_id=list, user_id=int)
    @PermissionVerify.verify_execute_permission(exec_id=list)
    def put():
        """重置执行任务"""
        payload = get_payload()
        params = Response(exec_id=payload.get('exec_id', []))
        log.info('重置执行任务[params: %s]' % str(params))
        return params

    @staticmethod
    @execute_start_requests
    @ExecuteFilter.filter_start(exec_id=list)
    @ExecuteOperation.start_execute_job(exec_id=list)
    @ExecuteVerify.verify_start_execute(exec_id=list, user_id=int)
    @PermissionVerify.verify_execute_permission(exec_id=list)
    def patch():
        """启动执行任务(重置任务后)"""
        payload = get_payload()
        params = Response(exec_id=payload.get('exec_id', []))
        log.info('启动执行任务[params: %s]' % str(params))
        return params


class ExecuteJobLog(Resource):
    @staticmethod
    @execute_log_request
    @ExecuteFilter.filter_get_execute_job_log(result=list, job_id=int)
    @ExecuteOperation.get_execute_job_log(exec_id=int, job_id=int)
    @ExecuteVerify.verify_get_execute_job_log(exec_id=int, job_id=int)
    def get():
        """获取任务执行日志"""
        params = Response(
            exec_id=int(get_arg('exec_id', 0)),
            job_id=int(get_arg('job_id', 0))
        )
        log.info('获取执行日志[params: %s]' % str(params))
        return params


class ExecuteGraph(Resource):
    @staticmethod
    @execute_graph_request
    @ExecuteFilter.filter_get_execute_graph(result=list, data_type=int)
    @ExecuteOperation.get_execute_graph(exec_id=int, interface_id=int)
    @ExecuteVerify.verify_get_execute_graph(exec_id=int, interface_id=int)
    def get():
        """获取执行拓扑结构"""
        params = Response(
            exec_id=int(get_arg('exec_id', 0)),
            interface_id=int(get_arg('interface_id', 0))
        )
        log.info('获取执行拓扑结构[params: %s]' % str(params))
        return params


ns = api.namespace('execute', description='执行')
ns.add_resource(ExecuteCallBack, '/callback/')
ns.add_resource(ExecuteFlow, '/flow/api/')
ns.add_resource(ExecuteFlowHistory, '/flow/history/api/')
ns.add_resource(ExecuteInterfaceList, '/interface/list/api/')
ns.add_resource(ExecuteJob, '/job/api/')
ns.add_resource(ExecuteHistoryJob, '/job/history/api/')
ns.add_resource(ExecuteFlowDetail, '/flow/detail/api/<int:exec_id>/')
ns.add_resource(ExecuteAction, '/action/api/')
ns.add_resource(ExecuteJobLog, '/job/log/api/')
ns.add_resource(ExecuteGraph, '/graph/api/')
