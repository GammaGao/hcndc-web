# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class FtpVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_ftp_list(ftp_name, ftp_type, ftp_host, is_deleted, page, limit):
        """获取FTP配置列表"""
        if ftp_type < 0 or ftp_type > 2:
            abort(400, **make_result(status=400, msg='FTP类型错误'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))

        return Response(ftp_name=ftp_name, ftp_type=ftp_type, ftp_host=ftp_host, is_deleted=is_deleted, page=page,
                        limit=limit)

    @staticmethod
    @make_decorator
    def verify_test_ftp_link(ftp_id, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd):
        """测试FTP连接"""
        return Response(ftp_id=ftp_id, ftp_type=ftp_type, ftp_host=ftp_host, ftp_port=ftp_port, ftp_user=ftp_user,
                        ftp_passwd=ftp_passwd)

    @staticmethod
    @make_decorator
    def verify_add_ftp_detail(ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd, user_id):
        """新增FTP配置详情"""
        if not ftp_name:
            abort(400, **make_result(status=400, msg='FTP名称不存在'))
        if ftp_type < 1 or ftp_type > 2:
            abort(400, **make_result(status=400, msg='FTP类型错误'))
        if not ftp_host:
            abort(400, **make_result(status=400, msg='FTP域名不存在'))
        if not ftp_port:
            abort(400, **make_result(status=400, msg='FTP端口不存在'))
        return Response(ftp_name=ftp_name, ftp_desc=ftp_desc, ftp_type=ftp_type, ftp_host=ftp_host, ftp_port=ftp_port,
                        ftp_user=ftp_user, ftp_passwd=ftp_passwd, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_delete_ftp(ftp_id, user_id):
        """删除FTP配置"""
        if not ftp_id:
            abort(400, **make_result(status=400, msg='FTP配置id不存在'))
        return Response(ftp_id=ftp_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_get_ftp_detail(ftp_id):
        """获取FTP配置详情"""
        if not ftp_id:
            abort(400, **make_result(status=400, msg='FTP配置id不存在'))
        return Response(ftp_id=ftp_id)

    @staticmethod
    @make_decorator
    def verify_update_ftp_detail(ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd,
                                 is_deleted, user_id):
        """修改FTP配置"""
        if not ftp_id:
            abort(400, **make_result(status=400, msg='FTP配置id不存在'))
        if not ftp_name:
            abort(400, **make_result(status=400, msg='FTP名称不存在'))
        if ftp_type < 1 or ftp_type > 2:
            abort(400, **make_result(status=400, msg='FTP类型错误'))
        if not ftp_host:
            abort(400, **make_result(status=400, msg='FTP域名不存在'))
        if not ftp_port:
            abort(400, **make_result(status=400, msg='FTP端口不存在'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))
        return Response(ftp_id=ftp_id, ftp_name=ftp_name, ftp_desc=ftp_desc, ftp_type=ftp_type, ftp_host=ftp_host,
                        ftp_port=ftp_port, ftp_user=ftp_user, ftp_passwd=ftp_passwd, is_deleted=is_deleted,
                        user_id=user_id)
