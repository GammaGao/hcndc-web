# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator


class ParamsFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """获取参数列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_add_data(param_id):
        """新增参数"""
        return {'status': 200, 'msg': '成功', 'data': {'param_id': param_id}}, 200

    @staticmethod
    @make_decorator
    def filter_detail_data(result):
        """获取参数详情"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_update_data(param_id):
        """修改参数详情"""
        return {'status': 200, 'msg': '成功', 'data': {'param_id': param_id}}, 200

    @staticmethod
    @make_decorator
    def filter_delete_data(param_id):
        """删除参数详情"""
        return {'status': 200, 'msg': '成功', 'data': {'param_id': param_id}}, 200

    @staticmethod
    @make_decorator
    def filter_test_data(result, msg, flag):
        """测试SQL参数"""
        if not flag:
            return {'status': 200, 'msg': msg, 'data': {'text': result}}, 200
        else:
            return {'status': 400, 'msg': msg, 'data': {'text': result}}, 200

    @staticmethod
    @make_decorator
    def filter_all_list_data(result):
        """获取所有参数"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_all_index_data(result):
        """获取所有参数目录"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200
