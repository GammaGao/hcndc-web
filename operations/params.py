# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from configs import db
from server.decorators import make_decorator, Response
from server.status import make_result
from models.params import ParamsModel


class ParamsOperation(object):
    @staticmethod
    @make_decorator
    def get_params_list(param_type, param_name, source_id, is_deleted, page, limit):
        """获取任务列表"""
        condition = []
        if param_type == 1:
            condition.append('param_type = 0')
        elif param_type == 2:
            condition.append('param_type = 1')
        if param_name:
            condition.append('param_name LIKE "%%%%%s%%%%"' % param_name)
        if source_id:
            condition.append('source_id = %s' % source_id)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = ParamsModel.get_params_list(db.etl_db, condition, page, limit)
        total = ParamsModel.get_params_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def add_params_detail(param_type, param_name, source_id, param_value, param_desc, user_id):
        """新增参数"""
        param_id = ParamsModel.add_params_detail(db.etl_db, param_type, param_name, source_id, param_value, param_desc,
                                                 user_id)
        return Response(param_id=param_id)

    @staticmethod
    @make_decorator
    def get_params_detail(param_id):
        """获取参数详情"""
        result = ParamsModel.get_params_detail(db.etl_db, param_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_params_detail(param_id, param_type, param_name, source_id, param_value, param_desc, is_deleted, user_id):
        """修改参数详情"""
        ParamsModel.update_params_detail(db.etl_db, param_id, param_type, param_name, source_id, param_value,
                                         param_desc, is_deleted, user_id)
        return Response(param_id=param_id)

    @staticmethod
    @make_decorator
    def delete_params_detail(param_id, user_id):
        """删除参数"""
        ParamsModel.delete_params_detail(db.etl_db, param_id, user_id)
        return Response(param_id=param_id)
