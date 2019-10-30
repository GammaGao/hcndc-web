# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from configs import log, api
from server.decorators import Response
from server.request import get_arg, get_payload
from operations.params_index import ParamsIndexOperation
from filters.params_index import ParamsIndexFilter


class ParamsIndexList(Resource):
    @staticmethod
    @ParamsIndexFilter.filter_list_data(menu_list=list)
    @ParamsIndexOperation.get_params_index_list()
    def get():
        """获取参数目录数据结构"""
        return Response()


ns = api.namespace('params_index', description='参数目录')
ns.add_resource(ParamsIndexList, '/list/api/')
