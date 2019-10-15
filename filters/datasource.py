# !/usr/bin/env python
# -*- coding: utf-8 -*-

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
    def filter_add_data(datasource_id):
        """新增数据源"""
        return {'status': 200, 'msg': '成功', 'data': {'datasource_id': datasource_id}}, 200
