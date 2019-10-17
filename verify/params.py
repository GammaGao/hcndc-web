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

    @staticmethod
    @make_decorator
    def verify_add_param(param_type, param_name, source_id, param_value, param_desc, user_id):
        """新增参数"""
        if param_type < 0 or param_type > 2:
            abort(400, **make_result(status=400, msg='参数类型错误'))
        if not param_name:
            abort(400, **make_result(status=400, msg='参数名称不得为空'))
        if param_type == 1 and source_id == 0:
            abort(400, **make_result(status=400, msg='数据源不得为空'))
        if not param_value:
            abort(400, **make_result(status=400, msg='参数值不得为空'))
        return Response(param_type=param_type, param_name=param_name, source_id=source_id, param_value=param_value,
                        param_desc=param_desc, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_update_param(param_id, param_type, param_name, source_id, param_value, param_desc, is_deleted, user_id):
        """修改参数"""
        if param_type < 0 or param_type > 2:
            abort(400, **make_result(status=400, msg='参数类型错误'))
        if not param_name:
            abort(400, **make_result(status=400, msg='参数名称不得为空'))
        if param_type == 1 and source_id == 0:
            abort(400, **make_result(status=400, msg='数据源不得为空'))
        if not param_value:
            abort(400, **make_result(status=400, msg='参数值不得为空'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))
        return Response(param_id=param_id, param_type=param_type, param_name=param_name, source_id=source_id,
                        param_value=param_value, param_desc=param_desc, is_deleted=is_deleted, user_id=user_id)
