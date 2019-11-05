# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator


class JobFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """任务列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_delete_data(result):
        """删除任务"""
        return {'status': 200, 'msg': '成功', 'data': {'id': result}}, 200

    @staticmethod
    @make_decorator
    def filter_detail_data(result):
        """任务详情"""
        if result['prep_id']:
            result['prep_id'] = list(result['prep_id'].split(','))
        else:
            result['prep_id'] = []
        if result['param_id']:
            result['param_id'] = list(result['param_id'].split(','))
        else:
            result['param_id'] = []
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_update_data(job_id):
        """任务修改"""
        return {'status': 200, 'msg': '成功', 'data': {'id': job_id}}, 200

    @staticmethod
    @make_decorator
    def filter_add_data(job_id):
        """新增任务"""
        return {'status': 200, 'msg': '成功', 'data': {'id': job_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_all_data(result):
        """获取所有任务列表"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_execute_job(status, msg):
        """立即执行任务"""
        if status:
            return {'status': 200, 'msg': '成功', 'data': {'content': '已成功分发执行任务'}}, 200
        return {'status': 200, 'msg': msg, 'data': {'content': '分发执行任务失败'}}, 400
