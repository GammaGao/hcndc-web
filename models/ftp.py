# !/usr/bin/env python
# -*- coding: utf-8 -*-


class FtpModel(object):
    @staticmethod
    def get_ftp_list(cursor, condition, page=1, limit=10):
        """获取FTP配置列表"""
        command = '''
        SELECT ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, is_deleted
        FROM tb_ftp_config
        %s
        LIMIT :limit OFFSET :offset
        '''
        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_ftp_list_count(cursor, condition):
        """获取FTP配置列表条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_ftp_config
        %s
        '''
        command = command % condition
        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_ftp_detail(cursor, ftp_id):
        """获取FTP详情"""
        command = '''
        SELECT ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port,
        ftp_user, FROM_BASE64(ftp_passwd) AS ftp_passwd, is_deleted
        FROM tb_ftp_config
        WHERE ftp_id = :ftp_id
        '''
        result = cursor.query_one(command, {
            'ftp_id': ftp_id
        })
        return result if result else {}
