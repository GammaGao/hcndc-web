# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator, Response
from scheduler.generate_dag import get_job_dag_by_exec_id, get_all_jobs_dag_by_exec_id
from rpc.rpc_client import Connection
from configs import config, log, db
from models.execute import ExecuteModel
from models.schedule import ScheduleModel
from util.msg_push import send_mail, send_dingtalk
from operations.job import JobOperation
from conn.mysql_lock import MysqlLock

import time


class ExecuteOperation(object):
    @staticmethod
    @make_decorator
    def get_execute_job(exec_id, job_id, status):
        """获取执行任务-推进执行流程"""
        # 修改数据库, 分布式锁
        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
            # 修改详情表执行状态
            ScheduleModel.update_exec_job_status(db.etl_db, exec_id, job_id, status)
        distribute_job = []
        if status == 'succeeded':
            # 推进流程
            result = get_job_dag_by_exec_id(exec_id)
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
                    # 获取所有层级可执行任务
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
                        params=nodes[job_id]['params_value'].split(','),
                        status=nodes[job_id]['status']
                    )
                except:
                    err_msg = 'rpc连接异常: host: %s, port: %s' % (nodes[job_id]['server_host'], config.exec.port)
                    # 添加执行任务详情日志
                    ScheduleModel.add_exec_detail_job(db.etl_db, exec_id, job_id, 'ERROR', nodes[job_id]['server_dir'],
                                                      nodes[job_id]['server_script'], err_msg, 3)
                    # 修改数据库, 分布式锁
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
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
            run_time = time.strftime('%Y-%m-%d', time.localtime())
            ExecuteModel.update_interface_account_by_execute_id(db.etl_db, exec_id, run_time)
        # 查询执行主表当前状态
        master_status = ExecuteModel.get_execute_status(db.etl_db, exec_id)
        # 非中断条件下修改调度执行表状态
        if master_status != 2:
            # 修改数据库, 分布式锁
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                ExecuteModel.update_execute_status(db.etl_db, exec_id, exec_status)

        return Response(distribute_job=distribute_job, msg='成功')

    @staticmethod
    @make_decorator
    def get_execute_flow(interface_id, interface_index, run_status, start_time, end_time, page, limit):
        """获取任务流最新日志"""
        condition = []
        if interface_id:
            condition.append('a.interface_id = %s' % interface_id)
        if interface_index:
            condition.append('a.interface_index IN (%s)' % ','.join('"%s"' % item for item in interface_index))
        if start_time:
            condition.append('d.insert_time >= %s' % start_time)
        if end_time:
            condition.append('d.insert_time <= %s' % end_time)
        if run_status:
            # 成功
            if run_status == 1:
                condition.append('d.`status` = 0')
            # 运行中
            elif run_status == 2:
                condition.append('d.`status` = 1')
            # 中断
            elif run_status == 3:
                condition.append('d.`status` = 2')
            # 失败
            elif run_status == 4:
                condition.append('d.`status` = -1')
            # 就绪
            elif run_status == 5:
                condition.append('d.`status` = 3')

        condition = ' AND ' + ' AND '.join(condition) if condition else ''

        result = ExecuteModel.get_execute_flow(db.etl_db, condition, page, limit)
        for item in result:
            item['run_time'] = item['run_time'].strftime('%Y-%m-%d') if item['run_time'] else None
        total = ExecuteModel.get_execute_flow_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_execute_history(dispatch_id, start_time, end_time, run_status, page, limit):
        """获取任务流历史日志"""
        condition = []
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
            # 中断
            elif run_status == 3:
                condition.append('a.`status` = 2')
            # 失败
            elif run_status == 4:
                condition.append('a.`status` = -1')
            # 就绪
            elif run_status == 5:
                condition.append('a.`status` = 3')

        condition = ' AND ' + ' AND '.join(condition) if condition else ''

        result = ExecuteModel.get_execute_history(db.etl_db, dispatch_id, condition, page, limit)
        total = ExecuteModel.get_execute_history_count(db.etl_db, dispatch_id, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_execute_job_log(job_id, start_time, end_time, run_status, page, limit):
        """获取手动执行任务日志"""
        condition = []
        if job_id:
            condition.append('b.job_id = %s' % job_id)
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
            # 中断
            elif run_status == 3:
                condition.append('a.`status` = 2')
            # 失败
            elif run_status == 4:
                condition.append('a.`status` = -1')
            # 就绪
            elif run_status == 5:
                condition.append('a.`status` = 3')

        condition = ' AND ' + ' AND '.join(condition) if condition else ''

        result = ExecuteModel.get_execute_job_log(db.etl_db, condition, page, limit)
        total = ExecuteModel.get_execute_job_log_count(db.etl_db, condition)
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
    def stop_execute_job(exec_id, user_id):
        """中止执行任务"""
        msg = []
        for item in exec_id:
            # 修改数据库, 分布式锁
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                # 修改调度主表状态为[中断]
                stop_num = ExecuteModel.update_execute_stop(db.etl_db, item, 2)
            # 是否成功中断判断
            if not stop_num:
                msg.append('执行ID: [%s]状态为非执行中, 中断失败' % item)
                continue
            # 获取正在执行任务
            result = ExecuteModel.get_execute_detail_by_status(db.etl_db, item, 'running')
            for execute in result:
                try:
                    # 获取进程id
                    if execute['pid']:
                        # rpc分发-停止任务
                        client = Connection(execute['server_host'], config.exec.port)
                        client.rpc.stop(exec_id=item, job_id=execute['job_id'], pid=execute['pid'])
                        # 修改数据库, 分布式锁
                        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                            # 修改执行详情表为[失败]
                            ScheduleModel.update_exec_job_status(db.etl_db, item, execute['job_id'], 'failed')
                        log.info('rpc分发-停止任务: 执行id: %s, 任务id: %s' % (item, execute['job_id']))
                except:
                    err_msg = 'rpc分发-停止任务异常: host: %s, port: %s, 执行id: %s, 任务id: %s' % (
                        execute['server_host'],
                        config.exec.port,
                        item,
                        execute['job_id']
                    )
                    log.error(err_msg, exc_info=True)
                    msg.append(err_msg)
        return Response(msg=msg)

    @staticmethod
    @make_decorator
    def restart_execute_job(exec_id, prepose_rely, user_id):
        """断点续跑"""
        for item in exec_id:
            # 修改数据库, 分布式锁
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                # 修改调度表状态为[运行中]
                ExecuteModel.update_execute_status(db.etl_db, item, 1)
            # 获取调度详情
            result = get_all_jobs_dag_by_exec_id(item)
            nodes = result['nodes']
            # 找出失败节点
            failed_nodes = {job_id: nodes[job_id] for job_id in nodes if nodes[job_id]['status'] == 'failed'}
            # 重置失败节点参数
            for job_id in set(failed_nodes):
                log.info('重置失败节点参数: 执行id: %s, 任务id: %s' % (item, job_id))
                # 获取任务参数
                params = JobOperation.get_job_params(db.etl_db, job_id)
                # 修改数据库, 分布式锁
                with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                    # 修改执行详情表状态为[待运行]
                    ScheduleModel.update_exec_job_reset(db.etl_db, item, job_id, 'preparing', ','.join(params))
            # 重新获取调度详情
            result = get_all_jobs_dag_by_exec_id(item)
            nodes = result['nodes']
            # 找到[待运行]节点
            preparing_nodes = {job_id: nodes[job_id] for job_id in nodes if nodes[job_id]['status'] == 'preparing'}
            rerun_job = []
            for job_id in preparing_nodes:
                flag = True
                # 入度
                for in_id in nodes[job_id]['in_degree']:
                    # 节点的入度是否全部成功
                    if nodes[in_id]['position'] == 1 and nodes[in_id]['status'] != 'succeeded':
                        flag = False
                        break
                if flag:
                    rerun_job.append(job_id)
                # TODO 考虑前置依赖(代码中无不考虑前置依赖部分代码)
                # if prepose_rely:
                #     flag = True
                #     # 入度
                #     for in_id in nodes[job_id]['in_degree']:
                #         # 节点的入度是否全部成功
                #         if nodes[in_id]['position'] == 1 and nodes[in_id]['status'] != 'succeeded':
                #             flag = False
                #             break
                #     if flag:
                #         rerun_job.append(job_id)
                # # 不考虑前置依赖
                # else:
                #     rerun_job.append(job_id)
            # 去重, 分发任务
            for job_id in set(rerun_job):
                log.info('分发任务: 执行id: %s, 任务id: %s' % (item, job_id))
                try:
                    # rpc分发任务
                    client = Connection(nodes[job_id]['server_host'], config.exec.port)
                    client.rpc.execute(
                        exec_id=item,
                        job_id=job_id,
                        server_dir=nodes[job_id]['server_dir'],
                        server_script=nodes[job_id]['server_script'],
                        return_code=nodes[job_id]['return_code'],
                        params=nodes[job_id]['params_value'].split(','),
                        status=nodes[job_id]['status']
                    )
                except:
                    err_msg = 'rpc连接异常: host: %s, port: %s' % (nodes[job_id]['server_host'], config.exec.port)
                    # 添加执行任务详情日志
                    ScheduleModel.add_exec_detail_job(db.etl_db, item, job_id, 'ERROR', nodes[job_id]['server_dir'],
                                                      nodes[job_id]['server_script'], err_msg, 3)
                    # 修改数据库, 分布式锁
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                        # 修改执行详情表状态[失败]
                        ScheduleModel.update_exec_job_status(db.etl_db, item, job_id, 'failed')
                        # 修改执行主表状态[失败]
                        ExecuteModel.update_execute_status(db.etl_db, item, -1)
                    log.error(err_msg, exc_info=True)
                    return Response(msg=err_msg)
        return Response(msg='成功')

    @staticmethod
    @make_decorator
    def reset_execute_job(exec_id, user_id):
        """重置执行任务"""
        for item in exec_id:
            # 获取调度详情
            result = get_all_jobs_dag_by_exec_id(item)
            nodes = result['nodes']
            # 重置节点参数
            for job_id in nodes:
                log.info('重置节点参数: 执行id: %s, 任务id: %s' % (item, job_id))
                # 获取任务参数
                params = JobOperation.get_job_params(db.etl_db, job_id)
                # 修改数据库, 分布式锁
                with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                    # 修改执行主表状态为[就绪]
                    ExecuteModel.update_execute_status(db.etl_db, item, 3)
                    # 修改执行详情表状态为[待运行]
                    ScheduleModel.update_exec_job_reset(db.etl_db, item, job_id, 'preparing', ','.join(params))
        return Response(exec_id=exec_id)

    @staticmethod
    @make_decorator
    def start_execute_job(exec_id, user_id):
        """启动执行任务"""
        for item in exec_id:
            # 推进流程
            result = get_job_dag_by_exec_id(item)
            nodes = result['nodes']
            # 修改数据库, 分布式锁
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                # 修改执行主表状态为[运行中]
                ExecuteModel.update_execute_status(db.etl_db, item, 1)
            dispatch = ExecuteModel.get_exec_dispatch_id(db.etl_db, item)
            # 任务流中任务为空, 则视调度已完成
            if not nodes:
                # 修改数据库, 分布式锁
                with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                    # 修改执行主表状态为[成功]
                    ExecuteModel.update_execute_status(db.etl_db, item, 0)
                # 修改调度执行表账期
                if dispatch['exec_type'] == 1 and dispatch['dispatch_id']:
                    run_time = time.strftime('%Y-%m-%d', time.localtime())
                    ExecuteModel.update_interface_account_by_dispatch_id(db.etl_db, dispatch['dispatch_id'], run_time)
                log.info('任务流中任务为空: 调度id: %s' % dispatch['dispatch_id'])
                return Response(exec_id=exec_id)

            # 遍历所有节点
            for job_id in nodes:
                job = nodes[job_id]
                # 获取初始层级可执行任务
                if job['level'] == 0 and job['position'] == 1:
                    try:
                        client = Connection(job['server_host'], config.exec.port)
                        client.rpc.execute(
                            exec_id=item,
                            job_id=job_id,
                            server_dir=job['server_dir'],
                            server_script=job['server_script'],
                            return_code=job['return_code'],
                            params=job['params_value'].split(','),
                            status=job['status']
                        )
                        log.info('分发任务: 执行id: %s, 任务id: %s' % (item, job_id))
                    except:
                        err_msg = 'rpc连接异常: host: %s, port: %s' % (job['server_host'], config.exec.port)
                        # 添加执行任务详情日志
                        ScheduleModel.add_exec_detail_job(db.etl_db, item, job_id, 'ERROR', job['server_dir'],
                                                          job['server_script'], err_msg, 3)
                        # 修改数据库, 分布式锁
                        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                            # 修改执行详情表状态[失败]
                            ScheduleModel.update_exec_job_status(db.etl_db, item, job_id, 'failed')
                            # 修改执行主表状态[失败]
                            ExecuteModel.update_execute_status(db.etl_db, item, -1)
                        log.error(err_msg, exc_info=True)

        return Response(exec_id=exec_id)
