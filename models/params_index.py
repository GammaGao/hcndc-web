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
