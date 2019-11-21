# !/usr/bin/env python
# -*- coding: utf-8 -*-

from math import log


def job_nodes_graph(job_nodes):
    """任务节点依赖"""
    if not job_nodes:
        return {'nodes': [], 'links': [], 'categories': []}
    nodes = {}
    links = []
    layers = {}
    symbol_size = log(10, len(job_nodes)) * 40 if len(job_nodes) > 1 else 30
    horizontal_margin = 20 * (1 + 1 / len(job_nodes)) if len(job_nodes) > 1 else 10
    vertical_margin = len(job_nodes)
    # 0.预处理: id统一为字符串
    for job in job_nodes:
        job['job_id'] = str(job['job_id']) if job['job_id'] else None
        job['prep_id'] = str(job['prep_id']) if job['prep_id'] else None
    # 1.构造节点
    for job in job_nodes:
        # 直连边
        # if job['job_id'] and job['prep_id']:
        #     links.append({'source': job['prep_id'], 'target': job['job_id']})
        # 目标节点
        if job['job_id'] and job['interface_id']:
            if job['job_id'] not in nodes:
                nodes[job['job_id']] = {
                    'id': job['job_id'],
                    'name': job['job_name'],
                    'itemStyle': None,
                    'symbolSize': symbol_size,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': job['interface_id'],
                    'in': set(),
                    'out': set(),
                    'level': 0
                }
            # 入度
            nodes[job['job_id']]['in'].add(job['prep_id']) if job['prep_id'] else None
        # 依赖节点
        if job['prep_id'] and job['prep_interface_id']:
            if job['prep_id'] not in nodes:
                nodes[job['prep_id']] = {
                    'id': job['prep_id'],
                    'name': job['prep_name'],
                    'itemStyle': None,
                    'symbolSize': symbol_size,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': job['prep_interface_id'],
                    'in': set(),
                    'out': set(),
                    'level': 0
                }
            # 出度
            nodes[job['prep_id']]['out'].add(job['job_id']) if job['job_id'] else None

    # 2.计算节点层级
    node_queue = []
    # 找出开始节点
    for _, node in nodes.items():
        node_queue.append(node) if not node['in'] else None
    # 计算层级
    index = 0
    while index < len(node_queue):
        node = node_queue[index]
        if node['in']:
            level = 0
            for key in node['in']:
                level = max(level, nodes[key]['level'])
            node['level'] = level + 1

        # 添加队列
        for out_id in node['out']:
            if out_id not in map(lambda x: x['id'], node_queue):
                node_queue.append(nodes[out_id])
        index += 1
    # 最大层级
    max_layer = max(j['level'] for i, j in nodes.items())
    # 填充层级对象
    for _, node in nodes.items():
        if node['level'] not in layers:
            layers[node['level']] = []
        layers[node['level']].append(node)
    # 3.构造连线
    for job in job_nodes:
        # 有依赖关系
        if job['job_id'] and job['prep_id']:
            # 相邻层级
            if abs(nodes[job['job_id']]['level'] - nodes[job['prep_id']]['level']) == 1:
                links.append({'source': job['prep_id'], 'target': job['job_id']})
            else:
                source_node = job['prep_id']
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
                        'category': 0,
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
    for level in range(max_layer + 1):
        # x坐标
        layer = layers[level]
        ranges = {
            'start': 0,
            'end': 0,
            'width': horizontal_margin,
            'x': 0
        }
        # 遍历每层所有节点
        for node_index in range(1, len(layer)):
            ranges['end'] = node_index
            ranges['width'] += horizontal_margin
        # 多个节点
        if ranges['start'] != ranges['end']:
            # 负数折半
            left = -ranges['width'] / 2
            for j in range(0, len(layer)):
                layer[j]['x'] = left + horizontal_margin / 2
                left += horizontal_margin
    # y坐标
    for level in range(max_layer + 1):
        for node in layers[level]:
            node['y'] = vertical_margin * level

    # 5.数据整理
    for _, node in nodes.items():
        node.pop('in')
        node.pop('out')
    # 按层级排序
    nodes = [j for i, j in nodes.items()]
    nodes.sort(key=lambda x: x['level'])
    # 6.节点任务流分类
    interface_id = set(node['category'] for node in nodes)
    interface_dict = {}
    for index, value in enumerate(interface_id):
        interface_dict[value] = index
    categories = [{'name': '任务流' + str(category) if category else '虚拟节点'} for category in interface_id]
    for node in nodes:
        node['category'] = interface_dict[node['category']]
    return {'nodes': nodes, 'links': links, 'categories': categories}


def execute_nodes_graph(job_nodes):
    """执行节点依赖"""
    if not job_nodes:
        return {'nodes': [], 'links': [], 'categories': []}
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
    symbol_size = log(10, len(job_nodes)) * 40 if len(job_nodes) > 1 else 30
    horizontal_margin = 20 * (1 + 1 / len(job_nodes)) if len(job_nodes) > 1 else 10
    vertical_margin = len(job_nodes)
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
                'symbolSize': symbol_size,
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
    max_layer = max(j['level'] for i, j in nodes.items())
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
    for level in range(max_layer + 1):
        # x坐标
        layer = layers[level]
        ranges = {
            'start': 0,
            'end': 0,
            'width': horizontal_margin,
            'x': 0
        }
        # 遍历每层所有节点
        for node_index in range(1, len(layer)):
            ranges['end'] = node_index
            ranges['width'] += horizontal_margin
        # 多个节点
        if ranges['start'] != ranges['end']:
            # 负数折半
            left = -ranges['width'] / 2
            for j in range(0, len(layer)):
                layer[j]['x'] = left + horizontal_margin / 2
                left += horizontal_margin
    # y坐标
    for level in range(max_layer + 1):
        for node in layers[level]:
            node['y'] = vertical_margin * level
    # 5.数据整理
    for _, node in nodes.items():
        node.pop('in')
        node.pop('out')
    # 按层级排序
    nodes = [j for i, j in nodes.items()]
    nodes.sort(key=lambda x: x['level'])
    # 6.节点任务流分类
    categories = [
        {'name': '等待依赖任务完成'},
        {'name': '待运行'},
        {'name': '运行中'},
        {'name': '成功'},
        {'name': '失败'},
        {'name': '外部节点'},
        {'name': '虚拟节点'}

    ]
    return {'nodes': nodes, 'links': links, 'categories': categories}
