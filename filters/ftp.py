# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator


class FtpFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """FTP配置列表"""
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_test_data(status, msg):
        """测试FTP连接"""
        return {'status': status, 'msg': msg, 'data': {}}, 200
