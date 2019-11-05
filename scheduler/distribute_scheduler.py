# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from scheduler.generate_dag import generate_dag_by_dispatch_id
from models.execute import ExecuteModel
from configs import db
from rpc.rpc_client import Connection
from configs import config, log


def get_dispatch_job(dispatch_id):
    """获取调度任务"""
    result = generate_dag_by_dispatch_id(dispatch_id)
    source = result['source']
    # 工作流中任务为空, 则视调度已完成
    if not source:
        # 修改调度执行表账期
        run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        ExecuteModel.update_interface_account_by_dispatch_id(db.etl_db, dispatch_id, run_time)
        log.info('工作流中任务为空: 调度id: %s' % dispatch_id)
        # 添加执行表-完成状态
        ExecuteModel.add_execute_success(db.etl_db, 1, dispatch_id)
        return
    # 添加相关信息至数据库
    exec_id = add_exec_record(dispatch_id, source)
    # rpc分发任务
    for job in source:
        if job['level'] == 0 and job['position'] == 1:
            client = Connection(job['server_host'], config.exec.port)
            try:
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
                log.error('rpc连接异常: host: %s, port: %s' % (job['server_host'], config.exec.port), exc_info=True)


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
            'params': ','.join(i['params']),
            'server_script': i.get('server_script', ''),
            'position': i['position'],
            'return_code': i['return_code'],
            'level': i['level'],
            'status': i['status'],
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
    # 添加执行详情表
    if data:
        ExecuteModel.add_execute_detail(db.etl_db, data)
    return exec_id
