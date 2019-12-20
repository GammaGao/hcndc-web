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
    @FtpOperation.test_ftp_link(ftp_id=int, ftp_type=int, ftp_host=str, ftp_port=int, ftp_user=str, ftp_passwd=str)
    @FtpVerify.verify_test_ftp_link(ftp_id=int, ftp_type=int, ftp_host=str, ftp_port=int, ftp_user=str, ftp_passwd=str)
    def post():
        """测试FTP连接"""
        payload = get_payload()
        params = Response(
            ftp_id=int(payload.get('ftp_id', 0)),
            ftp_type=int(payload.get('ftp_type', 0)),
            ftp_host=payload.get('ftp_host', ''),
            ftp_port=int(payload.get('ftp_port', 0)),
            ftp_user=payload.get('ftp_user', ''),
            ftp_passwd=payload.get('ftp_passwd', '')
        )
        log.info('测试FTP连接[params: %s]' % str(params))
        return params


class FtpAdd(Resource):
    @staticmethod
    @ftp_add_detail_request
    @FtpFilter.filter_add_data(ftp_id=int)
    @FtpOperation.add_ftp_detail(ftp_name=str, ftp_desc=str, ftp_type=int, ftp_host=str,
                                 ftp_port=int, ftp_user=str, ftp_passwd=str, user_id=int)
    @FtpVerify.verify_add_ftp_detail(ftp_name=str, ftp_desc=str, ftp_type=int, ftp_host=str,
                                     ftp_port=int, ftp_user=str, ftp_passwd=str, user_id=int)
    @PermissionVerify.verify_write_permission(ftp_name=str, ftp_desc=str, ftp_type=int, ftp_host=str,
                                              ftp_port=int, ftp_user=str, ftp_passwd=str)
    def post():
        """新增FTP配置详情"""
        payload = get_payload()
        params = Response(
            ftp_name=payload.get('ftp_name', ''),
            ftp_desc=payload.get('ftp_desc', ''),
            ftp_type=int(payload.get('ftp_type', 0)),
            ftp_host=payload.get('ftp_host', ''),
            ftp_port=int(payload.get('ftp_port', 0)),
            ftp_user=payload.get('ftp_user', ''),
            ftp_passwd=payload.get('ftp_passwd', '')
        )
        log.info('新增FTP配置[params: %s]' % str(params))
        return params


class FtpDetail(Resource):
    @staticmethod
    @FtpFilter.filter_delete_data(ftp_id=int)
    @FtpOperation.delete_ftp_detail(ftp_id=int)
    @FtpVerify.verify_delete_ftp(ftp_id=int, user_id=int)
    @PermissionVerify.verify_write_permission(ftp_id=int)
    def delete(ftp_id):
        """删除FTP配置"""
        params = Response(ftp_id=ftp_id)
        log.info('删除FTP配置[params: %s]' % str(params))
        return params

    @staticmethod
    @FtpFilter.filter_get_detail_data(result=dict)
    @FtpOperation.get_ftp_detail(ftp_id=int)
    @FtpVerify.verify_get_ftp_detail(ftp_id=int)
    def get(ftp_id):
        """获取FTP配置详情"""
        params = Response(ftp_id=ftp_id)
        log.info('获取FTP配置详情[params: %s]' % str(params))
        return params

    @staticmethod
    @ftp_update_detail_request
    @FtpFilter.filter_update_data(ftp_id=int)
    @FtpOperation.update_ftp_detail(ftp_id=int, ftp_name=str, ftp_desc=str, ftp_type=int, ftp_host=str,
                                    ftp_port=int, ftp_user=str, ftp_passwd=str, is_deleted=int, user_id=int)
    @FtpVerify.verify_update_ftp_detail(ftp_id=int, ftp_name=str, ftp_desc=str, ftp_type=int, ftp_host=str,
                                        ftp_port=int, ftp_user=str, ftp_passwd=str, is_deleted=int, user_id=int)
    @PermissionVerify.verify_write_permission(ftp_id=int, ftp_name=str, ftp_desc=str, ftp_type=int, ftp_host=str,
                                              ftp_port=int, ftp_user=str, ftp_passwd=str, is_deleted=int)
    def put(ftp_id):
        """修改FTP配置"""
        payload = get_payload()
        params = Response(
            ftp_id=ftp_id,
            ftp_name=payload.get('ftp_name', ''),
            ftp_desc=payload.get('ftp_desc', ''),
            ftp_type=int(payload.get('ftp_type', 0)),
            ftp_host=payload.get('ftp_host', ''),
            ftp_port=int(payload.get('ftp_port', 0)),
            ftp_user=payload.get('ftp_user', ''),
            ftp_passwd=payload.get('ftp_passwd', ''),
            is_deleted=int(payload.get('is_deleted', 0))
        )
        log.info('修改FTP配置[params: %s]' % str(params))
        return params


class FtpListAll(Resource):
    @staticmethod
    @FtpFilter.filter_get_all_data(result=list)
    @FtpOperation.get_ftp_list_all()
    def get():
        """获取所有FTP配置"""
        params = Response()
        log.info('获取所有FTP配置')
        return params


ns = api.namespace('ftp', description='FTP配置')
ns.add_resource(FtpList, '/list/api/')
ns.add_resource(FtpTest, '/test/api/')
ns.add_resource(FtpAdd, '/add/api/')
ns.add_resource(FtpDetail, '/detail/api/<int:ftp_id>/')
ns.add_resource(FtpListAll, '/list/all/api/')
