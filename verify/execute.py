# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class ExecuteVerify(object):
    @staticmethod
    @make_decorator
    def verify_callback(exec_id, status):
        """验证回调函数"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不存在'))
        if not status:
            abort(400, **make_result(status=400, msg='任务状态'))
        return Response(exec_id=exec_id, status=status)

    @staticmethod
    @make_decorator
    def verify_get_execute_list(interface_id, start_time, end_time, run_status, exec_type, page, limit):
        """获取执行列表"""
        if start_time and end_time and start_time >= end_time:
            abort(400, **make_result(status=400, msg='创建开始时间大于创建结束时间'))
        if run_status < 0 or run_status > 4:
            abort(400, **make_result(status=400, msg='运行状态错误'))
        if exec_type < 0 or exec_type > 2:
            abort(400, **make_result(status=400, msg='执行类型错误'))

        return Response(interface_id=interface_id, start_time=start_time, end_time=end_time, run_status=run_status,
                        exec_type=exec_type, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_execute_detail(exec_id):
        """获取执行详情"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id)

    @staticmethod
    @make_decorator
    def verify_get_execute_log(exec_id, job_id):
        """获取执行日志"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id, job_id=job_id)

    @staticmethod
    @make_decorator
    def verify_get_execute_graph(exec_id):
        """获取执行拓扑结构"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id)
