# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from server.decorators import make_decorator
from util.time_format import seconds_format
from util.graph_format import execute_nodes_graph


class ExecuteFilter(object):
    @staticmethod
    @make_decorator
    def filter_callback(msg):
        """执行服务任务回调"""
        return {'status': 200, 'msg': msg, 'data': {}}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_flow(result, total):
        """获取任务流最新日志列表"""
        for item in result:
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time'])) if item[
                'insert_time'] else None
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time'])) if item[
                'update_time'] else None
            item['timedelta'] = seconds_format(item['timedelta']) if item['timedelta'] else None
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_flow_history(result, total):
        """获取任务流历史日志列表"""
        for item in result:
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time'])) if item[
                'insert_time'] else None
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time'])) if item[
                'update_time'] else None
            item['timedelta'] = seconds_format(item['timedelta']) if item['timedelta'] else None
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_job_log_list(result, total):
        """获取手动执行任务日志"""
        for item in result:
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time'])) if item[
                'insert_time'] else None
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time'])) if item[
                'update_time'] else None
            item['timedelta'] = seconds_format(item['timedelta']) if item['timedelta'] else None
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_job_log_history(result, total):
        """获取任务历史日志列表"""
        for item in result:
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time'])) if item[
                'insert_time'] else None
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time'])) if item[
                'update_time'] else None
            item['timedelta'] = seconds_format(item['timedelta']) if item['timedelta'] else None
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_flow_detail(result):
        """获取任务流执行详情"""
        for item in result:
            item['margin_left'] = 1 if item['margin_left'] > 1 else item['margin_left']
            if item['margin_left'] + item['width'] > 1:
                item['width'] = 1 - item['margin_left']
            if item['margin_left'] and item['margin_left'] < 1:
                item['margin_left'] = '%s%%' % (item['margin_left'] * 100)
                item['width'] = '%s%%' % (item['width'] * 100) if item['width'] else '0'
            else:
                item['margin_left'] = '0'
                item['width'] = '0'
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time']))
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time']))
            item['timedelta'] = seconds_format(item['timedelta'])

        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_job_log(result, job_id):
        """获取执行日志"""
        group_result = {}
        # 任务日志分组聚合
        for item in result:
            group_result.setdefault(item['job_id'], {
                'interface_id': item['interface_id'], 'job_name': item['job_name'], 'message': ''
            })
            group_result[item['job_id']]['message'] += '[%s] %s<br>' % (item['level'], item['message'])
        result = []
        for key, item in group_result.items():
            result.append({
                'interface_id': item['interface_id'],
                'job_id': key,
                'job_name': item['job_name'],
                'message': item['message'] + '...' if not job_id else item['message']
            })
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_graph(result, data_type):
        """获取执行拓扑结构"""
        # 执行节点依赖渲染
        data = execute_nodes_graph(result, data_type)
        return {'status': 200, 'msg': '成功', 'data': data}, 200

    @staticmethod
    @make_decorator
    def filter_stop_execute_job(msg):
        """中止执行任务"""
        if not msg:
            return {'status': 200, 'msg': '成功', 'data': {}}, 200
        else:
            return {'status': 200, 'msg': '<br>' + ';<br>'.join(msg), 'data': {}}, 200

    @staticmethod
    @make_decorator
    def filter_restart(msg):
        """执行服务任务回调"""
        return {'status': 200, 'msg': msg, 'data': {}}, 200

    @staticmethod
    @make_decorator
    def filter_reset(exec_id):
        """重置执行任务"""
        return {'status': 200, 'msg': '成功', 'data': {'exec_id': exec_id}}, 200

    @staticmethod
    @make_decorator
    def filter_start(exec_id):
        """启动执行任务"""
        return {'status': 200, 'msg': '成功', 'data': {'exec_id': exec_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_interface_list(result):
        """获取该执行下的任务流列表"""
        data = []
        for item in result:
            data.append({
                'interface_id': item['id'],
                'interface_name': item['name']
            })
        return {'status': 200, 'msg': '成功', 'data': data}, 200
