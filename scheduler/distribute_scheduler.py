# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from scheduler.generate_dag import generate_job_dag_by_interface, generate_interface_dag_by_dispatch
from models.execute import ExecuteModel
from models.schedule import ScheduleModel
from configs import db
from rpc.rpc_client import Connection
from configs import config, log
from conn.mysql_lock import MysqlLock


def get_dispatch_job(dispatch_id):
    """
    调度执行开始方法
    1.获取前置任务流, 初始任务流所有任务参数
    2.添加执行主表, 调度任务流和所有任务表, 如果调度任务流为空, 则视调度已完成(修改执行流账期, 添加执行主表记录)
    3.RPC分发初始任务流中level=0任务, 如果RPC异常, 修改任务详情日志状态[失败], 任务流日志状态[失败], 执行主表状态[失败]
    :param dispatch_id: 调度id
    :return: None
    """
    # 获取执行任务流前后依赖关系
    interface_nodes = generate_interface_dag_by_dispatch(dispatch_id)
    if not interface_nodes:
        return
    # 获取所有任务流的任务详情
    job_nodes = {}
    start_node = ''
    for _, item in interface_nodes.items():
        result = generate_job_dag_by_interface(item['id'])
        job_nodes[item['id']] = result
        if item.get('is_start', False):
            start_node = item['id']
    # 添加执行主表, 任务流表, 任务表至数据库
    exec_id = add_exec_record(dispatch_id, interface_nodes, job_nodes)
    # 开始执行初始任务流中的任务
    source = job_nodes[start_node]['source']
    # 任务流中任务为空, 则视调度已完成
    if not source:
        # 修改调度执行表账期
        run_time = time.strftime('%Y-%m-%d', time.localtime())
        ExecuteModel.update_interface_account_by_dispatch_id(db.etl_db, dispatch_id, run_time)
        log.info('任务流中任务为空: 调度id: %s' % dispatch_id)
        # 修改执行任务流-完成状态
        ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, int(start_node), 0)
        # TODO 继续下一个任务流
        return
    # rpc分发任务
    for job in source:
        if job['level'] == 0 and job['position'] == 1:
            try:
                # 任务参数中数据日期变量替换
                run_time = time.strftime('%Y-%m-%d', time.localtime())
                # RPC分发任务
                client = Connection(job['server_host'], config.exec.port)
                client.rpc.execute(
                    exec_id=exec_id,
                    job_id=job['id'],
                    server_dir=job['server_dir'],
                    server_script=job['server_script'],
                    return_code=job['return_code'],
                    params=[item if item != '$date' else run_time for item in job['params_value']],
                    status=job['status']
                )
                log.info('分发任务: 执行id: %s, 任务id: %s' % (exec_id, job['id']))
            except:
                err_msg = 'rpc连接异常: host: %s, port: %s' % (job['server_host'], config.exec.port)
                # 添加执行任务详情日志
                ScheduleModel.add_exec_detail_job(db.etl_db, exec_id, job['id'], 'ERROR', job['server_dir'],
                                                  job['server_script'], err_msg, 3)
                # 修改数据库, 分布式锁
                with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                    # 修改执行详情表状态[失败]
                    ScheduleModel.update_exec_job_status(db.etl_db, exec_id, job['id'], 'failed')
                    # 修改执行任务流状态[失败]
                    ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, int(start_node), -1)
                    # 修改执行主表状态[失败]
                    ExecuteModel.update_execute_status(db.etl_db, exec_id, -1)
                log.error(err_msg, exc_info=True)
                return


def add_exec_record(dispatch_id, interface_nodes, job_nodes, exec_type=1):
    """添加执行表和执行详情表"""
    # 添加执行表
    exec_id = ExecuteModel.add_execute(db.etl_db, exec_type, dispatch_id)
    interface_arr = []
    for _, item in interface_nodes.items():
        interface_arr.append({
            'exec_id': exec_id,
            'interface_id': item['id'],
            'in_degree': ','.join(item['in']) if item['in'] else '',
            'out_degree': ','.join(item['out']) if item['out'] else '',
            'level': item['level'],
            'status': 1 if item.get('is_start', False) else 3,
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
    ExecuteModel.add_exec_interface(db.etl_db, interface_arr) if interface_arr else None
    data = []
    for _, item in job_nodes.items():
        for job in item['source']:
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
