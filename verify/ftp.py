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
            abort(400, **make_result(status=400, msg='ftp类型错误'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))

        return Response(ftp_name=ftp_name, ftp_type=ftp_type, ftp_host=ftp_host, is_deleted=is_deleted, page=page,
                        limit=limit)

    @staticmethod
    @make_decorator
    def verify_test_ftp_link(ftp_id):
        """测试FTP连接"""
        if not ftp_id:
            abort(400, **make_result(status=400, msg='ftp_id不存在'))
        return Response(ftp_id=ftp_id)
