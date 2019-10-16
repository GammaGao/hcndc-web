# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from server.decorators import make_decorator


class DataSourceFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """获取数据源列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_test_data(tag, msg):
        """测试数据源连接"""
        if tag:
            return {'status': 200, 'msg': msg, 'data': {}}, 200
        else:
            return {'status': 400, 'msg': msg, 'data': {}}, 200

    @staticmethod
    @make_decorator
    def filter_add_data(source_id):
        """新增数据源"""
        return {'status': 200, 'msg': '成功', 'data': {'source_id': source_id}}, 200

    @staticmethod
    @make_decorator
    def filter_delete_data(source_id):
        """删除数据源"""
        return {'status': 200, 'msg': '成功', 'data': {'source_id': source_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_detail_data(result):
        """获取数据源详情"""
        if result:
            result['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['insert_time']))
            result['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['update_time']))
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_update_data(source_id):
        """修改数据源"""
        return {'status': 200, 'msg': '成功', 'data': {'source_id': source_id}}, 200
