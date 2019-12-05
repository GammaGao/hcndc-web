# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask_restful import abort
from datetime import date, timedelta

from server.decorators import make_decorator, Response
from server.status import make_result
from models.job import JobModel
from models.execute import ExecuteModel
from models.schedule import ScheduleModel
from configs import db, config, log
from rpc.rpc_client import Connection
from util.db_util import get_db_data_one
from conn.mysql_lock import MysqlLock


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


class JobOperation(object):
    @staticmethod
    @make_decorator
    def get_job_list(job_name, job_index, interface_id, is_deleted, page, limit):
        """获取任务列表"""
        condition = []
        if job_name:
            condition.append('job_name LIKE "%%%%%s%%%%"' % job_name)
        if job_index:
            condition.append('job_index IN (%s)' % ','.join('"%s"' % item for item in job_index))
        if interface_id:
            condition.append('interface_id = %s' % interface_id)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = JobModel.get_job_list(db.etl_db, condition, page, limit)
        total = JobModel.get_job_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def delete_job(job_id, user_id):
        """删除任务"""
        # 是否在任务依赖中
        prep_count = JobModel.is_alive_job(db.etl_db, job_id)
        if prep_count:
            abort(400, **make_result(status=400, msg='任务存在%s个依赖, 不能删除' % prep_count))
        result = JobModel.delete_job(db.etl_db, job_id, user_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def get_job_detail(job_id):
        """获取任务详情"""
        result = JobModel.get_job_detail(db.etl_db, job_id)
        result['run_time'] = result['run_time'].strftime('%Y-%m-%d') if result['run_time'] else ''
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_job_detail(job_id, interface_id, job_name, job_desc, job_index, server_id, server_dir, server_script,
                          return_code, old_prep, job_prep, user_id, old_params, job_params, is_deleted):
        """修改任务详情"""
        # 任务名称查重
        job_detail = JobModel.get_job_detail_by_name(db.etl_db, job_name)
        if job_detail and job_detail['job_id'] != job_id:
            abort(400, **make_result(status=400, msg='任务名称重复, 已存在数据库中'))
        # 修改详情
        JobModel.update_job_detail(db.etl_db, job_id, interface_id, job_name, job_desc, job_index, server_id,
                                   server_dir,
                                   server_script, return_code, user_id, is_deleted)
        # 修改任务依赖
        old_prep = set() if not old_prep else set(int(i) for i in old_prep.split(','))
        job_prep = set() if not job_prep else set(int(i) for i in job_prep.split(','))
        # 删
        del_data = []
        for prep_id in old_prep - job_prep:
            del_data.append({
                'job_id': job_id,
                'prep_id': prep_id,
                'user_id': user_id,
                'update_time': int(time.time())
            })
        JobModel.delete_job_prep(db.etl_db, del_data) if del_data else None
        # 增
        add_data = []
        for prep_id in job_prep - old_prep:
            add_data.append({
                'job_id': job_id,
                'prep_id': prep_id,
                'user_id': user_id,
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
        JobModel.add_job_prep(db.etl_db, add_data) if add_data else None

        # 修改任务参数(保证参数顺序, 全部删除再新增)
        old_params = set() if not old_params else set(int(i) for i in old_params.split(','))
        job_params = [] if not job_params else [int(i) for i in job_params.split(',')]
        # 原顺序不变去重
        add_params = []
        for x in job_params:
            if x not in add_params:
                add_params.append(x)
        # 删
        del_data = []
        for param_id in old_params:
            del_data.append({
                'job_id': job_id,
                'param_id': param_id,
                'user_id': user_id,
                'update_time': int(time.time())
            })
        JobModel.delete_job_param(db.etl_db, del_data) if del_data else None
        # 增
        add_data = []
        for param_id in add_params:
            add_data.append({
                'job_id': job_id,
                'param_id': param_id,
                'user_id': user_id,
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
        JobModel.add_job_param(db.etl_db, add_data) if add_data else None
        return Response(job_id=job_id)

    @staticmethod
    @make_decorator
    def add_job_detail(job_name, interface_id, job_desc, job_index, server_id, server_dir, job_prep, job_params,
                       server_script, user_id, return_code):
        """新增任务详情"""
        # 任务名称查重
        if JobModel.get_job_detail_by_name(db.etl_db, job_name):
            abort(400, **make_result(status=400, msg='任务名称重复, 已存在数据库中'))
        # 新增任务详情
        job_id = JobModel.add_job_detail(db.etl_db, job_name, interface_id, job_desc, job_index, server_id, server_dir,
                                         server_script, return_code, user_id)
        # 新增任务依赖
        job_prep = job_prep.split(',') if job_prep else []
        data = []
        for prep_id in job_prep:
            data.append({
                'job_id': job_id,
                'prep_id': prep_id,
                'user_id': user_id,
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
        JobModel.add_job_prep(db.etl_db, data) if data else None
        # 新增任务参数
        job_params = job_params.split(',') if job_params else []
        data = []
        for param_id in job_params:
            data.append({
                'job_id': job_id,
                'param_id': param_id,
                'insert_time': int(time.time()),
                'update_time': int(time.time()),
                'user_id': user_id
            })
        JobModel.add_job_param(db.etl_db, data) if data else None
        return Response(job_id=job_id)

    @staticmethod
    @make_decorator
    def get_job_list_all(interface_id):
        """获取所有任务列表"""
        if not interface_id:
            result = JobModel.get_job_list_all(db.etl_db)
        else:
            result = JobModel.get_job_list_all_by_interface(db.etl_db, interface_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def execute_job(job_id):
        """立即执行任务"""
        # 获取任务
        job = JobModel.get_job_detail(db.etl_db, job_id)
        if job['is_deleted']:
            abort(400, **make_result(status=400, msg='任务已删除, 不能执行'))
        # 获取任务参数
        params = JobOperation.get_job_params(db.etl_db, job_id)
        # 添加执行表
        run_date = (date.today() + timedelta(days=-1)).strftime('%Y%d%m')
        exec_id = ExecuteModel.add_execute(db.etl_db, 2, 0, run_date, 0)
        # 添加执行详情表
        data = {
            'exec_id': exec_id,
            'interface_id': 0,
            'job_id': job_id,
            'in_degree': '',
            'out_degree': '',
            'server_host': job['server_host'],
            'server_dir': job['server_dir'],
            'params_value': ','.join(params),
            'server_script': job['server_script'],
            'return_code': job['return_code'],
            'position': 1,
            'level': 0,
            'status': 'preparing',
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        }
        ExecuteModel.add_execute_detail(db.etl_db, data)
        # RPC分发任务
        push_msg = rpc_push_job(exec_id, 0, job_id, job['server_host'], config.exec.port,
                                ','.join(params), job['server_dir'], job['server_script'], job['return_code'],
                                'preparing', run_date=run_date)
        if push_msg:
            return Response(status=False, msg=push_msg)
        else:
            return Response(status=True, msg='成功')

    @staticmethod
    def get_job_params(cursor, job_id):
        """获取任务参数"""
        # 获取任务
        job = JobModel.get_job_detail(cursor, job_id)
        if job['is_deleted']:
            abort(400, **make_result(status=400, msg='任务已删除, 不能执行'))
        # 获取任务参数
        job_params = JobModel.get_job_params_by_job_id(db.etl_db, job_id)
        params = []
        for item in job_params:
            # 静态参数
            if item['param_type'] == 0:
                params.append(item['param_value'])
            # SQL参数
            elif item['param_type'] == 1:
                # 获取SQL参数
                result = get_db_data_one(item['source_type'], item['source_host'], item['source_port'],
                                         item['source_user'], item['source_password'], item['source_database'],
                                         item['auth_type'], item['param_value'])
                if result['flag'] == 0:
                    params.append(result['result'])
                else:
                    abort(400, **make_result(status=400, msg='获取任务SQL参数错误[ERROR: %s]' % result['msg']))
            # 上下文参数
            elif item['param_type'] == 2:
                # 任务流名称
                if item['param_value'] == '$flow_name':
                    params.append(job['interface_name'])
                # 任务名称
                elif item['param_value'] == '$job_name':
                    params.append(job['job_name'])
                # 数据日期(该参数需要传递, 变量代替)
                elif item['param_value'] == '$date':
                    params.append('$date')
        return params

    @staticmethod
    @make_decorator
    def get_job_index():
        """获取所有任务目录"""
        result = JobModel.get_job_index(db.etl_db)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def delete_job_many(job_id_arr, user_id):
        """批量删除任务"""
        err_mag = []
        for item in job_id_arr:
            # 是否在任务依赖中
            prep_count = JobModel.is_alive_job(db.etl_db, item)
            if prep_count:
                err_mag.append('任务ID: [%s]存在%s个依赖, 不能删除' % (item, prep_count))
        if not err_mag:
            condition = '(%s)' % ','.join(str(item) for item in job_id_arr)
            JobModel.delete_job_many(db.etl_db, condition, user_id)
        return Response(msg=err_mag)
