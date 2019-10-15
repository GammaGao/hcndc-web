# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator, Response
from models.base import ExecHostModel, AlertModel
from configs import db, config, log
from server.status import make_result
from rpc.rpc_client import Connection

import json
import time
from flask_restful import abort


class ExecHostOperation(object):
    @staticmethod
    @make_decorator
    def get_exec_host_list(server_name, server_host, is_deleted, page, limit):
        """获取执行服务器列表"""
        condition = []
        if server_name:
            condition.append('server_name LIKE "%%%%%s%%%%"' % server_name)
        if server_host:
            condition.append('server_host LIKE "%%%%%s%%%%"' % server_host)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''
        result = ExecHostModel.get_exec_host_list(db.etl_db, condition, page, limit)
        total = ExecHostModel.get_exec_host_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_exec_host_detail(server_id):
        """获取执行服务器详情"""
        result = ExecHostModel.get_exec_host_detail(db.etl_db, server_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_exec_host_detail(server_id, server_host, server_name, is_deleted, user_id):
        """修改执行服务器详情"""
        # 是否存在调度任务中
        # run_job_count = ExecHostModel.get_exec_host_in_dispatch_job(db.etl_db, server_id)
        # if run_job_count:
        #     abort(400, **make_result(status=400, msg='调度任务中有%s个任务使用该执行服务器, 请停止调度任务后修改删除' % run_job_count))
        ExecHostModel.update_exec_host_detail(db.etl_db, server_id, server_host, server_name, is_deleted, user_id)
        return Response(server_id=server_id)

    @staticmethod
    @make_decorator
    def delete_exec_host_detail(server_id, user_id):
        """删除执行服务器"""
        # 是否存在调度任务中
        # run_job_count = ExecHostModel.get_exec_host_in_dispatch_job(db.etl_db, server_id)
        # if run_job_count:
        #     abort(400, **make_result(status=400, msg='调度任务中有%s个任务使用该执行服务器, 请停止调度后删除' % run_job_count))
        ExecHostModel.delete_exec_host_detail(db.etl_db, server_id, user_id)
        return Response(server_id=server_id)

    @staticmethod
    @make_decorator
    def test_exec_host(server_host):
        """测试执行服务器"""
        # 服务器状态
        host_item = ExecHostModel.get_exec_host_status_by_host(db.etl_db, server_host)
        try:
            # rpc调用
            client = Connection(server_host, config.exec.port)
            result = json.loads(client.rpc.test())
            # 不存在跳过
            if not host_item:
                pass
            # 新增服务器状态
            elif host_item['server_id'] and not host_item['status_id']:
                now_time = int(time.time())
                ExecHostModel.add_exec_host_status_by_host_success(db.etl_db, host_item['server_id'], result['cpu'],
                                                                   result['system'], result['disk']['used'],
                                                                   result['disk']['total'], result['memory']['used'],
                                                                   result['memory']['total'], now_time, 0)
            # 修改服务器状态
            elif host_item['server_id'] and host_item['status_id']:
                now_time = int(time.time())
                ExecHostModel.update_exec_host_status_by_host_success(db.etl_db, host_item['server_id'], result['cpu'],
                                                                      result['system'], result['disk']['used'],
                                                                      result['disk']['total'], result['memory']['used'],
                                                                      result['memory']['total'], now_time, 0)
            return Response(result=result)
        except Exception as e:
            # 不存在跳过
            if not host_item:
                pass
            # 新增服务器状态
            elif host_item['server_id'] and not host_item['status_id']:
                now_time = int(time.time())
                ExecHostModel.add_exec_host_status_by_host_failed(db.etl_db, host_item['server_id'], now_time, 1)
            # 修改服务器状态
            elif host_item['server_id'] and host_item['status_id']:
                now_time = int(time.time())
                ExecHostModel.update_exec_host_status_by_host_failed(db.etl_db, host_item['server_id'], now_time, 1)
            log.error('执行服务器连通失败, [server_host: %s]' % server_host, exc_info=1)
            abort(403, **make_result(status=403, msg='服务器连通失败: [ERROR: %s]' % e))

    @staticmethod
    @make_decorator
    def add_exec_host(server_host, server_name, user_id):
        """新增执行服务器"""
        host_id = ExecHostModel.add_exec_host_detail(db.etl_db, server_host, server_name, user_id)
        return Response(host_id=host_id)

    @staticmethod
    @make_decorator
    def get_exec_host_status(server_host, server_name, page, limit):
        """获取执行服务器状态"""
        condition = []
        if server_name:
            condition.append('server_name LIKE "%%%%%s%%%%"' % server_name)
        if server_host:
            condition.append('server_host LIKE "%%%%%s%%%%"' % server_host)
        condition = ' AND ' + ' AND '.join(condition) if condition else ''
        result = ExecHostModel.get_exec_host_status(db.etl_db, condition, page, limit)
        total = ExecHostModel.get_exec_host_status_count(db.etl_db, condition)
        return Response(result=result, total=total)


class AlertOperation(object):
    @staticmethod
    @make_decorator
    def get_alert_list(alert_channel, conf_name, is_deleted, page, limit):
        """获取预警配置列表"""
        condition = []
        if conf_name:
            condition.append('conf_name LIKE "%%%%%s%%%%"' % conf_name)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')
        if alert_channel == 1:
            condition.append('alert_channel = 1')
        elif alert_channel == 2:
            condition.append('alert_channel = 2')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''
        result = AlertModel.get_alert_conf_list(db.etl_db, condition, page, limit)
        total = AlertModel.get_alert_conf_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_alert_list_all():
        """获取预警配置列表(全)"""
        result = AlertModel.get_alert_conf_list_all(db.etl_db)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def delete_alert_detail(conf_id, user_id):
        """删除预警配置"""
        run_dispatch_count = AlertModel.get_alert_in_dispatch(db.etl_db, conf_id)
        if run_dispatch_count:
            abort(400, **make_result(status=400, msg='调度任务中有%s个任务使用该预警配置, 请停止调度后删除' % run_dispatch_count))
        AlertModel.delete_alert_config(db.etl_db, conf_id, user_id)
        return Response(conf_id=conf_id)

    @staticmethod
    @make_decorator
    def get_alert_detail_detail(conf_id):
        """获取预警配置"""
        result = AlertModel.get_alert_config_detail(db.etl_db, conf_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_alert_detail(conf_id, alert_channel, conf_name, param_config, param_host, param_port, param_pass,
                            is_deleted, user_id):
        """修改预警配置"""
        run_dispatch_count = AlertModel.get_alert_in_dispatch(db.etl_db, conf_id)
        if run_dispatch_count:
            abort(400, **make_result(status=400, msg='调度任务中有%s个任务使用该预警配置, 请停止调度后修改' % run_dispatch_count))
        AlertModel.update_alert_config_detail(db.etl_db, conf_id, alert_channel, conf_name, param_config, param_host,
                                              param_port, param_pass, is_deleted, user_id)
        return Response(conf_id=conf_id)

    @staticmethod
    @make_decorator
    def add_alert_detail(alert_channel, conf_name, param_config, param_host, param_port, param_pass, user_id):
        """新增预警配置"""
        conf_id = AlertModel.add_alert_config_detail(db.etl_db, alert_channel, conf_name, param_config, param_host,
                                                     param_port, param_pass, user_id)
        return Response(conf_id=conf_id)
