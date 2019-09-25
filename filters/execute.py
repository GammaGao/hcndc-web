# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from math import log

from server.decorators import make_decorator
from util.time_format import seconds_format


class ExecuteFilter(object):
    @staticmethod
    @make_decorator
    def filter_callback(distribute_job):
        """执行服务任务回调"""
        return {'status': 200, 'msg': '成功', 'data': distribute_job}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_list(result, total):
        """任务列表"""
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
            item['margin_left'] = '%s%%' % (item['margin_left'] * 100) if item['margin_left'] else '0'
            item['width'] = '%s%%' % (item['width'] * 100) if item['width'] else '0'
            item['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time']))
            item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['update_time']))
            item['timedelta'] = seconds_format(item['timedelta'])
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_log(result):
        """获取执行日志"""
        for item in result:
            item['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['insert_time']))
        return {'stauts': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_execute_graph(job_nodes):
        """获取执行拓扑结构"""
        if not job_nodes:
            return {'status': 200, 'msg': '成功', 'data': {'nodes': [], 'links': [], 'categories': []}}, 200
        remakes = {
            'ready': '等待依赖任务完成',
            'preparing': '待运行',
            'running': '运行中',
            'succeeded': '成功',
            'failed': '失败'
        }
        nodes = {}
        links = []
        layers = {}
        symbolSize = log(10, len(job_nodes)) * 40 if len(job_nodes) > 1 else 30
        horizontalMargin = 20 * (1 + 1 / len(job_nodes)) if len(job_nodes) > 1 else 10
        verticalMargin = len(job_nodes)
        # 0.预处理: id统一为字符串
        for job in job_nodes:
            job['job_id'] = str(job['job_id']) if job['job_id'] else None
        # 1.构造节点
        for job in job_nodes:
            # 目标节点
            if job['job_id'] not in nodes:
                nodes[job['job_id']] = {
                    'id': job['job_id'],
                    'name': job['job_name'],
                    'itemStyle': None,
                    'symbolSize': symbolSize,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': remakes[job['status']] if job['status'] else '外部节点',
                    'in': job['in_degree'].split(',') if job['in_degree'] else [],
                    'out': job['out_degree'].split(',') if job['out_degree'] else [],
                    'level': job['level']
                }
        # 2.计算节点层级
        # 最大层级
        maxLayer = max(j['level'] for i, j in nodes.items())
        # 填充层级对象
        for _, node in nodes.items():
            if node['level'] not in layers:
                layers[node['level']] = []
            layers[node['level']].append(node)
        # 3.构造连线
        for job in job_nodes:
            # 有依赖关系
            in_degree = job['in_degree'].split(',') if job['in_degree'] else []
            # 相邻层级
            for source_node in in_degree:
                if abs(nodes[job['job_id']]['level'] - nodes[source_node]['level']) == 1:
                    links.append({'source': source_node, 'target': job['job_id']})
                else:
                    min_transit = min(nodes[job['job_id']]['level'], nodes[source_node]['level']) + 1
                    max_transit = max(nodes[job['job_id']]['level'], nodes[source_node]['level'])
                    for transit_level in range(min_transit, max_transit):
                        # 添加过渡节点
                        transit_id = source_node + '>' + job['job_id'] + '>' + str(transit_level)
                        nodes[transit_id] = {
                            'id': transit_id,
                            'name': '',
                            'itemStyle': None,
                            'symbolSize': 1,
                            'x': 0,
                            'y': 0,
                            'label': {'show': True},
                            'category': '虚拟节点',
                            'in': set(),
                            'out': set(),
                            'level': transit_level
                        }
                        layers[transit_level].append(nodes[transit_id])
                        # 添加过渡边
                        links.append({'source': source_node, 'target': transit_id})
                        source_node = transit_id
                    # 添加结束边
                    links.append({'source': source_node, 'target': job['job_id']})
        # 4.计算坐标
        for level in range(maxLayer + 1):
            # x坐标
            layer = layers[level]
            ranges = {
                'start': 0,
                'end': 0,
                'width': horizontalMargin,
                'x': 0
            }
            # 遍历每层所有节点
            for node_index in range(1, len(layer)):
                ranges['end'] = node_index
                ranges['width'] += horizontalMargin
            # 多个节点
            if ranges['start'] != ranges['end']:
                # 负数折半
                left = -ranges['width'] / 2
                for j in range(0, len(layer)):
                    layer[j]['x'] = left + horizontalMargin / 2
                    left += horizontalMargin
        # y坐标
        for level in range(maxLayer + 1):
            for node in layers[level]:
                node['y'] = verticalMargin * level
        # 5.数据整理
        for _, node in nodes.items():
            node.pop('in')
            node.pop('out')
        # 按层级排序
        nodes = [j for i, j in nodes.items()]
        nodes.sort(key=lambda x: x['level'])
        # 6.节点接口分类
        categories = [
            {'name': '等待依赖任务完成'},
            {'name': '待运行'},
            {'name': '运行中'},
            {'name': '成功'},
            {'name': '失败'},
            {'name': '外部节点'},
            {'name': '虚拟节点'}

        ]
        return {'status': 200, 'msg': '成功', 'data': {'nodes': nodes, 'links': links, 'categories': categories}}, 200