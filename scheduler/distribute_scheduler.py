# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from scheduler.generate_dag import generate_dag_by_dispatch_id
from models.execute import ExecuteModel
from models.schedule import ScheduleModel
from configs import db
from rpc.rpc_client import Connection
from configs import config, log
from conn.mysql_lock import MysqlLock


def get_dispatch_job(dispatch_id):
    """执行调度主方法-获取调度任务"""
    # 获取任务流参数
    result = generate_dag_by_dispatch_id(dispatch_id)
    source = result['source']
    # 任务流中任务为空, 则视调度已完成
    if not source:
        # 修改调度执行表账期
        run_time = time.strftime('%Y-%m-%d', time.localtime())
        ExecuteModel.update_interface_account_by_dispatch_id(db.etl_db, dispatch_id, run_time)
        log.info('任务流中任务为空: 调度id: %s' % dispatch_id)
        # 添加执行表-完成状态
        ExecuteModel.add_execute_success(db.etl_db, 1, dispatch_id)
        return
    # 添加执行主表和详情表至数据库
    exec_id = add_exec_record(dispatch_id, source)
    # rpc分发任务
    for job in source:
        if job['level'] == 0 and job['position'] == 1:
            try:
                client = Connection(job['server_host'], config.exec.port)
                client.rpc.execute(
                    exec_id=exec_id,
                    job_id=job['id'],
                    server_dir=job['server_dir'],
                    server_script=job['server_script'],
                    return_code=job['return_code'],
                    params=job['params'],
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
                    # 修改执行主表状态[失败]
                    ExecuteModel.update_execute_status(db.etl_db, exec_id, -1)
                log.error(err_msg, exc_info=True)
                return


def add_exec_record(dispatch_id, source):
    # 添加执行表
    exec_id = ExecuteModel.add_execute(db.etl_db, 1, dispatch_id)
    data = []
    for i in source:
        data.append({
            'exec_id': exec_id,
            'job_id': i['id'],
            'in_degree': ','.join(str(j) for j in i['in']),
            'out_degree': ','.join(str(j) for j in i['out']),
            'server_host': i.get('server_host', ''),
            'server_dir': i.get('server_dir', ''),
            'params': ','.join(i.get('params', [])),
            'server_script': i.get('server_script', ''),
            'position': i['position'],
            'return_code': i.get('return_code', 0),
            'level': i.get('level', 0),
            'status': i.get('status', 'preparing'),
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
    # 添加执行详情表
    if data:
        ExecuteModel.add_execute_detail(db.etl_db, data)
    return exec_id
