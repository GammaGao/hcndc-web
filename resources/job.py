# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from document.job import *
from filters.job import JobFilter
from operations.job import JobOperation
from verify.job import JobVerify
from verify.permission import PermissionVerify


class JobList(Resource):
    @staticmethod
    @job_list_request
    @job_list_response_success
    @JobFilter.filter_list_data(result=list, total=int)
    @JobOperation.get_job_list(job_name=str, start_time=int, end_time=int, interface_id=int, is_deleted=int,
                               page=int, limit=int)
    @JobVerify.verify_get_job_list(job_name=str, start_time=int, end_time=int, interface_id=int, is_deleted=int,
                                   page=int, limit=int)
    def get():
        """获取任务列表"""
        params = Response(
            job_name=get_arg('job_name', ''),
            start_time=int(get_arg('start_time', 0)),
            end_time=int(get_arg('end_time', 0)),
            interface_id=int(get_arg('interface_id', 0)),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取任务列表[params: %s]' % str(params))
        return params


class JobDetail(Resource):
    @staticmethod
    @JobFilter.filter_delete_data(result=int)
    @JobOperation.delete_job(job_id=int, user_id=int)
    @JobVerify.verify_delete_job(job_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(job_id=int)
    def delete(job_id):
        """删除任务"""
        params = Response(job_id=job_id)
        log.info('删除任务[params: %s]' % str(params))
        return params

    @staticmethod
    @JobFilter.filter_detail_data(result=dict)
    @JobOperation.get_job_detail(job_id=int)
    @JobVerify.verify_get_job_id(job_id=int)
    def get(job_id):
        """获取任务"""
        params = Response(job_id=job_id)
        log.info('获取任务[params: %s]' % str(params))
        return params

    @staticmethod
    @job_update_request
    @JobFilter.filter_update_data(job_id=int)
    @JobOperation.update_job_detail(job_id=int, interface_id=int, job_name=str, job_desc=str, server_id=int,
                                    server_dir=str, server_script=str, return_code=int, old_prep=str, job_prep=str,
                                    user_id=int, old_params=str, job_params=str, is_deleted=int)
    @JobVerify.verify_update_job_id(job_id=int, interface_id=int, job_name=str, job_desc=str, server_id=int,
                                    server_dir=str, server_script=str, return_code=int, old_prep=str, job_prep=str,
                                    user_id=int, old_params=str, job_params=str, is_deleted=int)
    @PermissionVerify.verify_write_permission(job_id=int, interface_id=int, job_name=str, job_desc=str, server_id=int,
                                              server_dir=str, server_script=str, return_code=int, old_prep=str,
                                              job_prep=str, old_params=str, job_params=str, is_deleted=int)
    def put(job_id):
        """修改任务"""
        payload = get_payload()
        params = Response(
            job_id=job_id,
            interface_id=int(payload.get('interface_id', 0)),
            job_name=payload.get('job_name', ''),
            job_desc=payload.get('job_desc', ''),
            server_id=int(payload.get('server_id', 0)),
            server_dir=payload.get('server_dir', ''),
            server_script=payload.get('server_script', ''),
            return_code=int(payload.get('return_code', 0)),
            old_prep=payload.get('old_prep', ''),
            job_prep=payload.get('job_prep', ''),
            old_params=payload.get('old_params', ''),
            job_params=payload.get('job_params', ''),
            is_deleted=int(payload.get('is_deleted', 0))
        )
        log.info('修改任务[params: %s]' % str(params))
        return params


class JobAdd(Resource):
    @staticmethod
    @job_add_request
    @JobFilter.filter_add_data(job_id=int)
    @JobOperation.add_job_detail(job_name=str, interface_id=int, job_desc=str, server_id=int, server_dir=str,
                                 job_prep=str, job_params=str, server_script=str, user_id=int, return_code=int)
    @JobVerify.verify_add_job_id(job_name=str, interface_id=int, job_desc=str, server_id=int, server_dir=str,
                                 job_prep=str, job_params=str, server_script=str, user_id=int, return_code=int)
    @PermissionVerify.verify_write_permission(job_name=str, interface_id=int, job_desc=str, server_id=int,
                                              job_prep=str, job_params=str, server_dir=str, server_script=str,
                                              return_code=int)
    def post():
        """新增任务"""
        payload = get_payload()
        params = Response(
            job_name=payload.get('job_name', ''),
            interface_id=int(payload.get('interface_id', 0)),
            job_prep=payload.get('job_prep', ''),
            job_params=payload.get('job_params', ''),
            job_desc=payload.get('job_desc', ''),
            server_id=int(payload.get('server_id', 0)),
            server_dir=payload.get('server_dir', ''),
            server_script=payload.get('server_script', ''),
            return_code=int(payload.get('return_code', 0))
        )
        log.info('新增任务[params: %s]' % str(params))
        return params


class JobListAll(Resource):
    @staticmethod
    @all_job_request
    @JobFilter.filter_get_all_data(result=list)
    @JobOperation.get_job_list_all(interface_id=int)
    def get():
        """获取所有任务"""
        params = Response(interface_id=int(get_arg('interface_id', 0)))
        log.info('获取所有任务[params: %s]' % str(params))
        return params


class JobExecute(Resource):
    @staticmethod
    @job_execute_request
    @JobFilter.filter_execute_job(status=bool)
    @JobOperation.execute_job(job_id=int, user_id=int)
    @JobVerify.verify_execute_job(job_id=int, user_id=int)
    @PermissionVerify.verify_execute_permission(job_id=int)
    def post():
        """立即执行任务"""
        payload = get_payload()
        params = Response(
            job_id=int(payload.get('job_id', 0))
        )
        log.info('立即执行任务[params: %s]' % str(params))
        return params


ns = api.namespace('job', description='任务')
ns.add_resource(JobList, '/list/api/')
ns.add_resource(JobDetail, '/detail/api/<int:job_id>/')
ns.add_resource(JobAdd, '/add/api/')
ns.add_resource(JobListAll, '/list/all/api/')
ns.add_resource(JobExecute, '/run/api/')
