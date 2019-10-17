# !/usr/bin/env python
# -*- coding: utf-8 -*-


class ParamsModel(object):
    @staticmethod
    def get_params_list(cursor, condition, page=1, limit=10):
        """获取参数列表"""
        command = '''
        SELECT param_id, param_type, param_name, param_value, param_desc, source_name, a.is_deleted
        FROM tb_param_config AS a
        LEFT JOIN tb_datasource AS b USING(source_id)
        %s
        ORDER BY param_id
        LIMIT :limit OFFSET :offset
        '''

        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_params_count(cursor, condition):
        """获取参数条数"""
        command = '''
            SELECT COUNT(*) AS count
            FROM tb_jobs
            %s
            '''

        command = command % condition

        result = cursor.query_one(command)
        return result['count'] if result else 0
