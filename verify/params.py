# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class ParamsVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_params_list(param_type, param_name, source_id, is_deleted, page,
                               limit):
        """获取参数列表"""
        if param_type < 0 or param_type > 2:
            abort(400, **make_result(status=400, msg='参数类型错误'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))

        return Response(param_type=param_type, param_name=param_name, source_id=source_id, is_deleted=is_deleted,
                        page=page, limit=limit)
