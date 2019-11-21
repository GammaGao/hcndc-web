# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from server.decorators import make_decorator
from util.time_format import seconds_format
from util.graph_format import execute_nodes_graph


class ExecuteFilter(object):
    @staticmethod
    @make_decorator
    def filter_callback(distribute_job, msg):
        """执行服务任务回调"""
        return {'status': 200, 'msg': msg, 'data': distribute_job}, 200

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
        # 优先级排序
        group_result = {}
        for item in result:
            group_result.setdefault(-1, [])
            group_result.setdefault(2, [])
            group_result.setdefault(3, [])
            group_result.setdefault(1, [])
            group_result.setdefault(0, [])
            group_result.setdefault('-', [])
            if isinstance(item['status'], int):
                group_result[item['status']].append(item)
            else:
                group_result['-'].append(item)
        sort_index = [-1, 2, 3, 1, 0, '-']
        result = []
        for index in sort_index:
            result.extend(group_result[index])
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_history(result, total):
        """获取任务流历史日志列表"""
        for item in result:
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time']))
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time']))
            item['timedelta'] = seconds_format(item['timedelta'])
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_job_log(result, total):
        """获取手动执行任务日志"""
        for item in result:
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time']))
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time']))
            item['timedelta'] = seconds_format(item['timedelta'])
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_detail(result):
        """获取执行详情"""
        for item in result:
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
    def filter_get_execute_log(result):
        """获取执行日志"""
        group_result = {}
        for item in result:
            group_result.setdefault(item['job_id'], {'job_name': item['job_name'], 'message': ''})
            group_result[item['job_id']]['message'] = group_result[item['job_id']]['message'] \
                                                      + '[%s] %s<br>' % (item['level'], item['message'])
        result = []
        for key, item in group_result.items():
            result.append({'job_id': key, 'job_name': item['job_name'], 'message': item['message']})
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_graph(job_nodes):
        """获取执行拓扑结构"""
        # 执行节点依赖渲染
        data = execute_nodes_graph(job_nodes)
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
