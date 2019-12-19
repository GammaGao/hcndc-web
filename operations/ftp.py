# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask_restful import abort
from datetime import date, timedelta

from server.decorators import make_decorator, Response
from server.status import make_result
from models.ftp import FtpModel
from configs import db
from ftp_server.ftp import FtpLink
from ftp_server.sftp import SftpLink


class FtpOperation(object):
    @staticmethod
    @make_decorator
    def get_ftp_list(ftp_name, ftp_type, ftp_host, is_deleted, page, limit):
        """获取FTP配置列表"""
        condition = []
        if ftp_name:
            condition.append('ftp_name LIKE "%%%%%s%%%%"' % ftp_name)
        if ftp_host:
            condition.append('ftp_host LIKE "%%%%%s%%%%"' % ftp_host)
        if ftp_type:
            condition.append('ftp_type = %s' % ftp_type)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = FtpModel.get_ftp_list(db.etl_db, condition, page, limit)
        total = FtpModel.get_ftp_list_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def test_ftp_link(ftp_id):
        """测试FTP连接"""
        detail = FtpModel.get_ftp_detail(db.etl_db, ftp_id)
        if isinstance(detail['ftp_passwd'], bytes):
            detail['ftp_passwd'] = detail['ftp_passwd'].decode('utf-8', 'ignore')
        try:
            if detail['ftp_type'] == 1:
                FtpLink(detail['ftp_host'], detail['ftp_port'], detail['ftp_user'], detail['ftp_passwd'])
            elif detail['ftp_type'] == 2:
                SftpLink(detail['ftp_host'], detail['ftp_port'], detail['ftp_user'], detail['ftp_passwd'])
            else:
                return Response(status=400, msg='FTP服务器类型未知')
        except:
            return Response(status=400, msg='FTP连接异常')
        return Response(status=200, msg='FTP连接成功')
