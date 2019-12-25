# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import scheduler
from scheduler.distribute_scheduler import get_dispatch_job


def test(ftp_event_id):
    """测试任务"""
    print('测试任务: %s' % ftp_event_id)


class SchedulerHandler(object):
    """调度操作"""

    @staticmethod
    def add_job(run_id, dispatch_id, minute, hour, day, month, week):
        """添加任务"""
        scheduler.add_job(
            id=run_id,
            func=get_dispatch_job,
            args=(dispatch_id,),
            trigger='cron',
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            week=week
        )

    @staticmethod
    def add_event(run_id, ftp_event_id, minute, hour):
        """新增事件"""
        scheduler.add_job(
            id=run_id,
            func=test,
            args=(ftp_event_id,),
            trigger='cron',
            minute=minute,
            hour=hour,
        )

    @staticmethod
    def pause_job(run_id):
        """暂停任务"""
        scheduler.pause_job(run_id, jobstore='default')

    @staticmethod
    def resume_job(run_id):
        """恢复任务"""
        scheduler.resume_job(run_id, jobstore='default')

    @staticmethod
    def modify_job(run_id, dispatch_id, minute, hour, day, month, week):
        """修改任务"""
        scheduler.modify_job(
            id=run_id,
            jobstore='default',
            func=get_dispatch_job,
            args=(dispatch_id,),
            trigger='cron',
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            week=week
        )

    @staticmethod
    def modify_event(run_id, ftp_event_id, minute, hour):
        """修改事件"""
        scheduler.modify_job(
            id=run_id,
            jobstore='default',
            func=test,
            args=(ftp_event_id,),
            minute=minute,
            hour=hour
        )

    @staticmethod
    def run_job(run_id):
        """立即执行任务"""
        scheduler.run_job(id=run_id, jobstore='default')

    @staticmethod
    def remove_job(run_id):
        """删除任务"""
        scheduler.remove_job(id=run_id, jobstore='default')
