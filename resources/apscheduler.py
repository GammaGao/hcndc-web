# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import redirect

from document.apscheduler import *
from flask_restplus.resource import Resource


class SchedulerInfo(Resource):
    @staticmethod
    def get():
        """APScheduler对象信息"""
        return redirect('/scheduler')


class SchedulerJobs(Resource):
    @staticmethod
    def get():
        """获取任务列表"""
        return redirect('/scheduler/jobs')

    @staticmethod
    @scheduler_add_request
    def post():
        """新增调度任务"""
        return redirect('/scheduler/jobs')


class SchedulerDetail(Resource):
    @staticmethod
    def get(job_id):
        """获取调度详情"""
        return redirect('/scheduler/jobs/%s' % job_id)

    @staticmethod
    def delete(job_id):
        """删除调度"""
        return redirect('/scheduler/jobs/%s' % job_id)

    @staticmethod
    def patch(job_id):
        """修改调度"""
        return redirect('/scheduler/jobs/%s' % job_id)


class SchedulerPause(Resource):
    @staticmethod
    def post(job_id):
        """暂停调度"""
        return redirect('/scheduler/jobs/%s/pause' % job_id)


class SchedulerResume(Resource):
    @staticmethod
    def post(job_id):
        """恢复调度"""
        return redirect('/scheduler/jobs/%s/resume' % job_id)


class SchedulerRun(Resource):
    @staticmethod
    def post(job_id):
        """执行调度"""
        return redirect('/scheduler/jobs/%s/run' % job_id)


ns = api.namespace('apscheduler', description='APScheduler接口映射')
ns.add_resource(SchedulerInfo, '')
ns.add_resource(SchedulerJobs, '/jobs')
ns.add_resource(SchedulerDetail, '/jobs/<job_id>')
ns.add_resource(SchedulerPause, '/jobs/<job_id>/pause')
ns.add_resource(SchedulerResume, '/jobs/<job_id>/resume')
ns.add_resource(SchedulerRun, '/jobs/<job_id>/run')
