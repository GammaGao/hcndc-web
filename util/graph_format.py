# !/usr/bin/env python
# -*- coding: utf-8 -*-

from math import log


def job_nodes_graph(job_nodes):
    """任务节点依赖"""
    if not job_nodes:
        return {'nodes': [], 'links': [], 'categories': []}
    nodes = {}
    links = []
    # 层级对象
    layers = {}
    # 节点图标大小
    symbol_size = log(10, len(job_nodes)) * 40 if len(job_nodes) > 1 else 30
    # x坐标间距
    horizontal_margin = 20 * (1 + 1 / len(job_nodes)) if len(job_nodes) > 1 else 10
    # y坐标间距
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
        # 该层所有节点
        layer = layers[level]
        # x坐标
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


def interface_local_graph(detail, parent, child):
    """任务流局部拓扑"""
    nodes = {}
    links = []
    # 层级对象
    layers = {}
    # 节点图标大小
    length = len(parent) + len(child)
    symbol_size = log(10, length) * 40 if length > 1 else 30
    # x坐标间距
    horizontal_margin = 20 * (1 + 1 / length) if length > 1 else 10
    # y坐标间距
    vertical_margin = length
    # 1.构造节点: id统一为字符串
    # 父节点
    for item in parent:
        item['interface_id'] = str(item['interface_id'])
        item['parent_id'] = str(item['parent_id']) if item['parent_id'] else None
        nodes[item['parent_id']] = {
            'id': item['parent_id'],
            'name': item['parent_name'],
            'itemStyle': None,
            'symbolSize': symbol_size,
            'x': 0,
            'y': 0,
            'label': {'show': True},
            'category': item['parent_id'],
            'level': 0
        }
    # 当前节点
    nodes[detail['interface_id']] = {
        'id': str(detail['interface_id']),
        'name': detail['interface_name'],
        'itemStyle': None,
        'symbolSize': symbol_size,
        'x': 0,
        'y': 0,
        'label': {'show': True},
        'category': str(detail['interface_id']),
        'level': 1
    }
    # 子节点
    for item in child:
        item['interface_id'] = str(item['interface_id'])
        item['child_id'] = str(item['child_id']) if item['child_id'] else None
        nodes[item['child_id']] = {
            'id': item['child_id'],
            'name': item['child_name'],
            'itemStyle': None,
            'symbolSize': symbol_size,
            'x': 0,
            'y': 0,
            'label': {'show': True},
            'category': item['child_id'],
            'level': 2
        }
    # 2.构造连线
    for item in parent:
        links.append({'source': item['parent_id'], 'target': item['interface_id']})
    for item in child:
        links.append({'source': item['interface_id'], 'target': item['child_id']})
    # 3.填充层级对象
    for _, node in nodes.items():
        if node['level'] not in layers:
            layers[node['level']] = []
        layers[node['level']].append(node)
    # 3.计算坐标
    for level in range(3):
        # 该层所有节点
        layer = layers.get(level, [])
        # x坐标
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
    for level in range(3):
        for node in layers.get(level, []):
            node['y'] = vertical_margin * level
    # 5.数据整理
    # 按层级排序
    nodes = [j for i, j in nodes.items()]
    nodes.sort(key=lambda x: x['level'])
    # 6.节点任务流分类
    interface_id = list(set(node['category'] for node in nodes))
    interface_id.sort(key=lambda x: int(x))
    # 当前任务流id
    curr_interface_id = str(detail['interface_id'])
    interface_dict = {}
    for index, value in enumerate(interface_id):
        interface_dict[value] = index
    categories = [{
        'name': '当前任务流:' + category if category == curr_interface_id else '任务流:' + str(category) if category else '-'
    } for category in interface_id]
    for node in nodes:
        node['category'] = interface_dict[node['category']]
    return {'nodes': nodes, 'links': links, 'categories': categories}


def interface_global_graph(detail, parent, child):
    """任务流全局拓扑"""
    def get_context_node(interface_id):
        """获取上下文节点"""
        # 反向查找: 正向查找亦可
        parent_node = [i for i in child if i['child_id'] == interface_id]
        child_node = [i for i in parent if i['parent_id'] == interface_id]
        # 父节点
        for node in parent_node:
            # 添加入度
            nodes[interface_id]['in'].add(node['interface_id'])
            if node['interface_id'] not in nodes:
                # 添加节点
                nodes[node['interface_id']] = {
                    'id': node['interface_id'],
                    'name': node['interface_name'],
                    'itemStyle': None,
                    'symbolSize': symbol_size,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': node['interface_id'],
                    'in': set(),
                    'out': {interface_id},
                    'level': 0
                }
                # 递归节点
                get_context_node(node['interface_id'])
        # 子节点
        for node in child_node:
            # 添加出度
            nodes[interface_id]['out'].add(node['interface_id'])
            if node['interface_id'] not in nodes:
                # 添加节点
                nodes[node['interface_id']] = {
                    'id': node['interface_id'],
                    'name': node['interface_name'],
                    'itemStyle': None,
                    'symbolSize': symbol_size,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': node['interface_id'],
                    'in': {interface_id},
                    'out': set(),
                    'level': 0
                }
                # 递归节点
                get_context_node(node['interface_id'])

    nodes = {}
    links = []
    # 层级对象
    layers = {}
    # 节点图标大小
    length = len(parent) + len(child)
    symbol_size = log(10, length) * 40 if length > 1 else 30
    # x坐标间距
    horizontal_margin = 20 * (1 + 1 / length) if length > 1 else 10
    # y坐标间距
    vertical_margin = length
    # 0.预处理: id统一为字符串
    # 父节点
    for item in parent:
        item['interface_id'] = str(item['interface_id'])
        item['parent_id'] = str(item['parent_id']) if item['parent_id'] else None
    # 当前节点
    detail['interface_id'] = str(detail['interface_id'])
    # 子节点
    for item in child:
        item['interface_id'] = str(item['interface_id'])
        item['child_id'] = str(item['child_id']) if item['child_id'] else None
    # 1.构造节点
    # 当前节点
    nodes[detail['interface_id']] = {
        'id': detail['interface_id'],
        'name': detail['interface_name'],
        'itemStyle': None,
        'symbolSize': symbol_size,
        'x': 0,
        'y': 0,
        'label': {'show': True},
        'category': detail['interface_id'],
        'in': set(),
        'out': set(),
        'level': 0
    }
    # 节点上下文递归
    get_context_node(detail['interface_id'])
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
    for _, node in nodes.items():
        for out in node['out']:
            links.append({'source': node['id'], 'target': out})
    # 4.计算坐标
    for level in range(max_layer + 1):
        # 该层所有节点
        layer = layers[level]
        # x坐标
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
    interface_id = list(set(node['category'] for node in nodes))
    interface_id.sort(key=lambda x: int(x))
    # 当前任务流id
    curr_interface_id = str(detail['interface_id'])
    interface_dict = {}
    for index, value in enumerate(interface_id):
        interface_dict[value] = index
    categories = [{
        'name': '当前任务流:' + category if category == curr_interface_id else '任务流:' + str(category) if category else '-'
    } for category in interface_id]
    for node in nodes:
        node['category'] = interface_dict[node['category']]
    return {'nodes': nodes, 'links': links, 'categories': categories}
