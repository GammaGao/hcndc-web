# !/usr/bin/env python
# -*- coding: utf-8 -*-

from models.schedule import ScheduleModel
from models.execute import ExecuteModel
from models.interface import InterfaceModel
from configs import db
from operations.job import JobOperation


def generate_interface_dag_by_dispatch(dispatch_id):
    """
    获取执行任务流前后依赖关系
    0.预处理: 任务流详情和全部依赖关系, id统一为字符串
    1.构造节点: 节点获取一层父节点, 递归子节点
    2.计算节点层级: 找出开始节点(无入度), 入度和当前节点最大层级+1为当前节点层级, 队列中添加出度
    :param dispatch_id: 调度id
    :return: 任务流依赖关系
    """

    def get_context_node(node_id, is_parent=True):
        """获取上下文节点"""
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
                    'in': {node_id},
                    'out': set(),
                    'level': 0
                }
                # 递归节点
                get_context_node(node_item['interface_id'])

    # 任务流详情
    detail = InterfaceModel.get_interface_detail_by_dispatch_id(db.etl_db, dispatch_id)
    # 前后置依赖
    parent = InterfaceModel.get_interface_parent_all(db.etl_db)
    child = InterfaceModel.get_interface_child_all(db.etl_db)
    nodes = {}
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
        'is_start': True,
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
    return nodes


def generate_job_dag_by_interface(interface_id):
    """
    生成任务流中执行任务数据结构
    :param interface_id: 任务流id
    :return:
    """
    # 获取调度任务
    nodes = {}
    job_list = ScheduleModel.get_run_job_detail(db.etl_db, interface_id)
    for job in job_list:
        # 获取任务参数
        params_value = JobOperation.get_job_params(db.etl_db, job['job_id'])
        nodes[job['job_id']] = {
            'id': job['job_id'],
            'in': [int(i) for i in job['prep_id'].split(',')] if job['prep_id'] else [],
            'out': [],
            'server_host': job['server_host'],
            'server_dir': job['server_dir'],
            'server_script': job['server_script'],
            'params_value': params_value,
            'return_code': job['return_code'],
            'position': 1,
            'run_period': job['run_period'],
            'level': 0
        }
    # 获取外部依赖
    in_ids = []
    all_ids = []
    for job in job_list:
        in_ids.append(job['job_id'])
        if job['prep_id']:
            all_ids.extend(int(i) for i in job['prep_id'].split(','))

    for prep_id in set(all_ids) - set(in_ids):
        prep_job = ScheduleModel.get_prep_job_detail(db.etl_db, prep_id)
        nodes[prep_job['job_id']] = {
            'id': prep_job['job_id'],
            'in': [],
            'out': [],
            'position': 2,
            'run_period': prep_job['run_period'],
            'level': 0
        }
    # 任务状态
    source = []
    for _, job in nodes.items():
        status = 'preparing'
        for prep_id in job['in']:
            # 任务依赖未满足
            if job['run_period'] and job['run_period'] > nodes[prep_id]['run_period']:
                status = 'ready'
                break
        # 外部依赖
        if job['position'] == 2:
            status = ''
        job['status'] = status
        source.append(job)
    # 出度
    for node in source:
        for from_id in node['in']:
            from_node = nodes[from_id]
            from_node['out'].append(node['id'])
    # 层级数组
    node_queue = []
    # 找出开始节点(外部节点亦为开始节点)
    for node in source:
        if not node['in']:
            node_queue.append(node)
    # 计算层级
    index = 0
    while index < len(node_queue):
        node = node_queue[index]
        if node['in']:
            level = 0
            for key in node['in']:
                level = max(level, nodes[key]['level'])
            node['level'] = level + 1
        else:
            # 初始层
            node['level'] = 0
        # 添加出度
        for out_id in node['out']:
            if out_id not in map(lambda x: x['id'], node_queue):
                node_queue.append(nodes[out_id])
        index += 1

    # 按层级排序
    source.sort(key=lambda x: x['level'])
    return {'nodes': nodes, 'source': source}


def get_job_dag_by_exec_id(exec_id):
    """获取可执行任务数据结构"""
    # 获取执行任务(执行状态为运行中,失败[执行中存在错误],就绪)
    source = ExecuteModel.get_execute_jobs(db.etl_db, exec_id)
    for job in source:
        # 入度
        if not job['in_degree']:
            job['in_degree'] = []
        else:
            job['in_degree'] = [int(i) for i in job['in_degree'].split(',')]
        # 出度
        if not job['out_degree']:
            job['out_degree'] = []
        else:
            job['out_degree'] = [int(i) for i in job['out_degree'].split(',')]
    # 按层级排序
    source.sort(key=lambda x: x['level'])
    nodes = {}
    for job in source:
        nodes[job['job_id']] = job
    return {'nodes': nodes, 'source': source}


def get_interface_dag_by_exec_id(exec_id):
    """获取可执行任务流数据结构"""
    source = ExecuteModel.get_exec_interface_by_exec_id(db.etl_db, exec_id)
    for item in source:
        # 入度
        if not item['in_degree']:
            item['in_degree'] = []
        else:
            item['in_degree'] = [int(i) for i in item['in_degree'].split(',')]
        # 出度
        if not item['out_degree']:
            item['out_degree'] = []
        else:
            item['out_degree'] = [int(i) for i in item['out_degree'].split(',')]
    # 按层级排序
    source.sort(key=lambda x: x['level'])
    nodes = {}
    for item in source:
        nodes[item['interface_id']] = item


def get_all_jobs_dag_by_exec_id(exec_id):
    """获取所有执行任务数据结构"""
    # 获取执行所有任务
    source = ExecuteModel.get_execute_jobs_all(db.etl_db, exec_id)
    for job in source:
        # 入度
        if not job['in_degree']:
            job['in_degree'] = []
        else:
            job['in_degree'] = [int(i) for i in job['in_degree'].split(',')]
        # 出度
        if not job['out_degree']:
            job['out_degree'] = []
        else:
            job['out_degree'] = [int(i) for i in job['out_degree'].split(',')]
    # 按层级排序
    source.sort(key=lambda x: x['level'])
    nodes = {}
    for job in source:
        nodes[job['job_id']] = job
    return {'nodes': nodes, 'source': source}
