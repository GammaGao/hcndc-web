# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class InterfaceVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_interface_list(interface_name, interface_index, start_time, end_time, is_deleted, page, limit):
        """获取任务流列表"""
        # 任务流目录
        interface_index = interface_index.split(',') if interface_index else []
        # 创建时间
        if start_time and end_time and start_time >= end_time:
            abort(400, **make_result(status=400, msg='创建开始时间大于创建结束时间'))
        if is_deleted > 2:
            abort(400, **make_result(status=400, msg='任务流使用参数错误'))

        return Response(interface_name=interface_name, interface_index=interface_index, start_time=start_time,
                        end_time=end_time, is_deleted=is_deleted, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_interface_graph(interface_id):
        """获取任务流拓扑结构"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流不存在'))
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def verify_get_interface_detail(interface_id):
        """获取任务流详情"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流id不存在'))

        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def verify_update_interface_detail(interface_id, interface_name, interface_desc, interface_index, retry, user_id,
                                       is_deleted):
        """修改任务流详情"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流id不存在'))
        if not interface_name:
            abort(400, **make_result(status=400, msg='任务流名称不存在'))
        if not interface_index:
            abort(400, **make_result(status=400, msg='任务流目录不存在'))
        elif re.findall(',', interface_index):
            abort(400, **make_result(status=400, msg='任务流目录中不得出现逗号字符","'))
        if retry < 0 or retry > 10:
            abort(400, **make_result(status=400, msg='重试次数请限制在0-10之内'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='是否删除参数错误'))

        return Response(interface_id=interface_id, interface_name=interface_name, interface_desc=interface_desc,
                        interface_index=interface_index, retry=retry, user_id=user_id, is_deleted=is_deleted)

    @staticmethod
    @make_decorator
    def verify_add_interface(interface_name, interface_desc, interface_index, retry, user_id):
        """新增任务流请求"""
        if not interface_name:
            abort(400, **make_result(status=400, msg='任务流名称不存在'))
        if not interface_index:
            abort(400, **make_result(status=400, msg='任务流目录不存在'))
        elif re.findall(',', interface_index):
            abort(400, **make_result(status=400, msg='任务流目录中不得出现逗号字符","'))
        if retry < 0 or retry > 10:
            abort(400, **make_result(status=400, msg='重试次数请限制在0-10之内'))
        return Response(interface_name=interface_name, interface_desc=interface_desc, interface_index=interface_index,
                        retry=retry, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_delete_interface(interface_id, user_id):
        """删除任务流"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流id不存在'))
        return Response(interface_id=interface_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_delete_many_flow(flow_id_arr, user_id):
        """批量删除任务流"""
        if not flow_id_arr:
            abort(400, **make_result(status=400, msg='任务流id不存在'))
        return Response(flow_id_arr=flow_id_arr, user_id=user_id)
