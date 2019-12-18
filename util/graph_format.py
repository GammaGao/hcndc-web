# !/usr/bin/env python
# -*- coding: utf-8 -*-

from math import log


def job_nodes_graph(job_nodes, current_interface):
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
            links.append({'source': job['prep_id'], 'target': job['job_id']})
            # 不相邻层级
            if abs(nodes[job['job_id']]['level'] - nodes[job['prep_id']]['level']) != 1:
                # 计算相差层级数
                min_level = min(nodes[job['job_id']]['level'], nodes[job['prep_id']]['level']) + 1
                max_level = max(nodes[job['job_id']]['level'], nodes[job['prep_id']]['level'])
                for transit_level in range(min_level, max_level):
                    # 添加过渡节点
                    transit_id = '%s>%s>%s' % (job['prep_id'], job['job_id'], str(transit_level))
                    layers[transit_level].append({
                        'id': transit_id,
                        'x': 0,
                        'y': 0
                    })
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
    categories = [
        {'name': '当前任务流'},
        {'name': '其他任务流'}
    ]
    for node in nodes:
        node['category'] = int(not node['category'] == current_interface)
    return {'nodes': nodes, 'links': links, 'categories': categories}


def execute_nodes_graph(result, data_type):
    """执行节点依赖"""
    if not result:
        return {'nodes': [], 'links': [], 'categories': []}
    remakes_interface = {
        0: '成功',
        1: '运行中',
        2: '中断',
        3: '就绪',
        -1: '失败'
    }
    remakes_jobs = {
        'ready': '等待依赖任务完成',
        'preparing': '待运行',
        'running': '运行中',
        'succeeded': '成功',
        'failed': '失败'
    }
    nodes = {}
    links = []
    layers = {}
    symbol_size = log(10, len(result)) * 40 if len(result) > 1 else 30
    horizontal_margin = 20 * (1 + 1 / len(result)) if len(result) > 1 else 10
    vertical_margin = len(result)
    # 0.预处理: id统一为字符串
    for item in result:
        item['id'] = str(item['id']) if item['id'] else None
    # 1.构造节点
    for item in result:
        # 目标节点
        if item['id'] not in nodes:
            if data_type == 1:
                remakes = remakes_interface
            else:
                remakes = remakes_jobs
            nodes[item['id']] = {
                'id': item['id'],
                'name': item['name'],
                'itemStyle': None,
                'symbolSize': symbol_size,
                'x': 0,
                'y': 0,
                'label': {'show': True},
                'category': remakes.get(item['status'], '其他'),
                'in': item['in_degree'].split(',') if item['in_degree'] else [],
                'out': item['out_degree'].split(',') if item['out_degree'] else [],
                'level': item['level']
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
    for item in result:
        # 有依赖关系
        in_degree = item['in_degree'].split(',') if item['in_degree'] else []
        for source_node in in_degree:
            links.append({'source': source_node, 'target': item['id']})
            # 不相邻层级
            if abs(nodes[item['id']]['level'] - nodes[source_node]['level']) != 1:
                # 计算相差层级数
                min_level = min(nodes[item['id']]['level'], nodes[source_node]['level']) + 1
                max_level = max(nodes[item['id']]['level'], nodes[source_node]['level'])
                for transit_level in range(min_level, max_level):
                    # 添加过渡节点
                    transit_id = '%s>%s>%s' % (source_node, item['id'], str(transit_level))
                    layers[transit_level].append({
                        'id': transit_id,
                        'x': 0,
                        'y': 0
                    })
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
    if data_type == 1:
        categories = [
            {'name': '成功'},
            {'name': '运行中'},
            {'name': '中断'},
            {'name': '就绪'},
            {'name': '失败'},
            {'name': '其他'}
        ]
        color = ['#5CB85C', '#2fafcc', '#D9534F', '#F19153', '#ff5722', '#1E9FFF']
    else:
        categories = [
            {'name': '等待依赖任务完成'},
            {'name': '待运行'},
            {'name': '运行中'},
            {'name': '成功'},
            {'name': '失败'},
            {'name': '其他'}
        ]
        color = ['#FFB800', '#F19153', '#3398CC', '#5CB85C', '#D9534F', '#1E9FFF']
    return {'nodes': nodes, 'links': links, 'categories': categories, 'color': color}


def interface_local_graph(detail, parent, child):
    """任务流局部拓扑"""

    def get_context_node(node_id, is_parent=True):
        """获取上下文节点"""
        # 获取父子节点
        parent_node = [i for i in child if i['child_id'] == node_id]
        child_node = [i for i in parent if i['parent_id'] == node_id]
        # 父节点(局部拓扑情况下, 所有节点的父节点无需递归, 初始节点不添加父节点)
        if is_parent:
            for node_item in parent_node:
                # 添加入度
                nodes[node_id]['in'].add(node_item['interface_id'])
                if node_item['interface_id'] not in nodes:
                    # 添加节点
                    nodes[node_item['interface_id']] = {
                        'id': node_item['interface_id'],
                        'name': node_item['interface_name'],
                        'itemStyle': None,
                        'symbolSize': symbol_size,
                        'x': 0,
                        'y': 0,
                        'label': {'show': True},
                        'category': node_item['interface_id'],
                        'in': set(),
                        'out': {node_id},
                        'level': 0
                    }
        # 子节点
        for node_item in child_node:
            # 添加出度
            nodes[node_id]['out'].add(node_item['interface_id'])
            if node_item['interface_id'] not in nodes:
                # 添加节点
                nodes[node_item['interface_id']] = {
                    'id': node_item['interface_id'],
                    'name': node_item['interface_name'],
                    'itemStyle': None,
                    'symbolSize': symbol_size,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': node_item['interface_id'],
                    'in': {node_id},
                    'out': set(),
                    'level': 0
                }
                # 递归节点
                get_context_node(node_item['interface_id'])

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
    get_context_node(detail['interface_id'], is_parent=False)
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
    for _id, node in nodes.items():
        for out in node['out']:
            links.append({'source': _id, 'target': out})
            # 不相邻层级
            if abs(node['level'] - nodes[out]['level']) != 1:
                # 计算相差层级数
                min_level = min(node['level'], nodes[out]['level']) + 1
                max_level = max(node['level'], nodes[out]['level'])
                for transit_level in range(min_level, max_level):
                    # 添加过渡节点
                    transit_id = '%s>%s>%s' % (_id, nodes[out]['id'], str(transit_level))
                    layers[transit_level].append({
                        'id': transit_id,
                        'x': 0,
                        'y': 0
                    })
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
    categories = [
        {'name': '当前任务流'},
        {'name': '其他任务流'}
    ]
    for node in nodes:
        if node['id'] == str(detail['interface_id']):
            node['category'] = 0
        else:
            node['category'] = 1
    return {'nodes': nodes, 'links': links, 'categories': categories}


def interface_global_graph(detail, parent, child):
    """任务流全局拓扑"""

    def get_context_node(node_id):
        """获取上下文节点"""
        # 获取父子节点
        parent_node = [i for i in child if i['child_id'] == node_id]
        child_node = [i for i in parent if i['parent_id'] == node_id]
        # 父节点
        for node_item in parent_node:
            # 添加入度
            nodes[node_id]['in'].add(node_item['interface_id'])
            if node_item['interface_id'] not in nodes:
                # 添加节点
                nodes[node_item['interface_id']] = {
                    'id': node_item['interface_id'],
                    'name': node_item['interface_name'],
                    'itemStyle': None,
                    'symbolSize': symbol_size,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': node_item['interface_id'],
                    'in': set(),
                    'out': {node_id},
                    'level': 0
                }
                # 递归节点
                get_context_node(node_item['interface_id'])
        # 子节点
        for node_item in child_node:
            # 添加出度
            nodes[node_id]['out'].add(node_item['interface_id'])
            if node_item['interface_id'] not in nodes:
                # 添加节点
                nodes[node_item['interface_id']] = {
                    'id': node_item['interface_id'],
                    'name': node_item['interface_name'],
                    'itemStyle': None,
                    'symbolSize': symbol_size,
                    'x': 0,
                    'y': 0,
                    'label': {'show': True},
                    'category': node_item['interface_id'],
                    'in': {node_id},
                    'out': set(),
                    'level': 0
                }
                # 递归节点
                get_context_node(node_item['interface_id'])

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
    for _id, node in nodes.items():
        for out in node['out']:
            links.append({'source': _id, 'target': out})
            # 不相邻层级
            if abs(node['level'] - nodes[out]['level']) != 1:
                min_level = min(node['level'], nodes[out]['level']) + 1
                max_level = max(node['level'], nodes[out]['level'])
                for transit_level in range(min_level, max_level):
                    # 添加过渡节点
                    transit_id = '%s>%s>%s' % (_id, nodes[out]['id'], str(transit_level))
                    layers[transit_level].append({
                        'id': transit_id,
                        'x': 0,
                        'y': 0
                    })
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
    categories = [
        {'name': '当前任务流'},
        {'name': '其他任务流'}
    ]
    for node in nodes:
        if node['id'] == str(detail['interface_id']):
            node['category'] = 0
        else:
            node['category'] = 1
    return {'nodes': nodes, 'links': links, 'categories': categories}
