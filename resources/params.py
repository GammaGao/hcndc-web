# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from configs import log
from server.decorators import Response
from server.request import get_arg, get_payload
from verify.params import ParamsVerify
from operations.params import ParamsOperation
from filters.params import ParamsFilter
from document.params import *


class ParamsList(Resource):
    @staticmethod
    @params_list_request
    @ParamsFilter.filter_list_data(result=list, total=int)
    @ParamsOperation.get_params_list(param_type=int, param_name=str, source_id=int, is_deleted=int, page=int, limit=int)
    @ParamsVerify.verify_get_params_list(param_type=int, param_name=str, source_id=int, is_deleted=int, page=int,
                                         limit=int)
    def get():
        """获取参数列表"""
        params = Response(
            param_type=int(get_arg('param_type', 0)),
            param_name=get_arg('param_name', ''),
            source_id=int(get_arg('source_id', 0)),
            is_deleted=int(get_arg('is_deleted', 0)),
            page=int(get_arg('page', 1)),
            limit=int(get_arg('limit', 10))
        )
        log.info('获取参数列表[params: %s]' % str(params))
        return params


ns = api.namespace('params', description='参数')
ns.add_resource(ParamsList, '/list/api/')
