# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import croniter
import datetime
import pymysql
from flask_restful import abort

from configs import db, log
from models.dispatch import DispatchModel, DispatchAlertModel
from scheduler.handler import SchedulerHandler
from server.decorators import make_decorator, Response
from server.status import make_result
from models.schedule import ScheduleModel


class DispatchOperation(object):
    @staticmethod
    @make_decorator
    def crontab_next_time(sched, time_format='%Y-%m-%d %H:%M:%S', query_times=10):
        """计算定时任务下次运行时间"""
        try:
            now = datetime.datetime.now()
            # 以当前时间为基准开始计算
            cron = croniter.croniter(sched, now)
            result = [cron.get_next(datetime.datetime).strftime(time_format) for _ in range(query_times)]
        except Exception as e:
            log.error('计算cron表达式异常 [ERROR: %s]' % e, exc_info=True)
            result = ['计算cron表达式异常']
        return Response(run_times=result)

    @staticmethod
    @make_decorator
    def add_dispatch_detail(interface_id, dispatch_name, dispatch_desc, minute, hour, day, month, week, user_id):
        """新增调度"""
        try:
            # 新增调度表
            dispatch_id = DispatchModel.add_dispatch_detail(db.etl_db, interface_id, dispatch_name, dispatch_desc,
                                                            minute, hour, day, month, week, user_id)
            # 添加调度任务
            run_id = 'scheduler_%s' % dispatch_id
            SchedulerHandler.add_job(run_id, dispatch_id, minute, hour, day, month, week)
            return Response(dispatch_id=dispatch_id)
        except pymysql.err.IntegrityError as e:
            log.error('请勿重复为任务流添加调度 [ERROR: %s]' % e, exc_info=True)
            abort(400, **make_result(status=400, msg='请勿重复为任务流添加调度'))

    @staticmethod
    @make_decorator
    def get_dispatch_list(interface_id, dispatch_name, status, page, limit):
        """获取调度列表"""
        condition = []
        if interface_id:
            condition.append('interface_id = %s' % interface_id)
        if dispatch_name:
            condition.append('dispatch_name LIKE "%%%%%s%%%%"' % dispatch_name)
        if status == 1:
            condition.append('status = 0')
        elif status == 2:
            condition.append('status = 1')
        elif status == 3:
            condition.append('status = 2')
        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''
        result = DispatchModel.get_dispatch_list(db.etl_db, condition, page, limit)
        total = DispatchModel.get_dispatch_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_dispatch_detail(dispatch_id):
        """获取调度详情"""
        result = DispatchModel.get_dispatch_detail(db.etl_db, dispatch_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def delete_dispatch_detail(dispatch_id, user_id):
        """删除调度详情"""
        for item in dispatch_id:
            try:
                run_id = 'scheduler_%s' % item
                DispatchModel.update_dispatch_status(db.etl_db, item, 0, user_id)
                SchedulerHandler.remove_job(run_id)
            except Exception as e:
                log.error('删除调度异常[ERROR: %s]' % e, exc_info=True)
                abort(400, **make_result(status=400, msg='删除调度异常'))
        return Response(dispatch_id=dispatch_id)

    @staticmethod
    @make_decorator
    def update_dispatch_detail(dispatch_id, interface_id, dispatch_name, dispatch_desc, minute, hour, day, month,
                               week, old_status, new_status, user_id):
        """修改调度详情"""
        try:
            # 修改调度表
            DispatchModel.update_dispatch_detail(db.etl_db, dispatch_id, interface_id, dispatch_name, dispatch_desc,
                                                 minute, hour, day, month, week, new_status, user_id)
            # 修改调度状态
            run_id = 'scheduler_%s' % dispatch_id
            # 仍删除
            if old_status == 0 and new_status == 0:
                pass
            # 新增 or 先新增后暂停
            elif old_status == 0 and new_status == 1 or old_status == 0 and new_status == 2:
                SchedulerHandler.add_job(run_id, dispatch_id, minute, hour, day, month, week)
            # 修改
            else:
                SchedulerHandler.modify_job(run_id, dispatch_id, minute, hour, day, month, week)
            # 先新增后暂停
            if old_status == 0 and new_status == 2:
                SchedulerHandler.pause_job(run_id)
            # 暂停
            elif old_status == 1 and new_status == 2:
                SchedulerHandler.pause_job(run_id)
            # 删除
            elif old_status == 1 and new_status == 0 or old_status == 2 and new_status == 0:
                SchedulerHandler.remove_job(run_id)
            # 恢复
            elif old_status == 2 and new_status == 1:
                SchedulerHandler.resume_job(run_id)

            return Response(dispatch_id=dispatch_id)
        except pymysql.err.IntegrityError as e:
            log.error('请勿重复为任务流添加调度 [ERROR: %s]' % e, exc_info=True)
            abort(400, **make_result(status=400, msg='请勿重复为任务流添加调度'))

    @staticmethod
    @make_decorator
    def run_dispatch(dispatch_id):
        """立即执行调度"""
        for item in dispatch_id:
            run_id = 'scheduler_%s' % item
            try:
                SchedulerHandler.run_job(run_id)
            except Exception as e:
                log.error('立即执行调度异常 [ERROR: %s]' % e, exc_info=True)
                abort(400, **make_result(status=400, msg='立即执行调度异常'))
        return Response(dispatch_id=dispatch_id)

    @staticmethod
    @make_decorator
    def action_dispatch(dispatch_id, action, user_id):
        """暂停/恢复调度任务"""
        for item in dispatch_id:
            try:
                run_id = 'scheduler_%s' % item
                # 暂停调度任务
                if action == 1:
                    DispatchModel.update_dispatch_status(db.etl_db, item, 2, user_id)
                    SchedulerHandler.pause_job(run_id)
                # 恢复调度任务
                elif action == 2:
                    DispatchModel.update_dispatch_status(db.etl_db, item, 1, user_id)
                    SchedulerHandler.resume_job(run_id)
            except Exception as e:
                log.error('暂停/恢复调度异常 [ERROR: %s]' % e, exc_info=True)
                abort(400, **make_result(status=400, msg='暂停/恢复调度任务异常'))
        return Response(dispatch_id=dispatch_id)


class DispatchAlertOperation(object):
    @staticmethod
    @make_decorator
    def add_dispatch_alert(dispatch_id, alert_s, alert_f, conf_id_s, conf_id_f, user_id, send_mail_s, send_mail_f):
        """新增调度预警"""
        data = []
        if alert_s:
            data.append({
                'dispatch_id': dispatch_id,
                'config_id': conf_id_s,
                'alert_type': 1,
                'user_id': user_id,
                'send_mail': send_mail_s
            })
        if alert_f:
            data.append({
                'dispatch_id': dispatch_id,
                'config_id': conf_id_f,
                'alert_type': 2,
                'user_id': user_id,
                'send_mail': send_mail_f,
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
        # 批处理
        DispatchAlertModel.add_dispatch_alert(db.etl_db, data)
        return Response(dispatch_id=dispatch_id)

    @staticmethod
    @make_decorator
    def get_dispatch_alert_detail(dispatch_id):
        """获取调度预警详情"""
        result = DispatchAlertModel.get_dispatch_alert_detail(db.etl_db, dispatch_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_dispatch_alert_detail(dispatch_id, alert_s, alert_f, alert_id_s, alert_id_f, conf_id_s, conf_id_f,
                                     user_id, send_mail_s, send_mail_f):
        """修改执行流预警"""
        # 新增
        insert_data = []
        # 成功配置
        if alert_id_s < 0 and alert_s:
            insert_data.append({
                'dispatch_id': dispatch_id,
                'config_id': conf_id_s,
                'alert_type': 1,
                'user_id': user_id,
                'send_mail': send_mail_s,
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
        # 失败配置
        if alert_id_f < 0 and alert_f:
            insert_data.append({
                'dispatch_id': dispatch_id,
                'config_id': conf_id_f,
                'alert_type': 2,
                'user_id': user_id,
                'send_mail': send_mail_f,
                'insert_time': int(time.time()),
                'update_time': int(time.time())
            })
        # 修改/启用/关闭
        update_data = []
        if alert_id_s > 0:
            update_data.append({
                'id': alert_id_s,
                'config_id': conf_id_s,
                'alert_type': 1,
                'send_mail': send_mail_s,
                'user_id': user_id,
                'is_deleted': 0 if alert_s else 1,
                'update_time': int(time.time())
            })
        if alert_id_f > 0:
            update_data.append({
                'id': alert_id_f,
                'config_id': conf_id_f,
                'alert_type': 2,
                'send_mail': send_mail_f,
                'user_id': user_id,
                'is_deleted': 0 if alert_f else 1,
                'update_time': int(time.time())
            })
        # 批处理
        if insert_data:
            DispatchAlertModel.add_dispatch_alert(db.etl_db, insert_data)
        if update_data:
            DispatchAlertModel.update_dispatch_alert_detail(db.etl_db, update_data)

        return Response(dispatch_id=dispatch_id)
