# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator, Response
from scheduler.generate_dag import generate_dag_by_exec_id, get_failed_jobs_by_exec_id
from rpc.rpc_client import Connection
from configs import config, log, db
from models.execute import ExecuteModel
from models.schedule import ScheduleModel
from util.msg_push import send_mail, send_dingtalk

import time


class ExecuteOperation(object):
    @staticmethod
    @make_decorator
    def get_execute_job(exec_id, status):
        """获取执行任务-推进执行流程"""
        distribute_job = []
        if status == 'succeeded':
            # 推进流程
            result = generate_dag_by_exec_id(exec_id)
            nodes = result['nodes']
            # 遍历所有节点
            for job_id in nodes:
                # 出度
                for out_id in nodes[job_id]['out_degree']:
                    flag = True
                    # 出度的入度是否成功
                    for in_id in nodes[out_id]['in_degree']:
                        # 排除外部依赖
                        if nodes[in_id]['position'] == 1 and nodes[in_id]['status'] != 'succeeded':
                            flag = False
                            break
                    if flag and nodes[out_id]['position'] == 1 and nodes[out_id]['status'] in ('preparing', 'ready'):
                        distribute_job.append(out_id)
            # 去重, 分发任务
            for job_id in set(distribute_job):
                log.info('分发任务: 执行id: %s, 任务id: %s' % (exec_id, job_id))
                try:
                    # rpc分发任务
                    client = Connection(nodes[job_id]['server_host'], config.exec.port)
                    client.rpc.execute(
                        exec_id=exec_id,
                        job_id=job_id,
                        server_dir=nodes[job_id]['server_dir'],
                        server_script=nodes[job_id]['server_script'],
                        return_code=nodes[job_id]['return_code'],
                        params=nodes[job_id]['params'],
                        status=nodes[job_id]['status']
                    )
                except:
                    err_msg = 'rpc连接异常: host: %s, port: %s' % (nodes[job_id]['server_host'], config.exec.port)
                    # 添加执行任务详情日志
                    ScheduleModel.add_exec_detail_job(db.etl_db, exec_id, job_id, 'ERROR', nodes[job_id]['server_dir'],
                                                      nodes[job_id]['server_script'], err_msg, 3)
                    # 修改执行状态
                    ScheduleModel.update_exec_job_status(db.etl_db, exec_id, job_id, 'failed')
                    ExecuteModel.update_execute_status(db.etl_db, exec_id, -1)
                    log.error(err_msg, exc_info=True)
                    return Response(distribute_job=distribute_job, msg=err_msg)

        # 查看调度执行表状态
        status_list = ExecuteModel.get_execute_detail_status(db.etl_db, exec_id)
        # 失败
        if 'failed' in status_list:
            exec_status = -1
            # 调度预警
            failed_alert = ExecuteModel.get_execute_alert(db.etl_db, exec_id, 2)
            if failed_alert['is_push'] == 0:
                # 邮件
                if failed_alert['alert_channel'] == 1:
                    send_mail(2, failed_alert)
                # 钉钉
                if failed_alert['alert_channel'] == 2:
                    send_dingtalk(2, failed_alert)
                # 修改推送状态
                ExecuteModel.update_msg_push(db.etl_db, exec_id)
        # 成功
        elif set(status_list) == {'succeeded'}:
            exec_status = 0
            # 调度预警
            succeed_alert = ExecuteModel.get_execute_alert(db.etl_db, exec_id, 1)
            # 邮件
            if succeed_alert['alert_channel'] == 1:
                send_mail(1, succeed_alert)
            # 钉钉
            if succeed_alert['alert_channel'] == 2:
                send_dingtalk(1, succeed_alert)
        # 运行中
        else:
            exec_status = 1

        # 成功时修改账期
        if exec_status == 0:
            # 修改调度执行表账期
            run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            ExecuteModel.update_interface_account_by_execute_id(db.etl_db, exec_id, run_time)

        # 修改调度执行表状态
        ExecuteModel.update_execute_status(db.etl_db, exec_id, exec_status)

        return Response(distribute_job=distribute_job, msg='成功')

    @staticmethod
    @make_decorator
    def get_execute_list(interface_id, start_time, end_time, run_status, exec_type, page, limit):
        """获取执行列表"""
        condition = []
        if interface_id:
            condition.append('interface_id = %s' % interface_id)
        if start_time:
            condition.append('a.insert_time >= %s' % start_time)
        if end_time:
            condition.append('a.insert_time <= %s' % end_time)
        if run_status:
            # 成功
            if run_status == 1:
                condition.append('a.`status` = 0')
            # 运行中
            elif run_status == 2:
                condition.append('a.`status` = 1')
            # 失败
            elif run_status == 3:
                condition.append('a.`status` = -1')
            # 就绪
            elif run_status == 4:
                condition.append('a.`status` = 3')
        if exec_type:
            condition.append('exec_type = %s' % exec_type)

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = ExecuteModel.get_execute_list(db.etl_db, condition, page, limit)
        total = ExecuteModel.get_execute_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_execute_detail(exec_id):
        """获取执行详情"""
        result = ExecuteModel.get_execute_detail(db.etl_db, exec_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def get_execute_log(exec_id, job_id):
        """获取执行日志"""
        if job_id:
            result = ExecuteModel.get_execute_log_by_job(db.etl_db, exec_id, job_id)
        else:
            result = ExecuteModel.get_execute_log(db.etl_db, exec_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def get_execute_graph(exec_id):
        """获取执行拓扑结构"""
        job_nodes = ExecuteModel.get_execute_graph(db.etl_db, exec_id)
        return Response(job_nodes=job_nodes)

    @staticmethod
    @make_decorator
    def stop_execute_job(exec_id):
        """中止执行任务"""
        # 修改调度主表状态为失败
        ExecuteModel.update_execute_status(db.etl_db, exec_id, -1)
        # 获取正在执行任务
        result = ExecuteModel.get_execute_detail_by_status(db.etl_db, exec_id, 'running')
        for execute in result:
            try:
                # 获取进程id
                if execute['pid']:
                    # rpc分发-停止任务
                    client = Connection(execute['server_host'], config.exec.port)
                    client.rpc.stop(exec_id=exec_id, job_id=execute['job_id'], pid=execute['pid'])
                    log.info('rpc分发-停止任务: 执行id: %s, 任务id: %s' % (exec_id, execute['job_id']))
            except:
                log.error('rpc分发-停止任务异常: host: %s, port: %s, 执行id: %s, 任务id: %s' % (
                    execute['server_host'],
                    config.exec.port,
                    exec_id,
                    execute['job_id']
                ), exc_info=True)
                return Response(status=False)
        return Response(status=True)

    @staticmethod
    @make_decorator
    def restart_execute_job(exec_id, prepose_rely):
        """断点续跑"""
        # 修改调度表状态
        ExecuteModel.update_execute_status(db.etl_db, exec_id, 1)
        # 获取失败调度详情
        result = get_failed_jobs_by_exec_id(exec_id)
        nodes = result['nodes']
        # 找出失败节点
        failed_nodes = {job_id: nodes[job_id] for job_id in nodes if nodes[job_id]['status'] == 'failed'}
        distribute_job = []
        # 遍历所有失败节点
        for job_id in failed_nodes:
            # 考虑前置依赖
            if prepose_rely:
                # 不满足执行状态的前置任务
                not_rely_list = [in_id for in_id in nodes[job_id]['in_degree'] if nodes[in_id]['status'] != 'succeeded']
                if not not_rely_list:
                    distribute_job.append(job_id)
            # 不考虑前置依赖
            else:
                distribute_job.append(job_id)
        # 去重, 分发任务
        for job_id in set(distribute_job):
            log.info('分发任务: 执行id: %s, 任务id: %s' % (exec_id, job_id))
            # 修改执行状态为初始状态
            ScheduleModel.update_exec_job_status(db.etl_db, exec_id, job_id, 'preparing')
            try:
                # rpc分发任务
                client = Connection(nodes[job_id]['server_host'], config.exec.port)
                log.info('rpc分发任务: 执行id: %s, 任务id: %s, host: %s, port: %s' %
                         (exec_id, job_id, nodes[job_id]['server_host'], config.exec.port)
                         )
                client.rpc.execute(
                    exec_id=exec_id,
                    job_id=job_id,
                    server_dir=nodes[job_id]['server_dir'],
                    server_script=nodes[job_id]['server_script'],
                    return_code=nodes[job_id]['return_code'],
                    params=nodes[job_id]['params'],
                    status=nodes[job_id]['status']
                )
            except:
                err_msg = 'rpc连接异常: host: %s, port: %s' % (nodes[job_id]['server_host'], config.exec.port)
                # 添加执行任务详情日志
                ScheduleModel.add_exec_detail_job(db.etl_db, exec_id, job_id, 'ERROR', nodes[job_id]['server_dir'],
                                                  nodes[job_id]['server_script'], err_msg, 3)
                # 修改执行状态
                ScheduleModel.update_exec_job_status(db.etl_db, exec_id, job_id, 'failed')
                ExecuteModel.update_execute_status(db.etl_db, exec_id, -1)
                log.error(err_msg, exc_info=True)
                return Response(distribute_job=distribute_job, msg=err_msg)
        return Response(distribute_job=distribute_job, msg='成功')
