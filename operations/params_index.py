# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from configs import db, log
from server.decorators import make_decorator, Response
from server.status import make_result
from models.params_index import ParamsIndexModel


class ParamsIndexOperation(object):
    @staticmethod
    @make_decorator
    def get_params_index_list():
        """获取参数目录列表"""
        result = ParamsIndexModel.get_params_index_list(db.etl_db)
        return Response(menu_list=result)

    @staticmethod
    @make_decorator
    def add_params_index(parent_id, index_name, index_desc, index_mark, user_id):
        """新增参数目录"""
        result = ParamsIndexModel.add_params_index(db.etl_db, parent_id, index_name, index_desc, index_mark, user_id)
        return Response(index_id=result)

    @staticmethod
    @make_decorator
    def update_params_index(index_id, index_name, user_id):
        """修改参数目录"""
        ParamsIndexModel.update_params_index(db.etl_db, index_id, index_name, user_id)
        return Response(index_id=index_id)

    @staticmethod
    @make_decorator
    def delete_params_index(index_id, user_id):
        """删除参数目录"""
        ParamsIndexModel.delete_params_index(db.etl_db, index_id, user_id)
        return Response(index_id=index_id)
