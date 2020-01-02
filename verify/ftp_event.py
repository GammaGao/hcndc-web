# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result
from util.time_format import date_add


class FtpEventVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_ftp_event_list(event_name, status, page, limit):
        """获取文件事件列表"""
        if status < 0 or status > 3:
            abort(400, **make_result(status=400, msg='调度状态参数错误'))
        return Response(event_name=event_name, status=status, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_ftp_event_detail(ftp_event_id):
        """获取文件事件详情"""
        if not ftp_event_id:
            abort(400, **make_result(status=400, msg='调度id不存在'))
        return Response(ftp_event_id=ftp_event_id)

    @staticmethod
    @make_decorator
    def verify_update_ftp_event_detail(ftp_event_id, event_name, event_desc, ftp_id, data_path, file_name, interface_id,
                                       start_time, end_time, date_time, interval_value, old_status, new_status,
                                       user_id):
        """修改文件事件详情"""
        if not ftp_event_id:
            abort(400, **make_result(status=400, msg='事件id不存在'))
        if not event_name:
            abort(400, **make_result(status=400, msg='事件名称不存在'))
        if not ftp_id:
            abort(400, **make_result(status=400, msg='FTP配置id不存在'))
        if not data_path:
            abort(400, **make_result(status=400, msg='文件路径不存在'))
        if not file_name:
            abort(400, **make_result(status=400, msg='文件名称不存在'))
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流id不存在'))
        if not interval_value:
            abort(400, **make_result(status=400, msg='间隔值不得为空'))
        if interval_value < 1 or interval_value > 60:
            abort(400, **make_result(status=400, msg='间隔值应在1-60分钟之间'))
        if not date_time:
            now = time.strftime('%Y-%m-%d', time.localtime())
            date_time = date_add(now, -1)
        if start_time < 0 or start_time > 23:
            abort(400, **make_result(status=400, msg='开始时间错误'))
        if end_time < 1 or end_time > 24:
            abort(400, **make_result(status=400, msg='结束时间错误'))
        if end_time <= start_time:
            abort(400, **make_result(status=400, msg='结束时间不得小于等于开始时间'))
        if old_status < 0 or old_status > 2:
            abort(400, **make_result(status=400, msg='是否失效参数错误(旧)'))
        if new_status < 0 or new_status > 2:
            abort(400, **make_result(status=400, msg='是否失效参数错误(新)'))
        if not user_id:
            abort(400, **make_result(status=400, msg='用户不存在'))
        return Response(ftp_event_id=ftp_event_id, event_name=event_name, event_desc=event_desc, ftp_id=ftp_id,
                        data_path=data_path, file_name=file_name, interface_id=interface_id,
                        interval_value=interval_value, start_time=start_time, end_time=end_time, old_status=old_status,
                        date_time=date_time, new_status=new_status, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_add_ftp_event_detail(event_name, event_desc, ftp_id, data_path, file_name, interface_id, start_time,
                                    end_time, date_time, interval_value, user_id):
        """新增文件事件详情"""
        if not event_name:
            abort(400, **make_result(status=400, msg='事件名称不存在'))
        if not ftp_id:
            abort(400, **make_result(status=400, msg='FTP配置id不存在'))
        if not data_path:
            abort(400, **make_result(status=400, msg='文件路径不存在'))
        if not file_name:
            abort(400, **make_result(status=400, msg='文件名称不存在'))
        if not interface_id:
            abort(400, **make_result(status=400, msg='任务流id不存在'))
        if not interval_value:
            abort(400, **make_result(status=400, msg='间隔值不得为空'))
        if interval_value < 1 or interval_value > 60:
            abort(400, **make_result(status=400, msg='间隔值应在1-60分钟之间'))
        if not date_time:
            now = time.strftime('%Y-%m-%d', time.localtime())
            date_time = date_add(now, -1)
        if start_time < 0 or start_time > 23:
            abort(400, **make_result(status=400, msg='开始时间错误'))
        if end_time < 1 or end_time > 24:
            abort(400, **make_result(status=400, msg='结束时间错误'))
        if end_time <= start_time:
            abort(400, **make_result(status=400, msg='结束时间不得小于等于开始时间'))
        if not user_id:
            abort(400, **make_result(status=400, msg='用户不存在'))
        return Response(event_name=event_name, event_desc=event_desc, ftp_id=ftp_id, data_path=data_path,
                        file_name=file_name, interface_id=interface_id, interval_value=interval_value,
                        start_time=start_time, end_time=end_time, date_time=date_time, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_test_ftp_event_link(ftp_id, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd, data_path):
        """测试FTP文件目录是否存在"""
        if not data_path:
            abort(400, **make_result(status=400, msg='文件路径不得为空'))
        if not ftp_id and (not ftp_type and not ftp_host and not ftp_port):
            abort(400, **make_result(status=400, msg='FTP配置项缺失'))
        return Response(ftp_id=ftp_id, ftp_type=ftp_type, ftp_host=ftp_host, ftp_port=ftp_port, ftp_user=ftp_user,
                        ftp_passwd=ftp_passwd, data_path=data_path)

    @staticmethod
    @make_decorator
    def verify_action_ftp_event(ftp_event_id, action, user_id):
        """暂停/恢复调度事件"""
        if not ftp_event_id:
            abort(400, **make_result(status=400, msg='调度事件id不存在'))
        if action < 1 or action > 2:
            abort(400, **make_result(status=400, msg='请求参数错误'))
        return Response(ftp_event_id=ftp_event_id, action=action, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_delete_ftp_event(ftp_event_id, user_id):
        """删除调度详情"""
        if not ftp_event_id:
            abort(400, **make_result(status=400, msg='调度事件id不存在'))
        return Response(ftp_event_id=ftp_event_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_run_ftp_event(ftp_event_id, run_date, date_format):
        """立即执行调度事件"""
        if not ftp_event_id:
            abort(400, **make_result(status=400, msg='调度id不存在'))
        return Response(ftp_event_id=ftp_event_id, run_date=run_date, date_format=date_format)
