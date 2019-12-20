# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class FtpModel(object):
    @staticmethod
    def get_ftp_list(cursor, condition, page=1, limit=10):
        """获取FTP配置列表"""
        command = '''
        SELECT ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, last_ping_time, process_status, is_deleted
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
        SELECT ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, last_ping_time, process_status,
        FROM_BASE64(ftp_passwd) AS ftp_passwd, insert_time, update_time, is_deleted
        FROM tb_ftp_config
        WHERE ftp_id = :ftp_id
        '''
        result = cursor.query_one(command, {
            'ftp_id': ftp_id
        })
        return result if result else {}

    @staticmethod
    def add_ftp_detail(cursor, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd, user_id):
        """新增FTP详情"""
        command = '''
        INSERT INTO tb_ftp_config(ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd,
        insert_time, update_time, creator_id, updater_id)
        VALUES(:ftp_name, :ftp_desc, :ftp_type, :ftp_host, :ftp_port, :ftp_user, TO_BASE64(:ftp_passwd),
        :insert_time, :update_time, :user_id, :user_id)
        '''
        result = cursor.insert(command, {
            'ftp_name': ftp_name,
            'ftp_desc': ftp_desc,
            'ftp_type': ftp_type,
            'ftp_host': ftp_host,
            'ftp_port': ftp_port,
            'ftp_user': ftp_user,
            'ftp_passwd': ftp_passwd,
            'insert_time': int(time.time()),
            'update_time': int(time.time()),
            'user_id': user_id
        })
        return result

    @staticmethod
    def delete_ftp_detail(cursor, ftp_id):
        """删除FTP配置"""
        command = '''
        DELETE FROM tb_ftp_config
        WHERE ftp_id = :ftp_id
        '''

        result = cursor.update(command, {
            'ftp_id': ftp_id
        })
        return result

    @staticmethod
    def update_ftp_detail(cursor, ftp_id, ftp_name, ftp_desc, ftp_type, ftp_host, ftp_port, ftp_user, ftp_passwd,
                          is_deleted, user_id):
        """修改FTP配置"""
        command = '''
        UPDATE tb_ftp_config
        SET ftp_name = :ftp_name, ftp_desc = :ftp_desc, ftp_type = :ftp_type, ftp_host = :ftp_host,
        ftp_port = :ftp_port, ftp_user = :ftp_user, ftp_passwd = TO_BASE64(:ftp_passwd), is_deleted = :is_deleted,
        update_time = :update_time, updater_id = :user_id
        WHERE ftp_id = :ftp_id
        '''
        result = cursor.update(command, {
            'ftp_id': ftp_id,
            'ftp_name': ftp_name,
            'ftp_desc': ftp_desc,
            'ftp_type': ftp_type,
            'ftp_host': ftp_host,
            'ftp_port': ftp_port,
            'ftp_user': ftp_user,
            'ftp_passwd': ftp_passwd,
            'user_id': user_id,
            'is_deleted': is_deleted,
            'update_time': int(time.time()),
            'updater_id': user_id
        })
        return result

    @staticmethod
    def get_ftp_list_all(cursor):
        """获取所有FTP配置"""
        command = '''
        SELECT ftp_id, ftp_name
        FROM tb_ftp_config
        WHERE is_deleted = 0
        '''
        result = cursor.query(command)
        return result if result else []

    @staticmethod
    def update_ftp_status(cursor, ftp_id, status):
        """修改FTP配置连通状态"""
        command = '''
        UPDATE tb_ftp_config
        SET last_ping_time = :last_ping_time, process_status = :process_status, update_time = :update_time
        WHERE ftp_id = :ftp_id
        '''
        result = cursor.update(command, {
            'ftp_id': ftp_id,
            'process_status': status,
            'last_ping_time': int(time.time()),
            'update_time': int(time.time())
        })
        return result
