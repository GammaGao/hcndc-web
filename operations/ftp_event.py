# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from configs import db, log
from models.ftp_event import FtpEventModel
from models.ftp import FtpModel
from scheduler.event_handler import EventHandler
from server.decorators import make_decorator, Response
from ftp_server.ftp import FtpLink
from ftp_server.sftp import SftpLink
from server.status import make_result
from scheduler.event_scheduler import get_event_job


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
            EventHandler.add_event(run_id, ftp_event_id, minute, hour)
        # 修改
        else:
            EventHandler.modify_event(run_id, ftp_event_id, minute, hour)
        # 先新增后暂停
        if old_status == 0 and new_status == 2:
            EventHandler.pause_job(run_id)
        # 暂停
        elif old_status == 1 and new_status == 2:
            EventHandler.pause_job(run_id)
        # 失效
        elif old_status == 1 and new_status == 0 or old_status == 2 and new_status == 0:
            EventHandler.remove_job(run_id)
        # 恢复
        elif old_status == 2 and new_status == 1:
            EventHandler.resume_job(run_id)
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
        EventHandler.add_event(run_id, ftp_event_id, minute, hour)
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

    @staticmethod
    @make_decorator
    def test_ftp_event_link(ftp_id, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd, data_path):
        """测试FTP文件目录是否存在"""
        if ftp_id:
            detail = FtpModel.get_ftp_detail(db.etl_db, ftp_id)
            if isinstance(detail['ftp_passwd'], bytes):
                detail['ftp_passwd'] = detail['ftp_passwd'].decode('utf-8', 'ignore')
            try:
                if detail['ftp_type'] == 1:
                    ftp = FtpLink(detail['ftp_host'], detail['ftp_port'], detail['ftp_user'], detail['ftp_passwd'])
                    FtpModel.update_ftp_status(db.etl_db, ftp_id, 0)
                    result = ftp.test_dir(data_path)
                    ftp.close()
                    if result:
                        return Response(status=200, msg='FTP文件目录存在')
                    else:
                        return Response(status=400, msg='FTP文件目录不存在')
                elif detail['ftp_type'] == 2:
                    ftp = SftpLink(detail['ftp_host'], detail['ftp_port'], detail['ftp_user'], detail['ftp_passwd'])
                    FtpModel.update_ftp_status(db.etl_db, ftp_id, 0)
                    result = ftp.test_dir(data_path)
                    ftp.close()
                    if result:
                        return Response(status=200, msg='FTP文件目录存在')
                    else:
                        return Response(status=400, msg='FTP文件目录不存在')
                else:
                    FtpModel.update_ftp_status(db.etl_db, ftp_id, 1)
                    return Response(status=400, msg='FTP服务器类型未知')
            except:
                FtpModel.update_ftp_status(db.etl_db, ftp_id, 1)
                return Response(status=400, msg='FTP连接异常')
        else:
            try:
                if ftp_type == 1:
                    ftp = FtpLink(ftp_host, ftp_port, ftp_user, ftp_passwd)
                    result = ftp.test_dir(data_path)
                    ftp.close()
                    if result:
                        return Response(status=200, msg='FTP文件目录存在')
                    else:
                        return Response(status=400, msg='FTP文件目录不存在')
                elif ftp_type == 2:
                    ftp = SftpLink(ftp_host, ftp_port, ftp_user, ftp_passwd)
                    result = ftp.test_dir(data_path)
                    ftp.close()
                    if result:
                        return Response(status=200, msg='FTP文件目录存在')
                    else:
                        return Response(status=400, msg='FTP文件目录不存在')
                else:
                    return Response(status=400, msg='FTP服务器类型未知')
            except:
                return Response(status=400, msg='FTP连接异常')

    @staticmethod
    @make_decorator
    def action_ftp_event(ftp_event_id, action, user_id):
        """暂停/恢复调度事件"""
        for item in ftp_event_id:
            try:
                run_id = 'ftp_event_%s' % item
                # 暂停调度任务
                if action == 1:
                    FtpEventModel.update_ftp_event_status(db.etl_db, item, 2, user_id)
                    EventHandler.pause_job(run_id)
                # 恢复调度任务
                elif action == 2:
                    FtpEventModel.update_ftp_event_status(db.etl_db, item, 1, user_id)
                    EventHandler.resume_job(run_id)
            except Exception as e:
                log.error('暂停/恢复调度异常 [ERROR: %s]' % e, exc_info=True)
                abort(400, **make_result(status=400, msg='暂停/恢复调度任务异常'))
        return Response(ftp_event_id=ftp_event_id)

    @staticmethod
    @make_decorator
    def delete_ftp_event(ftp_event_id):
        """删除调度详情"""
        for item in ftp_event_id:
            try:
                run_id = 'ftp_event_%s' % item
                detail = FtpEventModel.get_ftp_event_detail(db.etl_db, item)
                FtpEventModel.delete_ftp_event_detail(db.etl_db, item)
                FtpEventModel.delete_file_event_interface(db.etl_db, item)
                if detail['status'] != 0:
                    EventHandler.remove_job(run_id)
            except Exception as e:
                log.error('删除调度异常[ERROR: %s]' % e, exc_info=True)
                abort(400, **make_result(status=400, msg='删除调度错误, 该调度不存在'))
        return Response(ftp_event_id=ftp_event_id)

    @staticmethod
    @make_decorator
    def run_ftp_event(ftp_event_id, run_date, date_format):
        """立即执行调度"""
        for item in ftp_event_id:
            try:
                get_event_job(item, 2, run_date, date_format)
            except Exception as e:
                log.error('立即执行调度异常 [ERROR: %s]' % e, exc_info=True)
                abort(400, **make_result(status=400, msg='立即执行调度异常'))
        return Response(dispatch_id=ftp_event_id)