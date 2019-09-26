# !/usr/bin/env python
# -*- coding: utf-8 -*-

from models.schedule import ScheduleModel
from models.execute import ExecuteModel
from configs import db


def generate_dag_by_dispatch_id(dispatch_id):
    """根据调度id生成dag模型"""
    # 接口属性
    dispatch_model = ScheduleModel.get_interface_detail(db.etl_db, dispatch_id)
    if not dispatch_model:
        return {}
    # 获取调度任务
    nodes = {}
    job_list = ScheduleModel.get_run_job_detail(db.etl_db, dispatch_model['interface_id'])

    for job in job_list:
        nodes[job['job_id']] = {
            'id': job['job_id'],
            'in': [int(i) for i in job['prep_id'].split(',')] if job['prep_id'] else [],
            'out': [],
            'server_host': job['server_host'],
            'server_dir': job['server_dir'],
            'server_script': job['server_script'],
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
    nodeQueue = []
    # 找出开始节点(外部节点亦为开始节点)
    for node in source:
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
        else:
            # 初始层
            node['level'] = 0
        # 添加出度
        for out_id in node['out']:
            if out_id not in map(lambda x: x['id'], nodeQueue):
                nodeQueue.append(nodes[out_id])
        index += 1

    # 按层级排序
    source.sort(key=lambda x: x['level'])
    return {'nodes': nodes, 'source': source}


def generate_dag_by_exec_id(exec_id):
    """根据执行id生成dag模型"""
    # 获取执行任务
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
