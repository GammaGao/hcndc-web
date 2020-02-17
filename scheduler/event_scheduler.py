# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from copy import deepcopy
from datetime import date, timedelta

from scheduler.generate_event_dag import generate_interface_dag_by_event, generate_interface_tree_by_event, \
    generate_job_dag_by_interface
from models.event import EventModel
from models.ftp_event import FtpEventModel
from models.ftp import FtpModel
from configs import db
from configs import config, log
from conn.mysql_lock import MysqlLock
from scheduler.generate_event_dag import get_event_interface_dag_by_exec_id, get_event_job_dag_by_exec_id
from rpc.rpc_client import Connection
from ftp_server.ftp import FtpLink
from ftp_server.sftp import SftpLink
from server.decorators import Response


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
        client.rpc.event_execute(
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
        EventModel.add_event_exec_detail_job(db.etl_db, exec_id, interface_id, job_id, 'ERROR', server_dir,
                                             server_script, err_msg, 3)
        # 修改数据库, 分布式锁
        with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
            # 修改执行详情表状态[失败]
            EventModel.update_event_exec_job_status(db.etl_db, exec_id, interface_id, job_id, 'failed')
            # 修改执行任务流状态[失败]
            EventModel.update_event_exec_interface_status(db.etl_db, exec_id, interface_id, -1)
            # 修改执行主表状态[失败]
            EventModel.update_event_execute_status(db.etl_db, exec_id, -1)
        log.error(err_msg, exc_info=True)
        return err_msg


def continue_event_execute_interface(exec_id, result=None, exec_type=1, run_date=''):
    """
    获取事件可执行任务流
    1.如果所有执行任务流都完成, 修改执行主表状态[成功]
    2.所有任务流都完成, 修改执行主表状态[成功], 返回退出
    3.获取当前执行id下的任务流, 遍历任务流
    3.自动调度下(exec_type=1)当前节点出度的所有入度成功, 出度的所有入度数据日期>=出度的数据日期, 节点出度的状态为待运行;
      手动调度下(exec_type=2)默认所有出度成功.
    4.获取可执行任务流下初始任务, 存在空任务流, 修改执行任务流状态[成功], 修改任务流数据日期, 递归本方法
    5.否则修改执行任务流状态[运行中], 返回结果集
    :param result: 结果集
    :param exec_id: 执行id
    :param exec_type: 执行类型: 1.自动, 2.手动
    :param run_date: 数据日期
    :return:
    """
    if not run_date:
        run_date = time.strftime('%Y-%m-%d', time.localtime())
    # 可执行任务流id
    if result is None:
        result = {}
    next_interface = []
    # {可执行任务流id: {'job_id': [可执行任务id], 'nodes': {'job_id': {任务详情}}}}
    # 推进流程
    with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
        interface_dict = get_event_interface_dag_by_exec_id(exec_id)
    # 已完成任务流
    complete_interface = [_ for _, item in interface_dict.items() if item['status'] == 0]
    # 所有任务流都完成
    if len(complete_interface) == len(interface_dict):
        # 修改执行主表状态[成功]
        with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
            EventModel.update_event_execute_status(db.etl_db, exec_id, 0)
        return
    # 遍历所有节点
    for interface_id in interface_dict:
        # 自动调度下, 检查出度的入度数据日期和状态是否成功
        if exec_type == 1:
            # 出度任务流的执行详情
            with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                current_detail = EventModel.get_event_interface_detail_last_execute(db.etl_db, interface_id)
            for out_id in interface_dict[interface_id]['out_degree']:
                flag = True
                for in_id in interface_dict[out_id]['in_degree']:
                    # 获取出度的入度任务流详情
                    with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                        in_detail = EventModel.get_event_interface_detail_last_execute(db.etl_db, in_id)
                    # 1.出度的入度本次执行状态不成功, 2.如果存在出度的上一次执行记录, 上一次执行记录不成功
                    if in_detail['status'] != 0 \
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
                    with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                        in_detail = EventModel.get_event_interface_detail_last_execute(db.etl_db, in_id)
                    # 1.出度的入度本次执行状态不成功
                    if in_detail['status'] != 0:
                        flag = False
                        break
                if flag and interface_dict[out_id]['status'] == 3:
                    next_interface.append(out_id)
        # 获取所有层级可执行任务
        for next_interface_id in set(next_interface):
            nodes = get_event_job_dag_by_exec_id(exec_id, next_interface_id)
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
            with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                EventModel.update_event_exec_interface_status(db.etl_db, exec_id, interface_id, 0)
        # 修改执行任务流状态[运行中]
        else:
            with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                EventModel.update_event_exec_interface_status(db.etl_db, exec_id, interface_id, 1)
    # 存在空任务流
    if flag:
        return continue_event_execute_interface(exec_id, result, exec_type, run_date)
    else:
        return result


def get_event_job(event_id, exec_type=1, run_date='', date_format='%Y%m%d'):
    """
    事件执行开始方法
    1.传入事件id(ftp_event_id)
    2.获取事件详情(任务流id, 任务流名称, 数据日期)
    3.获取FTP服务器配置(传入ftp_event_id)
    4.FTP服务器不存在抛出异常
    5.检测FTP服务器连接, 将数据日期替换文件名, 查询文件是否存在
    6.不存在退出
    7.条件一: 文件存在; 条件二: 未存在当前数据日期的成功执行记录(调度id查询), 执行任务流
    8.构造任务流, for任务流列表, return任务流依赖数据结构, 每个dict遍历一遍, 是否存在未for的key,
    如果存在(该任务流在之前任务流的数据结构中), 跳过该任务流, 写入数据库, 执行部分同调度触发, 执行成功时修改数据日期到当天
    :param event_id: 事件id
    :param exec_type: 执行类型: 1.自动, 2.手动
    :param run_date: 手动传入$date日期
    :param date_format: $date日期格式
    :return: None
    """
    # 传入日期
    if run_date and date_format:
        run_time = time.strftime(date_format, time.strptime(run_date, '%Y-%m-%d'))
    else:
        event_detail = FtpEventModel.get_ftp_event_detail(db.etl_db, event_id)
        if event_detail and event_detail['date_time']:
            run_time = time.strftime(date_format, time.strptime(event_detail['date_time'], '%Y-%m-%d'))
        else:
            run_time = time.strftime(date_format, time.localtime())
    # 任务流详情
    detail_list = EventModel.get_interface_detail_by_ftp_event_id(db.etl_db, event_id)
    # 检测是否执行
    # 获取FTP服务器配置
    ftp_detail = FtpEventModel.get_ftp_detail_by_event_id(db.etl_db, event_id)
    # 检测FTP服务器文件是否存在
    if isinstance(ftp_detail['ftp_passwd'], bytes):
        ftp_detail['ftp_passwd'] = ftp_detail['ftp_passwd'].decode('utf-8', 'ignore')
    try:
        # FTP连接
        if ftp_detail['ftp_type'] == 1:
            ftp = FtpLink(ftp_detail['ftp_host'], ftp_detail['ftp_port'], ftp_detail['ftp_user'], ftp_detail['ftp_passwd'])
            FtpModel.update_ftp_status(db.etl_db, ftp_detail['ftp_id'], 0)
            # 文件名
            file_name = time.strftime(ftp_detail['file_name'], time.strptime(ftp_detail['date_time'], '%Y-%m-%d'))
            result = ftp.test_file(ftp_detail['data_path'], file_name)
            ftp.close()
        # SFTP连接
        elif ftp_detail['ftp_type'] == 2:
            ftp = SftpLink(ftp_detail['ftp_host'], ftp_detail['ftp_port'], ftp_detail['ftp_user'], ftp_detail['ftp_passwd'])
            FtpModel.update_ftp_status(db.etl_db, ftp_detail['ftp_id'], 0)
            # 文件名
            file_name = time.strftime(ftp_detail['file_name'], time.strptime(ftp_detail['date_time'], '%Y-%m-%d'))
            result = ftp.test_file(ftp_detail['data_path'], file_name)
            ftp.close()
        else:
            FtpModel.update_ftp_status(db.etl_db, ftp_detail['ftp_id'], 1)
            return Response(status=400, msg='FTP服务器类型未知')
    except:
        FtpModel.update_ftp_status(db.etl_db, ftp_detail['ftp_id'], 1)
        return Response(status=400, msg='FTP连接异常')
    # 当前数据日期的成功执行记录
    success_detail = EventModel.get_event_exec_detail_success(db.etl_db, event_id, ftp_detail['date_time'])
    # 文件存在, 未存在当前数据日期的成功执行记录(调度id查询)
    if result and not success_detail:
        # 执行任务流
        pass
    else:
        return Response(status=400, msg='FTP文件目录不存在')
    interface_dag_nodes = {}
    # 遍历多个任务流
    for detail in detail_list:
        # 生成执行任务流前后依赖关系
        dag = generate_interface_dag_by_event(detail)
        # 生成执行任务流树形关系
        tree = generate_interface_tree_by_event(detail)
        tree_nodes = [_ for _ in tree.keys()]
        # 填充树形节点
        for key in set(tree_nodes):
            dag[key]['is_tree'] = 1
        # 合并
        interface_dag_nodes.update(dag)

    if not interface_dag_nodes:
        return
    # 需执行任务流
    interface_tree_nodes = {key: value for key, value in interface_dag_nodes.items() if value['is_tree'] == 1}
    # 获取所有任务流的任务详情
    job_nodes = {}
    for _, item in interface_tree_nodes.items():
        jobs = generate_job_dag_by_interface(item['id'])
        job_nodes[item['id']] = jobs
    # 添加执行主表, 任务流表, 任务表至数据库
    exec_id = add_event_exec_record(event_id, interface_dag_nodes, job_nodes, exec_type, run_time, date_format)
    # 初始任务流
    start_interface = [_ for _, item in interface_tree_nodes.items() if item['level'] == 0]
    # 开始执行初始任务流中的任务
    flag = False
    for curr_interface in start_interface:
        start_jobs = job_nodes[curr_interface]
        # 任务流中任务为空, 则视调度已完成
        if not start_jobs:
            flag = True
            log.info('事件任务流中任务为空: 事件id: %s, 执行id: %s, 任务流id: %s' % (event_id, exec_id, curr_interface))
            # 修改执行任务流[成功]
            with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                EventModel.update_event_exec_interface_status(db.etl_db, exec_id, curr_interface, 0)
        else:
            # 修改执行任务流[运行中]
            with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                EventModel.update_event_exec_interface_status(db.etl_db, exec_id, curr_interface, 1)
            # rpc分发任务
            for job in start_jobs:
                if job['level'] == 0:
                    # 修改执行详情表状态[运行中]
                    with MysqlLock(config.mysql.etl, 'event_lock_%s' % exec_id):
                        EventModel.update_event_exec_job_status(db.etl_db, exec_id, curr_interface, job['id'],
                                                                'running')
                    log.info('事件分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (exec_id, curr_interface, job['id']))
                    rpc_push_job(exec_id, curr_interface, job['id'], job['server_host'], config.exec.port,
                                 ','.join(job['params_value']), job['server_dir'], job['server_script'],
                                 job['return_code'], job['status'], run_date=run_time)
    # 继续下一个任务流
    if flag:
        next_jobs = continue_event_execute_interface(exec_id, exec_type=exec_type, run_date=run_time)
        if not next_jobs:
            return
        for interface_id, item in next_jobs.items():
            for job_id in set(item['job_id']):
                log.info('分发任务: 执行id: %s, 任务流id: %s, 任务id: %s' % (exec_id, interface_id, job_id))
                nodes = item['nodes']
                rpc_push_job(exec_id, interface_id, job_id, nodes[job_id]['server_host'],
                             config.exec.port, nodes[job_id]['params_value'],
                             nodes[job_id]['server_dir'], nodes[job_id]['server_script'],
                             nodes[job_id]['return_code'], nodes[job_id]['status'], run_date=run_time)


def add_event_exec_record(event_id, interface_nodes, job_nodes, exec_type=1, run_date='', date_format='%Y%m%d'):
    """添加事件执行表和执行详情表"""
    # 添加执行表
    if not run_date:
        run_date = time.strftime(date_format, time.localtime())
    exec_id = EventModel.add_event_execute(db.etl_db, exec_type, event_id, run_date, date_format)
    interface_arr = []
    for _, item in interface_nodes.items():
        interface_arr.append({
            'exec_id': exec_id,
            'interface_id': item['id'],
            'in_degree': ','.join(item['in']) if item['in'] else '',
            'out_degree': ','.join(item['out']) if item['out'] else '',
            'level': item['level'],
            'is_tree': item.get('is_tree', 0),
            'status': 0 if item.get('is_tree', 0) == 0 else 3,
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
    EventModel.add_event_exec_interface(db.etl_db, interface_arr) if interface_arr else None
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
                'params_value': ','.join(job.get('params_value', [])),
                'server_script': job.get('server_script', ''),
                'position': job['position'],
                'return_code': job.get('return_code', 0),
                'level': job.get('level', 0),
                'status': job.get('status', 'preparing'),
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
    # 添加执行详情表
    EventModel.add_event_execute_detail(db.etl_db, data) if data else None
    return exec_id
