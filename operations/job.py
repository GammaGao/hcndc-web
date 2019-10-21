# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result
from models.job import JobModel
from models.execute import ExecuteModel
from configs import db, config, log
from rpc.rpc_client import Connection


class JobOperation(object):
    @staticmethod
    @make_decorator
    def get_job_list(job_name, start_time, end_time, interface_id, is_deleted, page, limit):
        """获取任务列表"""
        condition = []
        if job_name:
            condition.append('job_name LIKE "%%%%%s%%%%"' % job_name)
        if start_time:
            condition.append('insert_time >= %s' % start_time)
        if end_time:
            condition.append('insert_time <= %s' % end_time)
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
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_job_detail(job_id, interface_id, job_name, job_desc, server_id, server_dir, server_script,
                          old_prep, job_prep, user_id, old_params, job_params, is_deleted):
        """修改任务详情"""
        # 修改详情
        JobModel.update_job_detail(db.etl_db, job_id, interface_id, job_name, job_desc, server_id, server_dir,
                                   server_script, user_id, is_deleted)
        # 修改任务依赖
        old_prep = set() if not old_prep else set(int(i) for i in old_prep.split(','))
        job_prep = set() if not job_prep else set(int(i) for i in job_prep.split(','))
        # 删
        del_data = []
        for prep_id in old_prep - job_prep:
            del_data.append({
                'job_id': job_id,
                'prep_id': prep_id,
                'user_id': user_id
            })
        if del_data:
            JobModel.delete_job_prep(db.etl_db, del_data)
        # 增
        add_data = []
        for prep_id in job_prep - old_prep:
            add_data.append({
                'job_id': job_id,
                'prep_id': prep_id,
                'user_id': user_id
            })
        if add_data:
            JobModel.add_job_prep(db.etl_db, add_data)

        # 修改任务参数
        old_params = set() if not old_prep else set(int(i) for i in old_params.split(','))
        job_params = set() if not job_prep else set(int(i) for i in job_params.split(','))
        # 删
        del_data = []
        for param_id in old_params - job_params:
            del_data.append({
                'job_id': job_id,
                'param_id': param_id,
                'user_id': user_id,
                'update_time': int(time.time())
            })
        if del_data:
            JobModel.delete_job_param(db.etl_db, del_data)
        # 增
        add_data = []
        for param_id in job_params - old_params:
            add_data.append({
                'job_id': job_id,
                'param_id': param_id,
                'user_id': user_id,
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
        if add_data:
            JobModel.add_job_param(db.etl_db, add_data)

        return Response(job_id=job_id)

    @staticmethod
    @make_decorator
    def add_job_detail(job_name, interface_id, job_desc, server_id, server_dir, job_prep, job_params, server_script, user_id):
        """新增任务详情"""
        # 新增任务详情
        job_id = JobModel.add_job_detail(db.etl_db, job_name, interface_id, job_desc, server_id, server_dir,
                                         server_script, user_id)
        # 新增任务依赖
        if job_prep:
            data = []
            for prep_id in job_prep.split(','):
                data.append({
                    'job_id': job_id,
                    'prep_id': prep_id,
                    'user_id': user_id
                })
            JobModel.add_job_prep(db.etl_db, data)
        # 新增任务参数
        if job_params:
            data = []
            for param_id in job_params.split(','):
                data.append({
                    'job_id': job_id,
                    'param_id': param_id,
                    'insert_time': int(time.time()),
                    'update_time': int(time.time()),
                    'user_id': user_id
                })
            JobModel.add_job_param(db.etl_db, data)
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
    def execute_job(job_id, user_id):
        """立即执行任务"""
        # 获取任务
        job = JobModel.get_job_detail(db.etl_db, job_id)
        if job.get('is_deleted', 1):
            abort(400, **make_result(status=400, msg='任务已删除, 不能执行'))
        # 添加执行表
        exec_id = ExecuteModel.add_execute(db.etl_db, 2, 0)
        # 添加执行详情表
        data = {
            'exec_id': exec_id,
            'job_id': job_id,
            'in_degree': '',
            'out_degree': '',
            'server_host': job['server_host'],
            'server_dir': job['server_dir'],
            'server_script': job['server_script'],
            'position': 1,
            'level': 0,
            'status': 'preparing'
        }
        ExecuteModel.add_execute_detail(db.etl_db, data)
        # rpc分发任务
        client = Connection(job['server_host'], config.exec.port)
        try:
            client.rpc.execute(
                exec_id=exec_id,
                job_id=job['job_id'],
                server_dir=job['server_dir'],
                server_script=job['server_script'],
                status='preparing'
            )
            log.info('分发任务: 执行id: %s, 任务id: %s' % (exec_id, job['job_id']))
            return Response(status=True)
        except:
            log.error('rpc连接异常: host: %s, port: %s' % (job['server_host'], config.exec.port), exc_info=True)
            return Response(status=False)
