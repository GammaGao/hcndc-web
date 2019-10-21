# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class DataSourceModel(object):
    @staticmethod
    def get_datasource_list(cursor, condition, page=1, limit=10):
        """获取数据源列表"""
        command = '''
        SELECT source_id, source_name, source_type, source_host, source_port,
        source_database, source_desc, is_deleted
        FROM tb_datasource
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
    def get_datasource_list_count(cursor, condition):
        """获取数据源列表条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_datasource
        %s
        '''
        command = command % condition
        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def add_datasource_detail(cursor, source_name, source_type, auth_type, source_host, source_port,
                              source_database, source_user, source_password, source_desc, user_id):
        """新增数据源"""
        command = '''
        INSERT INTO tb_datasource(source_name, source_type, auth_type, source_host, source_port,
        source_database, source_user, source_password, source_desc, insert_time, update_time, creator_id,
        updater_id)
        VALUES(:source_name, :source_type, :auth_type, :source_host, :source_port, :source_database,
        :source_user, :source_password, :source_desc, :insert_time, :update_time, :creator_id, :updater_id)
        '''
        result = cursor.insert(command, {
            'source_name': source_name,
            'source_type': source_type,
            'auth_type': auth_type,
            'source_host': source_host,
            'source_port': source_port,
            'source_database': source_database,
            'source_user': source_user,
            'source_password': source_password,
            'source_desc': source_desc,
            'insert_time': int(time.time()),
            'update_time': int(time.time()),
            'creator_id': user_id,
            'updater_id': user_id
        })
        return result

    @staticmethod
    def delete_datasource_detail(cursor, source_id, user_id):
        """删除数据源"""
        command = '''
        UPDATE tb_datasource
        SET is_deleted = 1, updater_id = :user_id, update_time = :update_time
        WHERE source_id = :source_id
        '''

        result = cursor.update(command, {
            'source_id': source_id,
            'user_id': user_id,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def get_datasource_detail(cursor, source_id):
        """获取数据源详情"""
        command = '''
        SELECT source_id, source_name, source_type, auth_type, source_host, source_port,
        source_database, source_user, source_password, source_desc, insert_time, update_time, is_deleted
        FROM tb_datasource
        WHERE source_id = :source_id
        '''
        result = cursor.query_one(command, {
            'source_id': source_id
        })
        return result if result else {}

    @staticmethod
    def update_datasource_detail(cursor, source_id, source_name, source_type, auth_type, source_host, source_port,
                                 source_database, source_user, source_password, source_desc, user_id, is_deleted):
        """修改数据源"""
        command = '''
        UPDATE tb_datasource
        SET source_name = :source_name, source_type = :source_type, auth_type = :auth_type,
        source_host = :source_host, source_port = :source_port,
        source_database = :source_database, source_user = :source_user,
        source_password = :source_password, source_desc = :source_desc,
        is_deleted = :is_deleted, update_time = :update_time, updater_id = :user_id
        WHERE source_id = :source_id
        '''
        result = cursor.update(command, {
            'source_id': source_id,
            'source_name': source_name,
            'source_type': source_type,
            'auth_type': auth_type,
            'source_host': source_host,
            'source_port': source_port,
            'source_database': source_database,
            'source_user': source_user,
            'source_password': source_password,
            'source_desc': source_desc,
            'user_id': user_id,
            'is_deleted': is_deleted,
            'update_time': int(time.time()),
            'updater_id': user_id
        })
        return result

    @staticmethod
    def get_datasource_list_all(cursor):
        """获取所有数据源"""
        command = '''
        SELECT source_id, source_name
        FROM tb_datasource
        WHERE is_deleted = 0
        '''
        result = cursor.query(command)
        return result if result else []

    @staticmethod
    def get_datasource_by_id(cursor, source_id):
        """根据id获取数据源"""
        command = '''
        SELECT source_id, source_name, source_type, auth_type, source_host, source_port, source_database,
        source_user, source_password
        FROM tb_datasource
        WHERE is_deleted = 0 AND source_id = :source_id
        '''
        result = cursor.query_one(command, {
            'source_id': source_id
        })
        return result if source_id else {}
