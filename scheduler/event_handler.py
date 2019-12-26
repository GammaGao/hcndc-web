# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import scheduler
from scheduler.event_scheduler import get_event_job


class EventHandler(object):
    @staticmethod
    def add_event(run_id, ftp_event_id, minute, hour):
        """新增事件"""
        scheduler.add_job(
            id=run_id,
            func=get_event_job,
            args=(ftp_event_id,),
            trigger='cron',
            minute=minute,
            hour=hour,
        )

    @staticmethod
    def modify_event(run_id, ftp_event_id, minute, hour):
        """修改事件"""
        scheduler.modify_job(
            id=run_id,
            jobstore='default',
            func=get_event_job,
            args=(ftp_event_id,),
            trigger='cron',
            minute=minute,
            hour=hour
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
    def run_job(run_id):
        """立即执行任务"""
        scheduler.run_job(id=run_id, jobstore='default')

    @staticmethod
    def remove_job(run_id):
        """删除任务"""
        scheduler.remove_job(id=run_id, jobstore='default')
