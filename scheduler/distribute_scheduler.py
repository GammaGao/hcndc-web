# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from scheduler.generate_dag import generate_job_dag_by_interface, generate_interface_dag_by_dispatch
from models.execute import ExecuteModel
from models.schedule import ScheduleModel
from configs import db
from configs import config, log
from conn.mysql_lock import MysqlLock
from operations.execute import continue_execute_interface, rpc_push_job


def get_dispatch_job(dispatch_id, exec_type=1, run_date='', date_format='', is_after=1):
    """
    调度执行开始方法
    1.生成所有任务流依赖(根据is_after参数, 确定递归深度), 生成任务流所有任务详情
    2.添加执行主表[运行中], 执行任务流[就绪], 修改执行详情表[待运行]
    3.获取初始任务流如果执行任务流为空, 则修改执行任务状态[成功](修改执行流账期, 修改执行任务流表记录);
      执行任务流非空, 执行任务流状态[运行中], 修改执行详情表状态[运行中]
    4.RPC分发初始任务流中level=0的执行任务, 替换参数变量$date为T-1日期;
      如果RPC异常, 修改执行详情表状态[失败], 执行任务流状态[失败], 执行主表状态[失败]
    5.如果存在执行任务流为空, 获取下一个可执行任务流
    :param dispatch_id: 调度id
    :param exec_type: 执行类型: 1.自动, 2.手动
    :param run_date: 手动传入$date日期
    :param date_format: $date日期格式
    :param is_after: 是否触发后置任务流
    :return: None
    """
    # 传入日期
    _date = ''
    if run_date and date_format:
        _date = time.strftime(date_format, time.strptime(run_date, '%Y-%m-%d'))
    # 获取执行任务流前后依赖关系
    interface_nodes = generate_interface_dag_by_dispatch(dispatch_id, is_after)
    if not interface_nodes:
        return
    # 获取所有任务流的任务详情
    job_nodes = {}
    for _, item in interface_nodes.items():
        jobs = generate_job_dag_by_interface(item['id'])
        job_nodes[item['id']] = jobs
    # 添加执行主表, 任务流表, 任务表至数据库
    exec_id = add_exec_record(dispatch_id, interface_nodes, job_nodes, exec_type, _date, is_after)
    # 初始任务流
    start_interface = [_ for _, item in interface_nodes.items() if item['level'] == 0]
    # 开始执行初始任务流中的任务
    flag = False
    for curr_interface in start_interface:
        start_jobs = job_nodes[curr_interface]
        # 任务流中任务为空, 则视调度已完成
        if not start_jobs:
            flag = True
            # 修改调度执行表账期
            run_time = time.strftime('%Y-%m-%d', time.localtime())
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                ExecuteModel.update_interface_run_time(db.etl_db, curr_interface, run_time)
            log.info('任务流中任务为空: 调度id: %s, 执行id: %s, 任务流id: %s' % (dispatch_id, exec_id, curr_interface))
            # 修改执行任务流[成功]
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, curr_interface, 0)
        else:
            # 修改执行任务流[运行中]
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, curr_interface, 1)
            # rpc分发任务
            for job in start_jobs:
                if job['level'] == 0:
                    # 修改执行详情表状态[运行中]
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                        ScheduleModel.update_exec_job_status(db.etl_db, exec_id, curr_interface, job['id'], 'running')
                    log.info('分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (exec_id, curr_interface, job['id']))
                    rpc_push_job(exec_id, curr_interface, job['id'], job['server_host'], config.exec.port,
                                 ','.join(job['params_value']), job['server_dir'], job['server_script'],
                                 job['return_code'], job['status'], run_date=_date)
    # 继续下一个任务流
    if flag:
        next_jobs = continue_execute_interface(exec_id, exec_type=exec_type)
        for interface_id, item in next_jobs.items():
            for job_id in set(item['job_id']):
                log.info('分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (exec_id, interface_id, job_id))
                nodes = item['nodes']
                rpc_push_job(exec_id, interface_id, job_id, nodes[job_id]['server_host'],
                             config.exec.port, nodes[job_id]['params_value'],
                             nodes[job_id]['server_dir'], nodes[job_id]['server_script'],
                             nodes[job_id]['return_code'], nodes[job_id]['status'], run_date=_date)


def add_exec_record(dispatch_id, interface_nodes, job_nodes, exec_type=1, run_date='', is_after=1):
    """添加执行表和执行详情表"""
    # 添加执行表
    exec_id = ExecuteModel.add_execute(db.etl_db, exec_type, dispatch_id, run_date, is_after)
    interface_arr = []
    for _, item in interface_nodes.items():
        interface_arr.append({
            'exec_id': exec_id,
            'interface_id': item['id'],
            'in_degree': ','.join(item['in']) if item['in'] else '',
            'out_degree': ','.join(item['out']) if item['out'] else '',
            'level': item['level'],
            'status': 3,
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
    ExecuteModel.add_exec_interface(db.etl_db, interface_arr) if interface_arr else None
    data = []
    for _, item in job_nodes.items():
        for job in item:
            data.append({
                'exec_id': exec_id,
                'interface_id': _,
                'job_id': job['id'],
                'in_degree': ','.join(str(j) for j in job['in']) if job['in'] else '',
                'out_degree': ','.join(str(j) for j in job['out']) if job['out'] else '',
                'server_host': job.get('server_host', ''),
                'server_dir': job.get('server_dir', ''),
                'params_value': ','.join(job.get('params', [])),
                'server_script': job.get('server_script', ''),
                'position': job['position'],
                'return_code': job.get('return_code', 0),
                'level': job.get('level', 0),
                'status': job.get('status', 'preparing'),
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
    # 添加执行详情表
    ExecuteModel.add_execute_detail(db.etl_db, data) if data else None
    return exec_id
