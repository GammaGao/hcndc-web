# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator


class ParamsFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """获取参数列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200
