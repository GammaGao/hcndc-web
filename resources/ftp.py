# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from document.ftp import *
from filters.ftp import FtpFilter
from operations.ftp import FtpOperation
from verify.ftp import FtpVerify
from verify.permission import PermissionVerify


class FtpList(Resource):
    @staticmethod
    @ftp_list_request
    @FtpFilter.filter_list_data(result=list, total=int)
    @FtpOperation.get_ftp_list(ftp_name=str, ftp_type=int, ftp_host=str, is_deleted=int, page=int, limit=int)
    @FtpVerify.verify_get_ftp_list(ftp_name=str, ftp_type=int, ftp_host=str, is_deleted=int, page=int, limit=int)
    def get():
        """获取FTP配置列表"""
        params = Response(
            ftp_name=get_arg('ftp_name', ''),
            ftp_type=int(get_arg('ftp_type', 0)),
            ftp_host=get_arg('ftp_host', ''),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取FTP配置列表[params: %s]' % str(params))
        return params


class FtpTest(Resource):
    @staticmethod
    @ftp_test_request
    @FtpFilter.filter_test_data(status=int, msg=str)
    @FtpOperation.test_ftp_link(ftp_id=int)
    @FtpVerify.verify_test_ftp_link(ftp_id=int)
    def post():
        """测试FTP连接"""
        payload = get_payload()
        params = Response(
            ftp_id=int(payload.get('ftp_id', 0))
        )
        log.info('测试FTP连接[params: %s]' % str(params))
        return params


ns = api.namespace('ftp', description='FTP配置')
ns.add_resource(FtpList, '/list/api/')
