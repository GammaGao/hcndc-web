# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class DataSourceModel(object):
    @staticmethod
    def get_datasource_list(cursor, condition, page=1, limit=10):
        """获取数据源列表"""
        command = '''
        SELECT source_id, source_name, source_type, source_host, source_port,
        source_database, check_sql, source_desc, is_deleted
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
    def add_datasource_detail(cursor, source_name, source_type, auth_type, collection_name, source_host, source_port,
                              source_database, source_user, source_password, check_sql, source_desc, user_id):
        """新增数据源"""
        command = '''
        INSERT INTO tb_datasource(source_name, source_type, auth_type, collection_name, source_host, source_port,
        source_database, source_user, source_password, check_sql, source_desc, insert_time, update_time, creator_id,
        updater_id)
        VALUES(:source_name, :source_type, :auth_type, :collection_name, :source_host, :source_port, :source_database,
        :source_user, :source_password, :check_sql, :source_desc, :insert_time, :update_time, :creator_id, :updater_id)
        '''
        result = cursor.insert(command, {
            'source_name': source_name,
            'source_type': source_type,
            'auth_type': auth_type,
            'collection_name': collection_name,
            'source_host': source_host,
            'source_port': source_port,
            'source_database': source_database,
            'source_user': source_user,
            'source_password': source_password,
            'check_sql': check_sql,
            'source_desc': source_desc,
            'insert_time': int(time.time()),
            'update_time': int(time.time()),
            'creator_id': user_id,
            'updater_id': user_id
        })
        return result
