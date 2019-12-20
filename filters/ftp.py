# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from server.decorators import make_decorator


class FtpFilter(object):
    @staticmethod
    @make_decorator
    def filter_list_data(result, total):
        """FTP配置列表"""
        for item in result:
            item['last_ping_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['last_ping_time']))
        return {'status': 200, 'msg': '成功', 'total': total, 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_test_data(status, msg):
        """测试FTP连接"""
        return {'status': status, 'msg': msg, 'data': {}}, 200

    @staticmethod
    @make_decorator
    def filter_add_data(ftp_id):
        """新增FTP详情"""
        return {'status': 200, 'msg': '成功', 'data': {'ftp_id': ftp_id}}, 200

    @staticmethod
    @make_decorator
    def filter_delete_data(ftp_id):
        """删除FTP配置详情"""
        return {'status': 200, 'msg': '成功', 'data': {'ftp_id': ftp_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_detail_data(result):
        """获取FTP配置详情"""
        if result:
            result['last_ping_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['last_ping_time']))
            result['insert_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['insert_time']))
            result['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['update_time']))
        return {'status': 200, 'msg': '成功', 'data': result}, 200

    @staticmethod
    @make_decorator
    def filter_update_data(ftp_id):
        """修改FTP配置详情"""
        return {'status': 200, 'msg': '成功', 'data': {'ftp_id': ftp_id}}, 200

    @staticmethod
    @make_decorator
    def filter_get_all_data(result):
        """获取所有FTP配置"""
        return {'status': 200, 'msg': '成功', 'data': result}, 200
