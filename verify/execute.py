# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class ExecuteVerify(object):
    @staticmethod
    @make_decorator
    def verify_callback(exec_id, interface_id, job_id, status):
        """验证回调函数"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不存在'))
        if not job_id:
            abort(400, **make_result(status=400, msg='任务id不存在'))
        if not status:
            abort(400, **make_result(status=400, msg='任务状态'))
        return Response(exec_id=exec_id, interface_id=interface_id, job_id=job_id, status=status)

    @staticmethod
    @make_decorator
    def verify_get_execute_flow(interface_id, interface_index, run_status, start_time, end_time, page, limit):
        """获取任务流日志"""
        # 任务流目录
        interface_index = interface_index.split(',') if interface_index else []
        # 执行时间
        if start_time and end_time and start_time >= end_time:
            abort(400, **make_result(status=400, msg='创建开始时间大于创建结束时间'))
        if run_status < 0 or run_status > 5:
            abort(400, **make_result(status=400, msg='运行状态错误'))

        return Response(interface_id=interface_id, interface_index=interface_index, run_status=run_status,
                        start_time=start_time, end_time=end_time, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_execute_flow_history(dispatch_id, start_time, end_time, run_status, page, limit):
        """获取任务流历史日志"""
        # 调度ID
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度ID缺失'))
        # 执行时间
        if start_time and end_time and start_time >= end_time:
            abort(400, **make_result(status=400, msg='执行开始时间大于创建结束时间'))
        if run_status < 0 or run_status > 5:
            abort(400, **make_result(status=400, msg='运行状态错误'))

        return Response(dispatch_id=dispatch_id, start_time=start_time, end_time=end_time, run_status=run_status,
                        page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_execute_job_log_1(job_id, start_time, end_time, run_status, page, limit):
        """获取手动执行任务日志"""
        # 执行时间
        if start_time and end_time and start_time >= end_time:
            abort(400, **make_result(status=400, msg='执行开始时间大于创建结束时间'))
        if run_status < 0 or run_status > 5:
            abort(400, **make_result(status=400, msg='运行状态错误'))

        return Response(job_id=job_id, start_time=start_time, end_time=end_time, run_status=run_status,
                        page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_execute_flow_detail(exec_id):
        """获取任务流执行详情"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id)

    @staticmethod
    @make_decorator
    def verify_get_execute_job_log(exec_id, job_id):
        """获取任务执行日志"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id, job_id=job_id)

    @staticmethod
    @make_decorator
    def verify_get_execute_graph(exec_id, interface_id):
        """获取执行拓扑结构"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id, interface_id=interface_id)

    @staticmethod
    @make_decorator
    def verify_stop_execute(exec_id, user_id):
        """中止执行任务"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_restart_execute(exec_id, user_id):
        """断点续跑"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_reset_execute(exec_id, user_id):
        """重置执行任务"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_start_execute(exec_id, user_id):
        """启动执行任务(重置任务后)"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_get_execute_interface_list(exec_id):
        """获取该执行下的任务流列表"""
        if not exec_id:
            abort(400, **make_result(status=400, msg='执行id不得为空'))
        return Response(exec_id=exec_id)
