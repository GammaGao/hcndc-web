# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result
from util import session


class PermissionVerify(object):
    """权限验证"""
    @staticmethod
    @make_decorator
    def verify_write_permission(**kwargs):
        """新增、更改、删除权限"""
        user_info = session.get_info()
        if 'write' not in user_info['permission']:
            abort(403, **make_result(status=403, msg='无操作权限'))
        kwargs['user_id'] = user_info['id']
        return Response(**kwargs)

    @staticmethod
    @make_decorator
    def verify_execute_permission(**kwargs):
        """执行权限"""
        user_info = session.get_info()
        if 'execute' not in user_info['permission']:
            abort(403, **make_result(status=403, msg='无执行权限'))
        kwargs['user_id'] = user_info['id']
        return Response(**kwargs)

    @staticmethod
    @make_decorator
    def verify_schedule_permission(**kwargs):
        """调度权限"""
        user_info = session.get_info()
        if 'schedule' not in user_info['permission']:
            abort(403, **make_result(status=403, msg='无调度权限'))
        kwargs['user_id'] = user_info['id']
        return Response(**kwargs)
