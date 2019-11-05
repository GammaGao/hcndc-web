# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class InterfaceVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_interface_list(interface_name, start_time, end_time, interface_type, is_deleted, page, limit):
        """获取工作流列表"""
        if start_time and end_time and start_time >= end_time:
            abort(400, **make_result(status=400, msg='创建开始时间大于创建结束时间'))
        if is_deleted > 2:
            abort(400, **make_result(status=400, msg='工作流使用参数错误'))
        if interface_type > 5:
            abort(400, **make_result(status=400, msg='工作流类型参数错误'))

        return Response(interface_name=interface_name, start_time=start_time, end_time=end_time,
                        interface_type=interface_type, is_deleted=is_deleted, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_interface_graph(interface_id):
        """获取工作流拓扑结构"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='工作流不存在'))
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def verify_get_interface_detail(interface_id):
        """获取工作流详情"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='工作流id不存在'))

        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def verify_update_interface_detail(interface_id, interface_name, interface_desc, retry, user_id, is_deleted):
        """修改工作流详情"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='工作流id不存在'))
        if not interface_name:
            abort(400, **make_result(status=400, msg='工作流名称不存在'))
        if retry < 0 or retry > 10:
            abort(400, **make_result(status=400, msg='重试次数请限制在0-10之内'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='是否删除参数错误'))

        return Response(interface_id=interface_id, interface_name=interface_name, interface_desc=interface_desc,
                        retry=retry, user_id=user_id, is_deleted=is_deleted)

    @staticmethod
    @make_decorator
    def verify_add_interface(interface_name, interface_desc, retry, user_id):
        """新增工作流请求"""
        if not interface_name:
            abort(400, **make_result(status=400, msg='工作流名称不存在'))
        if retry < 0 or retry > 10:
            abort(400, **make_result(status=400, msg='重试次数请限制在0-10之内'))
        return Response(interface_name=interface_name, interface_desc=interface_desc, retry=retry, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_delete_interface(interface_id, user_id):
        """删除工作流"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='工作流id不存在'))
        return Response(interface_id=interface_id, user_id=user_id)