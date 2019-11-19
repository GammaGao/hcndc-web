# !/usr/bin/env python
# -*- coding: utf-8 -*-

from math import log

from server.decorators import make_decorator


class InterfaceFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """任务流列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_interface_graph_data(job_nodes):
        """获取任务流拓扑结构"""
        if not job_nodes:
            return {'status': 200, 'msg': '成功', 'data': {'nodes': [], 'links': [], 'categories': []}}, 200
        nodes = {}
        links = []
        layers = {}
        symbolSize = log(10, len(job_nodes)) * 40 if len(job_nodes) > 1 else 30
        horizontalMargin = 20 * (1 + 1 / len(job_nodes)) if len(job_nodes) > 1 else 10
        verticalMargin = len(job_nodes)
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
                        'symbolSize': symbolSize,
                        'x': 0,
                        'y': 0,
                        'label': {'show': True},
                        'category': job['interface_id'],
                        'in': set(),
                        'out': set(),
                        'level': 0
                    }
                # 入度
                if job['prep_id']:
                    nodes[job['job_id']]['in'].add(job['prep_id'])
            # 依赖节点
            if job['prep_id'] and job['prep_interface_id']:
                if job['prep_id'] not in nodes:
                    nodes[job['prep_id']] = {
                        'id': job['prep_id'],
                        'name': job['prep_name'],
                        'itemStyle': None,
                        'symbolSize': symbolSize,
                        'x': 0,
                        'y': 0,
                        'label': {'show': True},
                        'category': job['prep_interface_id'],
                        'in': set(),
                        'out': set(),
                        'level': 0
                    }
                # 出度
                if job['job_id']:
                    nodes[job['prep_id']]['out'].add(job['job_id'])

        # 2.计算节点层级
        nodeQueue = []
        # 找出开始节点
        for _, node in nodes.items():
            if not node['in']:
                nodeQueue.append(node)
        # 计算层级
        index = 0
        while index < len(nodeQueue):
            node = nodeQueue[index]
            if node['in']:
                level = 0
                for key in node['in']:
                    level = max(level, nodes[key]['level'])
                node['level'] = level + 1

            # 添加队列
            for out_id in node['out']:
                if out_id not in map(lambda x: x['id'], nodeQueue):
                    nodeQueue.append(nodes[out_id])
            index += 1
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
        # 6.节点任务流分类
        interface_id = set(node['category'] for node in nodes)
        interface_dict = {}
        for index, value in enumerate(interface_id):
            interface_dict[value] = index
        categories = [{'name': '任务流' + str(category) if category else '虚拟节点'} for category in interface_id]
        for node in nodes:
            node['category'] = interface_dict[node['category']]
        return {'status': 200, 'msg': '成功', 'data': {'nodes': nodes, 'links': links, 'categories': categories}}, 200

    @staticmethod
    @make_decorator
    def filter_interface_detail_data(detail):
        """任务流详情"""
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
