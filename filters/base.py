# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator

import time


class ExecFilter(object):
    @staticmethod
    @make_decorator
    def filter_exec_host_list_data(result, total):
        """执行服务器列表"""
        for item in result:
            if item['last_ping_time']:
                item['last_ping_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['last_ping_time']))
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_exec_host_detail_data(result):
        """执行服务器详情"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_exec_host_update(server_id):
        """修改执行服务器"""
        return {'status': 200, 'msg': '成功', 'data': {'id': server_id}}, 200

    @staticmethod
    @make_decorator
    def filter_exec_host_delete(server_id):
        """删除执行服务器"""
        return {'status': 200, 'msg': '成功', 'data': {'id': server_id}}, 200

    @staticmethod
    @make_decorator
    def filter_exec_host_test(result):
        """测试执行服务器"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_exec_host_add(host_id):
        """新增执行服务器"""
        return {'status': 200, 'msg': '成功', 'data': {'id': host_id}}, 200

    @staticmethod
    @make_decorator
    def filter_exec_host_status(result, total):
        """获取执行服务器状态"""
        for item in result:
            if item['last_ping_time']:
                item['last_ping_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['last_ping_time']))
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200


class AlertFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """获取预警配置列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_list_all_data(result):
        """获取预警配置列表(全)"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_delete_data(conf_id):
        """删除预警配置"""
        return {'status': 200, 'msg': '成功', 'data': {'id': conf_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_detail_data(result):
        """获取预警配置详情"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_update_detail_data(conf_id):
        """修改预警配置"""
        return {'status': 200, 'msg': '成功', 'data': {'id': conf_id}}, 200

    @staticmethod
    @make_decorator
    def filter_add_detail_data(conf_id):
        """新增预警配置"""
        return {'status': 200, 'msg': '成功', 'data': {'id': conf_id}}, 200
