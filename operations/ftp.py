# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator, Response
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
    def test_ftp_link(ftp_id, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd):
        """测试FTP连接"""
        if ftp_id:
            detail = FtpModel.get_ftp_detail(db.etl_db, ftp_id)
            if isinstance(detail['ftp_passwd'], bytes):
                detail['ftp_passwd'] = detail['ftp_passwd'].decode('utf-8', 'ignore')
            try:
                if detail['ftp_type'] == 1:
                    ftp = FtpLink(detail['ftp_host'], detail['ftp_port'], detail['ftp_user'], detail['ftp_passwd'])
                    ftp.close()
                    FtpModel.update_ftp_status(db.etl_db, ftp_id, 0)
                elif detail['ftp_type'] == 2:
                    ftp = SftpLink(detail['ftp_host'], detail['ftp_port'], detail['ftp_user'], detail['ftp_passwd'])
                    ftp.close()
                    FtpModel.update_ftp_status(db.etl_db, ftp_id, 0)
                else:
                    FtpModel.update_ftp_status(db.etl_db, ftp_id, 1)
                    return Response(status=400, msg='FTP服务器类型未知')
            except:
                FtpModel.update_ftp_status(db.etl_db, ftp_id, 1)
                return Response(status=400, msg='FTP连接异常')
            return Response(status=200, msg='FTP连接成功')
        else:
            try:
                if ftp_type == 1:
                    ftp = FtpLink(ftp_host, ftp_port, ftp_user, ftp_passwd)
                    ftp.close()
                elif ftp_type == 2:
                    ftp = SftpLink(ftp_host, ftp_port, ftp_user, ftp_passwd)
                    ftp.close()
                else:
                    return Response(status=400, msg='FTP服务器类型未知')
            except:
                return Response(status=400, msg='FTP连接异常')
            return Response(status=200, msg='FTP连接成功')

    @staticmethod
    @make_decorator
    def add_ftp_detail(ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd, user_id):
        """新增FTP配置详情"""
        ftp_id = FtpModel.add_ftp_detail(db.etl_db, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user,
                                         ftp_passwd, user_id)
        return Response(ftp_id=ftp_id)

    @staticmethod
    @make_decorator
    def delete_ftp_detail(ftp_id):
        """删除FTP配置"""
        # TODO 检查依赖
        # prep_count = FtpModel.get_param_by_ftp_id(db.etl_db, ftp_id)
        # if prep_count:
        #     abort(400, **make_result(status=400, msg='FTP配置在任务参数表中存在%s个依赖, 不可删除' % prep_count))
        FtpModel.delete_ftp_detail(db.etl_db, ftp_id)
        return Response(ftp_id=ftp_id)

    @staticmethod
    @make_decorator
    def get_ftp_detail(ftp_id):
        """获取FTP配置详情"""
        result = FtpModel.get_ftp_detail(db.etl_db, ftp_id)
        if isinstance(result['ftp_passwd'], bytes):
            result['ftp_passwd'] = result['ftp_passwd'].decode('utf-8', 'ignore')
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_ftp_detail(ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd, is_deleted,
                          user_id):
        """修改FTP配置"""
        # TODO 检查依赖
        # if is_deleted == 1:
        #     prep_count = FtpModel.get_param_by_source_id(db.etl_db, source_id)
        #     if prep_count:
        #         abort(400, **make_result(status=400, msg='数据源在任务参数表中存在%s个依赖, 不可设置失效' % prep_count))
        FtpModel.update_ftp_detail(db.etl_db, ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user,
                                   ftp_passwd, is_deleted, user_id)
        return Response(ftp_id=ftp_id)

    @staticmethod
    @make_decorator
    def get_ftp_list_all():
        """获取所有FTP配置"""
        result = FtpModel.get_ftp_list_all(db.etl_db)
        return Response(result=result)
