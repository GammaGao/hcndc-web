# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator, Response
from scheduler.generate_dag import get_job_dag_by_exec_id, get_all_jobs_dag_by_exec_id, get_interface_dag_by_exec_id, \
    generate_job_dag_by_interface, generate_interface_dag_by_dispatch
from rpc.rpc_client import Connection
from configs import config, log, db
from models.execute import ExecuteModel
from models.schedule import ScheduleModel
from models.interface import InterfaceModel
# from util.msg_push import send_mail, send_dingtalk
# from operations.job import JobOperation
from conn.mysql_lock import MysqlLock

import time
from copy import deepcopy
from datetime import date, timedelta


def continue_execute_job(exec_id, interface_id):
    """
    获取可执行任务
    1.遍历节点
    2.当前任务流下, 节点出度的所有入度执行成功, 节点出度的状态为待运行
    :param exec_id: 执行id
    :param interface_id: 任务流id
    :return: (待运行任务id, 当前任务流下任务详情列表)
    """
    # 下一批执行任务
    next_job = []
    # 推进流程
    nodes = get_job_dag_by_exec_id(exec_id, interface_id)
    # 遍历所有节点
    for job_id in nodes:
        # 出度
        for out_id in nodes[job_id]['out_degree']:
            flag = True
            # 出度的入度是否成功
            for in_id in nodes[out_id]['in_degree']:
                if nodes[in_id]['status'] != 'succeeded':
                    flag = False
                    break
            # 获取所有层级可执行任务
            if flag and nodes[out_id]['status'] in ('preparing', 'ready'):
                next_job.append(out_id)
    return next_job, nodes


def continue_execute_interface(exec_id, result=None, exec_type=1):
    """
    获取可执行任务流
    1.如果所有执行任务流都完成, 修改执行主表状态[成功]
    2.所有任务流都完成, 修改执行主表状态[成功], 返回退出
    3.获取当前执行id下的任务流, 遍历任务流
    3.自动调度下(exec_type=1)当前节点出度的所有入度成功, 出度的所有入度数据日期>=出度的数据日期, 节点出度的状态为待运行;
      手动调度下(exec_type=2)默认所有出度成功.
    4.获取可执行任务流下初始任务, 存在空任务流, 修改执行任务流状态[成功], 递归本方法
    5.否则修改执行任务流状态[运行中], 返回结果集
    :param result: 结果集
    :param exec_id: 执行id
    :param exec_type: 执行类型: 1.自动, 2.手动
    :return:
    """
    # 可执行任务流id
    if result is None:
        result = {}
    next_interface = []
    # {可执行任务流id: {'job_id': [可执行任务id], 'nodes': {'job_id': {任务详情}}}}
    # 推进流程
    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
        interface_dict = get_interface_dag_by_exec_id(exec_id)
    # 已完成任务流
    complete_interface = [_ for _, item in interface_dict.items() if item['status'] == 0]
    # 所有任务流都完成
    if len(complete_interface) == len(interface_dict):
        # 修改执行主表状态[成功]
        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
            ExecuteModel.update_execute_status(db.etl_db, exec_id, 0)
        return
    # 遍历所有节点
    for interface_id in interface_dict:
        # 自动调度下, 检查出度的入度数据日期和状态是否成功
        if exec_type == 1:
            # 出度任务流的执行详情
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                current_detail = InterfaceModel.get_interface_detail_last_execute(db.etl_db, interface_id)
            for out_id in interface_dict[interface_id]['out_degree']:
                flag = True
                for in_id in interface_dict[out_id]['in_degree']:
                    # 获取出度的入度任务流详情
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                        in_detail = InterfaceModel.get_interface_detail_last_execute(db.etl_db, in_id)
                    # 1.出度的入度本次执行状态不成功, 2.出度的入度没有数据日期, 3.出度的入度数据日期小于出度的数据日期, 4.如果存在出度的上一次执行记录, 上一次执行记录不成功
                    if in_detail['status'] != 0 or not in_detail['run_time'] \
                            or in_detail['run_time'] < current_detail['run_time'] \
                            or (current_detail['last_status'] and current_detail['last_status'] != 0):
                        flag = False
                        break
                if flag and interface_dict[out_id]['status'] == 3:
                    next_interface.append(out_id)
        # 手动调度下, 直接通过
        else:
            for out_id in interface_dict[interface_id]['out_degree']:
                flag = True
                for in_id in interface_dict[out_id]['in_degree']:
                    # 获取出度的入度详情
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                        in_detail = InterfaceModel.get_interface_detail_last_execute(db.etl_db, in_id)
                    # 1.出度的入度本次执行状态不成功
                    if in_detail['status'] != 0:
                        flag = False
                        break
                if flag and interface_dict[out_id]['status'] == 3:
                    next_interface.append(out_id)
        # 获取所有层级可执行任务
        for next_interface_id in set(next_interface):
            nodes = get_job_dag_by_exec_id(exec_id, next_interface_id)
            # 可执行任务流设置默认可执行任务
            result.setdefault(next_interface_id, {'nodes': nodes, 'job_id': []})
            # 遍历所有节点
            for job_id in nodes:
                # 初始节点
                if nodes[job_id]['level'] == 0 and nodes[job_id]['status'] in ('preparing', 'ready'):
                    result[next_interface_id]['job_id'].append(job_id)
    # 出度任务流中符合条件的任务为空, 寻找下一个可执行任务流
    flag = False
    result_deep = deepcopy(result)
    for interface_id, item in result_deep.items():
        # 修改执行任务流状态[成功]
        if not item['job_id']:
            flag = True
            result.pop(interface_id)
            log.info('任务流中任务为空: 执行id: %s, 任务流id: %s' % (exec_id, interface_id))
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, interface_id, 0)
        # 修改执行任务流状态[运行中]
        else:
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, interface_id, 1)
    # 存在空任务流
    if flag:
        return continue_execute_interface(exec_id, result, exec_type)
    else:
        return result
    # # 如果没有可执行任务流
    # if not result:
    #     # 查询执行任务流状态
    #     status_list = ExecuteModel.get_execute_interface_status(db.etl_db, exec_id)
    #     # 存在失败
    #     if -1 in status_list:
    #         interface_status = -1
    #     # 全部成功
    #     elif set(status_list) == {0}:
    #         interface_status = 0
    #     # 运行中
    #     else:
    #         interface_status = 1
    #     # 修改执行主表状态[成功/失败]
    #     ExecuteModel.update_execute_status(db.etl_db, exec_id, interface_status)


def rpc_push_job(exec_id, interface_id, job_id, server_host, port, params_value, server_dir, server_script, return_code,
                 status, date_format='%Y%m%d', run_date=''):
    """
    RPC分发任务
    1.替换$date变量
    :param exec_id: 执行id
    :param interface_id: 任务流id
    :param job_id: 任务id
    :param server_host: RPC执行服务器域名
    :param port: RPC执行服务器端口
    :param params_value: 参数值字符串
    :param server_dir: 脚本目录
    :param server_script: 运行脚本
    :param return_code: 状态返回码
    :param status: 任务状态
    :param date_format: 日期格式
    :param run_date: 数据日期
    :return: 
    """""
    try:
        # rpc分发任务
        client = Connection(server_host, port)
        # 任务参数中数据日期变量为T-1
        if not run_date:
            run_time = (date.today() + timedelta(days=-1)).strftime(date_format)
        else:
            run_time = run_date
        params = params_value.split(',') if params_value else []
        client.rpc.execute(
            exec_id=exec_id,
            interface_id=interface_id,
            job_id=job_id,
            server_dir=server_dir,
            server_script=server_script,
            return_code=return_code,
            params=[item if item != '$date' else run_time for item in params],
            status=status
        )
        client.disconnect()
        return ''
    except:
        err_msg = 'rpc连接异常: host: %s, port: %s' % (server_host, port)
        # 添加执行任务详情日志
        ScheduleModel.add_exec_detail_job(db.etl_db, exec_id, interface_id, job_id, 'ERROR',
                                          server_dir, server_script,
                                          err_msg, 3)
        # 修改数据库, 分布式锁
        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
            # 修改执行详情表状态[失败]
            ScheduleModel.update_exec_job_status(db.etl_db, exec_id, interface_id, job_id, 'failed')
            # 修改执行任务流状态[失败]
            ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, interface_id, -1)
            # 修改执行主表状态[失败]
            ExecuteModel.update_execute_status(db.etl_db, exec_id, -1)
        log.error(err_msg, exc_info=True)
        return err_msg


class ExecuteOperation(object):
    @staticmethod
    @make_decorator
    def get_execute_job(exec_id, interface_id, job_id, status):
        """
        执行服务任务回调
        1.修改详情表回调任务执行状态[成功/失败]
        2.如果执行任务状态成功, 获取当前任务流下一批执行任务(初始节点状态为'preparing'或'ready', 出度的入度==succeeded)
        3.RPC分发当前任务流中可执行的任务, 替换参数变量$date为T-1日期, 修改执行详情表状态[运行中];
          如果RPC异常, 修改执行详情表状态[失败], 执行任务流状态[失败], 执行主表状态[失败]
        4.查看调度任务表中当前执行流的任务状态,
          如果存在失败, exec_status = -1; 如果全部成功, exec_status = 0; else运行中exec_status = 1
        5.查看调度任务表中所有执行流的任务状态,
          如果存在失败, interface_status = -1; 如果全部成功, interface_status = 0; else运行中interface_status = 1
        6.查询执行主表当前状态, 非中断条件下修改调度表状态(允许失败条件下继续执行, master_status != 2)
          修改执行当前任务流状态(exec_status)[成功/失败/运行]
          修改执执行主表状态(interface_status)[成功/失败/运行]
        7.如果当前任务流全部成功(exec_status = 0), 修改账期为T, 获取出度任务流中符合条件的任务
          (出度的入度状态为1或3, 出度的入度数据日期>=出度任务流数据日期)
        8.如果出度任务流中符合条件的任务为空, 修改执行任务流状态[成功], 寻找下一个可执行任务流
          如果没有可执行任务流, 修改执行主表状态[成功/失败]
        9.RPC分发出度任务流中符合条件的任务, 替换参数变量$date为T-1日期, 修改执行详情表状态[运行中];
          如果RPC异常, 修改执行任务状态[失败], 执行任务流状态[失败], 执行主表状态[失败]
        :param exec_id: 执行id
        :param interface_id: 任务流id
        :param job_id: 任务id
        :param status: 执行任务状态
        :return:
        """
        # 修改详情表执行状态
        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
            ScheduleModel.update_exec_job_status(db.etl_db, exec_id, interface_id, job_id, status)
            # 获取执行主表详情
            execute_detail = ExecuteModel.get_exec_dispatch_id(db.etl_db, exec_id)
            # 是否存在
        if status == 'succeeded':
            # 获取下一批执行任务
            distribute_job, nodes = continue_execute_job(exec_id, interface_id)
            # 去重, 分发任务
            for job_id in set(distribute_job):
                # 修改执行详情表状态[运行中]
                with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                    ScheduleModel.update_exec_job_status(db.etl_db, exec_id, interface_id, job_id, 'running')
                log.info('分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (exec_id, interface_id, job_id))
                # RPC分发任务
                push_msg = rpc_push_job(exec_id, interface_id, job_id, nodes[job_id]['server_host'], config.exec.port,
                                        nodes[job_id]['params_value'], nodes[job_id]['server_dir'],
                                        nodes[job_id]['server_script'],
                                        nodes[job_id]['return_code'], nodes[job_id]['status'],
                                        run_date=execute_detail['run_date'])
                if push_msg:
                    return Response(msg=push_msg)

        # 查看调度执行表中当前执行流的状态
        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
            status_list = ExecuteModel.get_execute_detail_status(db.etl_db, interface_id, exec_id)
        # 存在失败
        if 'failed' in status_list:
            exec_status = -1
        # 全部成功
        elif set(status_list) == {'succeeded'}:
            exec_status = 0
        # 运行中
        else:
            exec_status = 1
        # 查询执行任务流状态
        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
            status_list = ExecuteModel.get_execute_interface_status(db.etl_db, exec_id)
        # 存在失败
        if -1 in status_list:
            interface_status = -1
        # 全部成功
        elif set(status_list) == {0}:
            interface_status = 0
        # 运行中
        else:
            interface_status = 1
        # 查询执行主表当前状态
        with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
            master_status = ExecuteModel.get_execute_status(db.etl_db, exec_id)
        # 非中断条件下修改调度表状态(允许失败条件下继续执行)
        if master_status != 2:
            # 修改数据库, 分布式锁
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                # 修改执行任务流状态[成功/失败/运行]
                ExecuteModel.update_exec_interface_status(db.etl_db, exec_id, interface_id, exec_status)
                # 修改执行主表状态[成功/失败/运行]
                ExecuteModel.update_execute_status(db.etl_db, exec_id, interface_status)
        # 当前任务流成功时修改账期, 运行后置任务流
        if exec_status == 0:
            # 当前任务流全部成功时修改账期
            run_time = time.strftime('%Y-%m-%d', time.localtime())
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                ExecuteModel.update_interface_run_time(db.etl_db, interface_id, run_time)
            # 获取可执行任务流
            next_jobs = continue_execute_interface(exec_id, exec_type=execute_detail['exec_type'])
            if not next_jobs:
                return Response(msg='成功')
            for interface_id, item in next_jobs.items():
                for job_id in set(item['job_id']):
                    # 修改执行详情表状态[运行中]
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % exec_id):
                        ScheduleModel.update_exec_job_status(db.etl_db, exec_id, interface_id, job_id, 'running')
                    log.info('分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (exec_id, interface_id, job_id))
                    nodes = item['nodes']
                    # RPC分发任务
                    push_msg = rpc_push_job(exec_id, interface_id, job_id, nodes[job_id]['server_host'],
                                            config.exec.port, nodes[job_id]['params_value'],
                                            nodes[job_id]['server_dir'], nodes[job_id]['server_script'],
                                            nodes[job_id]['return_code'], nodes[job_id]['status'],
                                            run_date=execute_detail['run_date'])
                    if push_msg:
                        return Response(msg=push_msg)

        return Response(msg='成功')

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
    def get_execute_flow_history(dispatch_id, start_time, end_time, run_status, page, limit):
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

        result = ExecuteModel.get_execute_flow_history(db.etl_db, dispatch_id, condition, page, limit)
        total = ExecuteModel.get_execute_flow_history_count(db.etl_db, dispatch_id, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_execute_job_log_1(job_id, start_time, end_time, run_status, page, limit):
        """获取手动执行任务日志"""
        condition = []
        if job_id:
            condition.append('a.job_id = %s' % job_id)
        if start_time:
            condition.append('c.insert_time >= %s' % start_time)
        if end_time:
            condition.append('c.insert_time <= %s' % end_time)
        if run_status:
            # 成功
            if run_status == 1:
                condition.append('c.`status` = 0')
            # 运行中
            elif run_status == 2:
                condition.append('c.`status` = 1')
            # 中断
            elif run_status == 3:
                condition.append('c.`status` = 2')
            # 失败
            elif run_status == 4:
                condition.append('c.`status` = -1')
            # 就绪
            elif run_status == 5:
                condition.append('c.`status` = 3')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = ExecuteModel.get_execute_job_log(db.etl_db, condition, page, limit)
        total = ExecuteModel.get_execute_job_log_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_execute_flow_detail(exec_id):
        """获取任务流执行详情"""
        result = ExecuteModel.get_execute_flow_detail(db.etl_db, exec_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def get_execute_job_log(exec_id, job_id):
        """获取任务执行日志"""
        if job_id:
            result = ExecuteModel.get_execute_job_log_by_id(db.etl_db, exec_id, job_id)
        # 全局日志只显示5行
        else:
            result = ExecuteModel.get_execute_log(db.etl_db, exec_id)
        return Response(result=result, job_id=job_id)

    @staticmethod
    @make_decorator
    def get_execute_graph(exec_id, interface_id):
        """获取执行拓扑结构"""
        # 任务流拓扑
        if not interface_id:
            result = ExecuteModel.get_execute_interface_graph(db.etl_db, exec_id)
            data_type = 1
        else:
            result = ExecuteModel.get_execute_jobs_graph(db.etl_db, exec_id, interface_id)
            data_type = 2
        return Response(result=result, data_type=data_type)

    @staticmethod
    @make_decorator
    def stop_execute_job(exec_id, user_id):
        """
        中止执行任务
        1.修改调度主表状态为[中断]
        2.获取正在执行任务
        3.rpc分发-停止任务
        4.修改执行详情表为[失败], 修改执行任务流状态[中断]
        """
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
                            ScheduleModel.update_exec_job_status(db.etl_db, item, execute['interface_id'],
                                                                 execute['job_id'], 'failed')
                            # 修改执行任务流状态[中断]
                            ExecuteModel.update_exec_interface_status(db.etl_db, item, execute['interface_id'], 2)
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
    def restart_execute_job(exec_id, user_id):
        """
        断点续跑
        1.修改调度主表状态为[运行中]
        2.获取调度任务流参数, 调度信息, 找出[中断/失败]任务流
        3.获取调度任务流详情(所有执行任务), 找出失败任务, 重新生成任务流下所有任务详情
        4.重置失败任务参数, 修改执行详情表参数, 状态为[待运行]
        4.重新生成任务流依赖, 修改执行任务流参数, 状态[运行中]
        5.重新获取调度详情, 找到[运行中]任务流, 重新获取调度任务流详情, 找到运行任务(状态[待运行], 入度执行成功)
        6.去重, RPC分发任务
        """
        for item in exec_id:
            # 修改数据库, 分布式锁
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                # 修改调度表状态为[运行中]
                ExecuteModel.update_execute_status(db.etl_db, item, 1)
                # 获取任务流参数
                interface_dict = get_interface_dag_by_exec_id(exec_id)
            # 获取调度信息
            dispatch = ExecuteModel.get_exec_dispatch_id(db.etl_db, item)
            # 中断/失败任务流
            error_interface = [_ for _, item in interface_dict.items() if item['status'] in (2, -1)]
            # 获取调度任务流详情
            for interface_id in set(error_interface):
                # 获取所有执行任务
                result = get_all_jobs_dag_by_exec_id(item, interface_id)
                nodes = result['nodes']
                # 找出失败任务
                failed_nodes = {job_id: item for job_id, item in nodes.items() if item['status'] == 'failed'}
                # 生成任务流下所有任务详情
                job_list = {item['id']: item for item in generate_job_dag_by_interface(interface_id)}
                # 重置失败任务参数
                for job_id in set(failed_nodes):
                    log.info('重置失败任务参数: 执行id: %s, 任务流id: %s, 任务id: %s' % (item, interface_id, job_id))
                    job = job_list[job_id]
                    # 修改数据库, 分布式锁
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                        # 修改执行详情表参数, 状态为[待运行]
                        ScheduleModel.update_exec_job_reset(db.etl_db, item, interface_id, job_id, 'preparing', job)
                # 重新生成任务流依赖
                interface_list = generate_interface_dag_by_dispatch(dispatch['dispatch_id'], dispatch['is_after'])
                interface = interface_list[str(interface_id)]
                # 修改数据库, 分布式锁
                with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                    # 修改执行任务流参数, 状态[运行中]
                    log.info('重置失败任务流参数: 执行id: %s, 任务流id: %s' % (item, interface_id))
                    ScheduleModel.update_exec_interface_reset(db.etl_db, exec_id, interface['id'], 1, interface)
            # 重新获取调度详情
            interface_list = get_interface_dag_by_exec_id(item)
            # 找到[运行中]任务流
            running_nodes = {_: interface for _, interface in interface_list.items() if interface['status'] == 1}
            for interface_id, node in running_nodes.items():
                # 重新获取调度任务流详情
                result = get_all_jobs_dag_by_exec_id(item, interface_id)
                nodes = result['nodes']
                # 找到[待运行]任务
                preparing_nodes = {_: job for _, job in nodes.items() if job['status'] == 'preparing'}
                rerun_job = []
                for job_id in preparing_nodes:
                    flag = True
                    # 入度
                    for in_id in nodes[job_id]['in_degree']:
                        # 节点的入度是否全部成功
                        if nodes[in_id]['status'] != 'succeeded':
                            flag = False
                            break
                    if flag:
                        rerun_job.append(job_id)
                # 去重, 分发任务
                for job_id in set(rerun_job):
                    log.info('分发任务: 执行id: %s, 任务id: %s' % (item, job_id))
                    push_msg = rpc_push_job(item, interface_id, job_id, nodes[job_id]['server_host'],
                                            config.exec.port, nodes[job_id]['params_value'],
                                            nodes[job_id]['server_dir'], nodes[job_id]['server_script'],
                                            nodes[job_id]['return_code'], nodes[job_id]['status'],
                                            run_date=dispatch['run_date'])
                    if push_msg:
                        return Response(msg=push_msg)
        return Response(msg='成功')

    @staticmethod
    @make_decorator
    def reset_execute_job(exec_id, user_id):
        """
        重置执行任务
        1.获取调度信息
        2.删除执行主表, 执行任务流表, 执行详情表
        3.添加执行主表, 任务流表, 任务表至数据库
        """
        for item in exec_id:
            # 获取调度信息
            dispatch = ExecuteModel.get_exec_dispatch_id(db.etl_db, item)
            # 删除执行主表, 执行任务流表, 执行详情表
            ExecuteModel.delete_execute(db.etl_db, item)
            ExecuteModel.delete_exec_interface(db.etl_db, item)
            ExecuteModel.delete_exec_detail(db.etl_db, item)
            # 获取执行任务流前后依赖关系
            interface_nodes = generate_interface_dag_by_dispatch(dispatch['dispatch_id'], dispatch['is_after'])
            if not interface_nodes:
                continue
            # 获取所有任务流的任务详情
            job_nodes = {}
            for _, interface in interface_nodes.items():
                jobs = generate_job_dag_by_interface(interface['id'])
                job_nodes[interface['id']] = jobs
            # 添加执行表
            ExecuteModel.add_execute_by_id(db.etl_db, exec_id, dispatch['exec_type'], dispatch['dispatch_id'],
                                           dispatch['run_date'], dispatch['is_after'])
            interface_arr = []
            for _, val in interface_nodes.items():
                interface_arr.append({
                    'exec_id': exec_id,
                    'interface_id': val['id'],
                    'in_degree': ','.join(val['in']) if val['in'] else '',
                    'out_degree': ','.join(val['out']) if val['out'] else '',
                    'level': val['level'],
                    'status': 3,
                    'insert_time': int(time.time()),
                    'update_time': int(time.time())
                })
            ExecuteModel.add_exec_interface(db.etl_db, interface_arr) if interface_arr else None
            data = []
            for _, val in job_nodes.items():
                for job in val:
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
        return Response(exec_id=exec_id)

    @staticmethod
    @make_decorator
    def start_execute_job(exec_id, user_id):
        """
        启动执行任务
        1.获取调度详情
        2.修改执行主表状态为[运行中]
        3.获取起始任务流(默认任务流状态为3: 就绪), 获取所有起始任务流下所有任务
        4.开始执行初始任务流中的任务,
          任务流中任务为空, 则视调度已完成,修改调度执行表账期, 修改执行任务流[成功]
          否则修改执行任务流[运行中], rpc分发任务, 修改执行详情表状态[运行中]
          5.如果存在空任务流, 继续下一个任务流
        """
        for item in exec_id:
            # 获取调度详情
            dispatch = ExecuteModel.get_exec_dispatch_id(db.etl_db, item)
            # 修改数据库, 分布式锁
            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                # 修改执行主表状态为[运行中]
                ExecuteModel.update_execute_status(db.etl_db, item, 1)
            # 推进流程
            interface_dict = get_interface_dag_by_exec_id(item)
            # 起始任务流(默认任务流状态为3: 就绪)
            start_interface = [_ for _, item in interface_dict.items() if item['level'] == 0]
            # 任务流的任务详情
            job_nodes = {}
            for interface_id in start_interface:
                # 获取起始任务流下所有任务
                jobs = get_all_jobs_dag_by_exec_id(item, interface_id)
                job_nodes[interface_id] = jobs['source']
            # 开始执行初始任务流中的任务
            flag = False
            for curr_interface in start_interface:
                start_jobs = job_nodes[curr_interface]
                # 任务流中任务为空, 则视调度已完成
                if not start_jobs:
                    flag = True
                    # 修改调度执行表账期
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                        ExecuteModel.update_interface_run_time(db.etl_db, curr_interface, dispatch['run_date'])
                    log.info('任务流中任务为空: 调度id: %s, 执行id: %s, 任务流id: %s' %
                             (dispatch['dispatch_id'], item, curr_interface))
                    # 修改执行任务流[成功]
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                        ExecuteModel.update_exec_interface_status(db.etl_db, item, curr_interface, 0)
                else:
                    # 修改执行任务流[运行中]
                    with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                        ExecuteModel.update_exec_interface_status(db.etl_db, item, curr_interface, 1)
                    # rpc分发任务
                    for job in start_jobs:
                        if job['level'] == 0:
                            # 修改执行详情表状态[运行中]
                            with MysqlLock(config.mysql.etl, 'exec_lock_%s' % item):
                                ScheduleModel.update_exec_job_status(db.etl_db, item, curr_interface, job['job_id'],
                                                                     'running')
                            log.info('分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (item, curr_interface, job['job_id']))
                            rpc_push_job(item, curr_interface, job['job_id'], job['server_host'], config.exec.port,
                                         ','.join(job['params_value']), job['server_dir'], job['server_script'],
                                         job['return_code'], job['status'], run_date=dispatch['run_date'])
            # 继续下一个任务流
            if flag:
                next_jobs = continue_execute_interface(item, exec_type=dispatch['exec_type'])
                for interface_id, val in next_jobs.items():
                    for job_id in set(val['job_id']):
                        log.info('分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (item, interface_id, job_id))
                        nodes = val['nodes']
                        rpc_push_job(item, interface_id, job_id, nodes[job_id]['server_host'],
                                     config.exec.port, nodes[job_id]['params_value'], nodes[job_id]['server_dir'],
                                     nodes[job_id]['server_script'], nodes[job_id]['return_code'],
                                     nodes[job_id]['status'], run_date=dispatch['run_date'])
        return Response(exec_id=exec_id)

    @staticmethod
    @make_decorator
    def get_execute_interface_list(exec_id):
        """获取该执行下的任务流列表"""
        result = ExecuteModel.get_execute_interface_graph(db.etl_db, exec_id)
        return Response(result=result)

# # 查看调度执行表中当前执行流的状态
# status_list = ExecuteModel.get_execute_detail_status(db.etl_db, interface_id, exec_id)
# # 存在失败
# if 'failed' in status_list:
#     exec_status = -1
#     # # 调度预警
#     # failed_alert = ExecuteModel.get_execute_alert(db.etl_db, exec_id, 2)
#     # if failed_alert['is_push'] == 0:
#     #     # 邮件
#     #     if failed_alert['alert_channel'] == 1:
#     #         send_mail(2, failed_alert)
#     #     # 钉钉
#     #     if failed_alert['alert_channel'] == 2:
#     #         send_dingtalk(2, failed_alert)
#     #     # 修改推送状态
#     #     ExecuteModel.update_msg_push(db.etl_db, exec_id)
# # 全部成功
# elif set(status_list) == {'succeeded'}:
#     exec_status = 0
#     # # 调度预警
#     # succeed_alert = ExecuteModel.get_execute_alert(db.etl_db, exec_id, 1)
#     # # 邮件
#     # if succeed_alert['alert_channel'] == 1:
#     #     send_mail(1, succeed_alert)
#     # # 钉钉
#     # if succeed_alert['alert_channel'] == 2:
#     #     send_dingtalk(1, succeed_alert)
