# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class JobVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_job_list(job_name, start_time, end_time, interface_id, is_deleted, page, limit):
        """获取任务列表"""
        if start_time and end_time and start_time >= end_time:
            abort(400, **make_result(status=400, msg='创建开始时间大于创建结束时间'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))

        return Response(job_name=job_name, start_time=start_time, end_time=end_time,
                        interface_id=interface_id, is_deleted=is_deleted, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_delete_job(job_id, user_id):
        """删除任务"""
        if not job_id:
            abort(400, **make_result(status=400, msg='任务id不存在'))

        return Response(job_id=job_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_get_job_id(job_id):
        """获取任务"""
        if not job_id:
            abort(400, **make_result(status=400, msg='任务id不存在'))

        return Response(job_id=job_id)

    @staticmethod
    @make_decorator
    def verify_update_job_id(job_id, interface_id, job_name, job_desc, server_id, server_dir, server_script,
                             return_code, old_prep, job_prep, user_id, old_params, job_params, is_deleted):
        """修改任务"""
        if not job_id:
            abort(400, **make_result(status=400, msg='任务id不存在'))
        if not interface_id:
            abort(400, **make_result(status=400, msg='接口id不存在'))
        if not user_id:
            abort(400, **make_result(status=400, msg='用户不存在'))
        if not server_id:
            abort(400, **make_result(status=400, msg='执行服务器id不存在'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='是否删除参数错误'))
        if return_code < 0:
            abort(400, **make_result(status=400, msg='返回状态码应大于等于0'))
        return Response(job_id=job_id, interface_id=interface_id, job_name=job_name, job_desc=job_desc,
                        server_id=server_id, server_dir=server_dir, server_script=server_script,
                        return_code=return_code, old_prep=old_prep, job_prep=job_prep, old_params=old_params,
                        job_params=job_params, user_id=user_id, is_deleted=is_deleted)

    @staticmethod
    @make_decorator
    def verify_add_job_id(job_name, interface_id, job_desc, server_id, job_prep, job_params, server_dir, server_script,
                          user_id, return_code):
        """新增任务"""
        if not job_name:
            abort(400, **make_result(status=400, msg='任务名称不存在'))
        if not interface_id:
            abort(400, **make_result(status=400, msg='接口id不存在'))
        if not server_id:
            abort(400, **make_result(status=400, msg='执行服务器id不存在'))
        if not server_script:
            abort(400, **make_result(status=400, msg='脚本命令不存在'))
        if not user_id:
            abort(400, **make_result(status=400, msg='用户不存在'))
        if return_code < 0:
            abort(400, **make_result(status=400, msg='返回状态码应大于等于0'))

        return Response(job_name=job_name, interface_id=interface_id, job_desc=job_desc, server_id=server_id,
                        job_prep=job_prep, job_params=job_params, server_dir=server_dir, server_script=server_script,
                        user_id=user_id, return_code=return_code)

    @staticmethod
    @make_decorator
    def verify_execute_job(job_id, user_id):
        """立即执行任务"""
        if not job_id:
            abort(400, **make_result(status=400, msg='任务id不存在'))
        if not user_id:
            abort(400, **make_result(status=400, msg='用户不存在'))
        return Response(job_id=job_id, user_id=user_id)
