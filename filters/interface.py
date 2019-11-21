# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator
from util.graph_format import job_nodes_graph


class InterfaceFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """任务流列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_interface_graph_data(result, graph_type):
        """获取任务流拓扑结构"""
        # 任务流中任务依赖
        data = {}
        if graph_type == 1:
            data = job_nodes_graph(result)
        # 局部-任务流依赖
        elif graph_type == 2:
            pass
        # 全局-任务流依赖
        elif graph_type == 3:
            pass
        return {'status': 200, 'msg': '成功', 'data': data}, 200

    @staticmethod
    @make_decorator
    def filter_interface_detail_data(detail, parent, child):
        """任务流详情"""
        detail['parent_interface'] = [item['parent_id'] for item in parent]
        detail['child_interface'] = [item['child_id'] for item in child]
        return {'status': 200, 'msg': '成功', 'data': {'detail': detail}}, 200

    @staticmethod
    @make_decorator
    def filter_update_interface_detail(interface_id):
        """修改任务流详情"""
        return {'status': 200, 'msg': '成功', 'data': {'id': interface_id}}, 200

    @staticmethod
    @make_decorator
    def filter_add_interface(interface_id):
        """新增任务流"""
        return {'status': 200, 'msg': '成功', 'data': {'id': interface_id}}, 200

    @staticmethod
    @make_decorator
    def filter_delete_interface(interface_id):
        """删除任务流"""
        return {'status': 200, 'msg': '成功', 'data': {'id': interface_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_interface_id_list(result):
        """获取任务流id列表"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_interface_index(result):
        """获取所有任务流目录"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_delete_interface_many(msg):
        """批量删除任务流"""
        if not msg:
            return {'status': 200, 'msg': '成功', 'data': {}}, 200
        else:
            return {'status': 403, 'msg': '<br>' + ';<br>'.join(msg), 'data': {}}, 200
