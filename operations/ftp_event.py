# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from configs import db, log
from models.ftp_event import FtpEventModel
from scheduler.handler import SchedulerHandler
from scheduler.distribute_scheduler import get_dispatch_job
from server.decorators import make_decorator, Response
from server.status import make_result


class FtpEventOperation(object):
    @staticmethod
    @make_decorator
    def get_ftp_event_list(event_name, status, page, limit):
        """获取文件事件列表"""
        condition = []
        if event_name:
            condition.append('event_name LIKE "%%%%%s%%%%"' % event_name)
        if status == 1:
            condition.append('status = 0')
        elif status == 2:
            condition.append('status = 1')
        elif status == 3:
            condition.append('status = 2')
        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''
        result = FtpEventModel.get_ftp_event_list(db.etl_db, condition, page, limit)
        total = FtpEventModel.get_ftp_event_list_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_ftp_event_detail(ftp_event_id):
        """获取文件事件详情"""
        # 文件事件详情
        result = FtpEventModel.get_ftp_event_detail(db.etl_db, ftp_event_id)
        # 事件中任务流
        result['interface_id'] = FtpEventModel.get_ftp_event_interface(db.etl_db, ftp_event_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_ftp_event_detail(ftp_event_id, event_name, event_desc, ftp_id, data_path, file_name, interface_id,
                                start_time, end_time, date_time, interval_value, old_status, new_status, user_id):
        """修改文件事件详情"""
        # 修改事件详情
        FtpEventModel.update_ftp_event_detail(db.etl_db, ftp_event_id, event_name, event_desc, ftp_id, data_path,
                                              file_name, interval_value, start_time, end_time, date_time, new_status,
                                              user_id)
        # 修改任务流依赖
        interface_id = interface_id.split(',')
        insert_data = []
        for item in interface_id:
            insert_data.append({
                'ftp_event_id': ftp_event_id,
                'interface_id': item
            })
        FtpEventModel.delete_file_event_interface(db.etl_db, ftp_event_id)
        FtpEventModel.add_file_event_interface(db.etl_db, insert_data)
        # 修改文件事件状态
        run_id = 'ftp_event_%s' % ftp_event_id
        minute = '*/%s' % interval_value
        hour = '%d-%d' % (start_time, end_time)
        # 新增调度
        # 仍失效
        if old_status == 0 and new_status == 0:
            pass
        # 新增 or 先新增后暂停
        elif old_status == 0 and new_status == 1 or old_status == 0 and new_status == 2:
            SchedulerHandler.add_event(run_id, ftp_event_id, minute, hour)
        # 修改
        else:
            SchedulerHandler.modify_event(run_id, ftp_event_id, minute, hour)
        # 先新增后暂停
        if old_status == 0 and new_status == 2:
            SchedulerHandler.pause_job(run_id)
        # 暂停
        elif old_status == 1 and new_status == 2:
            SchedulerHandler.pause_job(run_id)
        # 失效
        elif old_status == 1 and new_status == 0 or old_status == 2 and new_status == 0:
            SchedulerHandler.remove_job(run_id)
        # 恢复
        elif old_status == 2 and new_status == 1:
            SchedulerHandler.resume_job(run_id)
        return Response(ftp_event_id=ftp_event_id)

    @staticmethod
    @make_decorator
    def add_ftp_event_detail(event_name, event_desc, ftp_id, data_path, file_name, interface_id, start_time, end_time,
                             date_time, interval_value, user_id):
        """新增文件事件详情"""
        # 新增事件详情
        ftp_event_id = FtpEventModel.add_ftp_event_detail(db.etl_db, event_name, event_desc, ftp_id, data_path,
                                                          file_name, interval_value, start_time, end_time, date_time,
                                                          user_id)
        # 新增调度
        run_id = 'ftp_event_%s' % ftp_event_id
        minute = '*/%s' % interval_value
        hour = '%d-%d' % (start_time, end_time)
        SchedulerHandler.add_event(run_id, ftp_event_id, minute, hour)
        # 新增任务流依赖
        interface_id = interface_id.split(',')
        insert_data = []
        for item in interface_id:
            insert_data.append({
                'ftp_event_id': ftp_event_id,
                'interface_id': item
            })
        FtpEventModel.add_file_event_interface(db.etl_db, insert_data)
        return Response(ftp_event_id=ftp_event_id)
