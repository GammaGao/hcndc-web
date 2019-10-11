# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from configs import log
from server.decorators import Response
from server.request import get_arg
from filters.execute import ExecuteFilter
from operations.execute import ExecuteOperation
from verify.execute import ExecuteVerify
from document.execute import *


class ExecuteCallBack(Resource):
    @staticmethod
    @callback_request
    @ExecuteFilter.filter_callback(distribute_job=list)
    @ExecuteOperation.get_execute_job(exec_id=int, status=str)
    @ExecuteVerify.verify_callback(exec_id=int, status=str)
    def get():
        """执行服务任务回调"""
        params = Response(
            exec_id=int(get_arg('exec_id', 0)),
            status=get_arg('status', '')
        )
        log.info('获取执行服务任务回调[params: %s]' % str(params))
        return params


class ExecuteList(Resource):
    @staticmethod
    @execute_list_request
    @ExecuteFilter.filter_get_execute_list(result=list, total=int)
    @ExecuteOperation.get_execute_list(interface_id=int, start_time=int, end_time=int, run_status=int, exec_type=int,
                                       page=int, limit=int)
    @ExecuteVerify.verify_get_execute_list(interface_id=int, start_time=int, end_time=int, run_status=int,
                                           exec_type=int, page=int, limit=int)
    def get():
        """获取执行列表"""
        params = Response(
            interface_id=int(get_arg('interface_id', 0)),
            start_time=int(get_arg('start_time', 0)),
            end_time=int(get_arg('end_time', 0)),
            run_status=int(get_arg('run_status', 0)),
            exec_type=int(get_arg('exec_type', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取执行列表[params: %s]' % str(params))
        return params


class ExecuteDetail(Resource):
    @staticmethod
    @ExecuteFilter.filter_get_execute_detail(result=list)
    @ExecuteOperation.get_execute_detail(exec_id=int)
    @ExecuteVerify.verify_get_execute_detail(exec_id=int)
    def get(exec_id):
        """获取执行详情"""
        params = Response(exec_id=exec_id)
        log.info('获取执行详情[params: %s]' % str(params))
        return params


class ExecuteLog(Resource):
    @staticmethod
    @execute_log_request
    @ExecuteFilter.filter_get_execute_log(result=list)
    @ExecuteOperation.get_execute_log(exec_id=int, job_id=int)
    @ExecuteVerify.verify_get_execute_log(exec_id=int, job_id=int)
    def get():
        """获取执行日志"""
        params = Response(
            exec_id=int(get_arg('exec_id', 0)),
            job_id=int(get_arg('job_id', 0))
        )
        log.info('获取执行日志[params: %s]' % str(params))
        return params


class ExecuteGraph(Resource):
    @staticmethod
    @execute_graph_request
    @ExecuteFilter.filter_get_execute_graph(job_nodes=list)
    @ExecuteOperation.get_execute_graph(exec_id=int)
    @ExecuteVerify.verify_get_execute_graph(exec_id=int)
    def get():
        """获取执行拓扑结构"""
        params = Response(exec_id=int(get_arg('exec_id', 0)))
        log.info('获取执行拓扑结构[params: %s]' % str(params))
        return params


ns = api.namespace('execute', description='执行')
ns.add_resource(ExecuteCallBack, '/callback/')
ns.add_resource(ExecuteList, '/list/api/')
ns.add_resource(ExecuteDetail, '/detail/api/<int:exec_id>/')
ns.add_resource(ExecuteLog, '/log/api/')
ns.add_resource(ExecuteGraph, '/graph/api/')
