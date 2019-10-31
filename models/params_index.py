# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class ParamsIndexModel(object):
    @staticmethod
    def get_params_index_list(cursor):
        """获取参数目录列表"""
        command = '''
        SELECT p_index_id AS id, parent_id, index_name AS title, index_mark AS mark
        FROM tb_param_index
        WHERE is_deleted = 0
        '''
        result = cursor.query(command)
        return result if result else []

    @staticmethod
    def add_params_index(cursor, parent_id, index_name, index_desc, index_mark, user_id):
        """新增参数目录"""
        command = '''
        INSERT INTO tb_param_index(parent_id, index_name, index_desc, index_mark, insert_time, update_time,
        creator_id, updater_id)
        VALUES (:parent_id, :index_name, :index_desc, :index_mark, :insert_time, :update_time, :user_id, :user_id)
        '''
        result = cursor.insert(command, {
            'parent_id': parent_id,
            'index_name': index_name,
            'index_desc': index_desc,
            'index_mark': index_mark,
            'insert_time': int(time.time()),
            'update_time': int(time.time()),
            'user_id': user_id
        })
        return result

    @staticmethod
    def update_params_index(cursor, index_id, index_name, user_id):
        """修改参数目录"""
        command = '''
        UPDATE tb_param_index
        SET index_name = :index_name, update_time = :update_time, updater_id = :updater_id
        WHERE p_index_id = :index_id AND index_mark = 0
        '''
        result = cursor.update(command, {
            'index_name': index_name,
            'update_time': int(time.time()),
            'updater_id': user_id,
            'index_id': index_id
        })
        return result

    @staticmethod
    def delete_params_index(cursor, index_id, user_id):
        """删除参数目录"""
        command = '''
        UPDATE tb_param_index
        SET is_deleted = 1, update_time = :update_time, updater_id = :updater_id
        WHERE p_index_id = :index_id AND index_mark = 0
        '''
        result = cursor.update(command, {
            'index_id': index_id,
            'update_time': int(time.time()),
            'updater_id': user_id
        })
        return result
