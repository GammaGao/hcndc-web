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
