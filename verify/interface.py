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
    def verify_get_interface_graph(interface_id, graph_type):
        """获取任务流拓扑结构"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流不存在'))
        if graph_type < 1 or graph_type > 3:
            abort(400, **make_result(status=400, msg='图表类型错误'))
        return Response(interface_id=interface_id, graph_type=graph_type)

    @staticmethod
    @make_decorator
    def verify_get_interface_detail(interface_id):
        """获取任务流详情"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流id不存在'))

        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def verify_update_interface_detail(interface_id, interface_name, interface_desc, interface_index, old_parent,
                                       parent_interface, old_child, child_interface, run_time, retry, user_id,
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
        if run_time and not re.findall(r'\d{4}-\d{2}-\d{2}', run_time):
            abort(400, **make_result(status=400, msg='数据日期格式错误'))
        if retry < 0 or retry > 10:
            abort(400, **make_result(status=400, msg='重试次数请限制在0-10之内'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='是否删除参数错误'))
        # 原任务流前置&后置
        old_parent = [int(item) for item in old_parent.split(',')] if old_parent else []
        old_child = [int(item) for item in old_child.split(',')] if old_child else []
        # 任务流前置&后置
        parent_interface = [int(item) for item in parent_interface.split(',')] if parent_interface else []
        child_interface = [int(item) for item in child_interface.split(',')] if child_interface else []
        if parent_interface and child_interface and set(parent_interface) & set(child_interface):
            abort(400, **make_result(status=400, msg='前置任务流和后置任务流存在交集'))
        return Response(interface_id=interface_id, interface_name=interface_name, interface_desc=interface_desc,
                        interface_index=interface_index, run_time=run_time, old_parent=old_parent,
                        parent_interface=parent_interface, old_child=old_child, child_interface=child_interface,
                        retry=retry, user_id=user_id, is_deleted=is_deleted)

    @staticmethod
    @make_decorator
    def verify_add_interface(interface_name, interface_desc, interface_index, parent_interface, child_interface,
                             run_time, retry, user_id):
        """新增任务流请求"""
        if not interface_name:
            abort(400, **make_result(status=400, msg='任务流名称不存在'))
        if not interface_index:
            abort(400, **make_result(status=400, msg='任务流目录不存在'))
        elif re.findall(',', interface_index):
            abort(400, **make_result(status=400, msg='任务流目录中不得出现逗号字符","'))
        if run_time and not re.findall(r'\d{4}-\d{2}-\d{2}', run_time):
            abort(400, **make_result(status=400, msg='数据日期格式错误'))
        if retry < 0 or retry > 10:
            abort(400, **make_result(status=400, msg='重试次数请限制在0-10之内'))
        # 任务流前置&后置
        parent_interface = [int(item) for item in parent_interface.split(',')] if parent_interface else []
        child_interface = [int(item) for item in child_interface.split(',')] if child_interface else []
        if parent_interface and child_interface and set(parent_interface) & set(child_interface):
            abort(400, **make_result(status=400, msg='前置任务流和后置任务流存在交集'))
        return Response(interface_name=interface_name, interface_desc=interface_desc, interface_index=interface_index,
                        parent_interface=parent_interface, child_interface=child_interface, run_time=run_time,
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
