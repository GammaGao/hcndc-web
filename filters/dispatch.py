# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from server.decorators import make_decorator


class DispatchFilter(object):
    @staticmethod
    @make_decorator
    def filter_cron_data(run_times):
        """crontab查询"""
        return {'status': 200, 'msg': '成功', 'data': run_times}, 200

    @staticmethod
    @make_decorator
    def filter_add_dispatch(dispatch_id):
        """添加调度"""
        return {'status': 200, 'msg': '成功', 'data': {'id': dispatch_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_dispatch(result, total):
        """获取调度列表"""
        for item in result:
            cron_expr = [item.pop('minute'), item.pop('hour'), item.pop('day'), item.pop('month'), item.pop('week')]
            item['cron_expr'] = ' '.join(cron_expr)
            if item['next_run_time']:
                item['next_run_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['next_run_time']))
            else:
                item['next_run_time'] = ''
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_get_dispatch_detail(result):
        """获取调度详情"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_delete_dispatch_detail(dispatch_id):
        """删除调度详情"""
        return {'status': 200, 'msg': '成功', 'data': {'id': dispatch_id}}, 200

    @staticmethod
    @make_decorator
    def filter_update_dispatch_detail(dispatch_id):
        """修改调度详情"""
        return {'status': 200, 'msg': '成功', 'data': {'id': dispatch_id}}, 200

    @staticmethod
    @make_decorator
    def filter_run_dispatch(dispatch_id):
        """立即执行调度任务"""
        return {'status': 200, 'msg': '成功', 'data': {'id': dispatch_id}}, 200

    @staticmethod
    @make_decorator
    def filter_action_dispatch(dispatch_id):
        """暂停/恢复调度任务"""
        return {'status': 200, 'msg': '成功', 'data': {'id': dispatch_id}}, 200


class DispatchAlertFilter(object):
    @staticmethod
    @make_decorator
    def filter_add_dispatch_alert(dispatch_id):
        """新增调度预警"""
        return {'status': 200, 'msg': '成功', 'data': {'id': dispatch_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_dispatch_alert_detail(result):
        """获取调度预警详情"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_update_dispatch_alert(dispatch_id):
        """修改调度预警详情"""
        return {'status': 200, 'msg': '成功', 'data': {'id': dispatch_id}}, 200
