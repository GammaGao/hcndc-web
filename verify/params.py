# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class ParamsVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_params_list(param_type, param_name, param_index, source_id, is_deleted, page, limit):
        """获取参数列表"""
        param_index = param_index.split(',') if param_index else []
        if param_type < 0 or param_type > 3:
            abort(400, **make_result(status=400, msg='参数类型错误'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))

        return Response(param_type=param_type, param_name=param_name, param_index=param_index, source_id=source_id,
                        is_deleted=is_deleted, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_add_param(param_type, param_name, param_index, source_id, param_value, param_desc, param_mark, user_id):
        """新增参数"""
        if param_type < 0 or param_type > 2:
            abort(400, **make_result(status=400, msg='参数类型错误'))
        if not param_name:
            abort(400, **make_result(status=400, msg='参数名称不得为空'))
        if param_type == 1 and source_id == 0:
            abort(400, **make_result(status=400, msg='数据源不得为空'))
        if not param_index:
            abort(400, **make_result(status=400, msg='参数目录不得为空'))
        elif re.findall(',', param_index):
            abort(400, **make_result(status=400, msg='参数目录中不得出现逗号字符","'))
        if not param_value:
            abort(400, **make_result(status=400, msg='参数值不得为空'))
        if param_mark < 0 or param_mark > 1:
            abort(400, **make_result(status=400, msg='参数权限标识错误'))
        if param_type != 2 and param_value.startswith('$'):
            abort(400, **make_result(status=400, msg='非上下文参数[参数值]不能以$开头'))
        if param_type == 2 and not param_value.startswith('$'):
            abort(400, **make_result(status=400, msg='上下文参数[参数值]只能以$开头'))
        return Response(param_type=param_type, param_name=param_name, param_index=param_index, source_id=source_id,
                        param_value=param_value, param_desc=param_desc, param_mark=param_mark, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_update_param(param_id, param_type, param_name, param_index, source_id, param_value, param_desc,
                            is_deleted, param_mark, user_id):
        """修改参数"""
        if param_type < 0 or param_type > 2:
            abort(400, **make_result(status=400, msg='参数类型错误'))
        if not param_name:
            abort(400, **make_result(status=400, msg='参数名称不得为空'))
        if not param_index:
            abort(400, **make_result(status=400, msg='参数目录不得为空'))
        elif re.findall(',', param_index):
            abort(400, **make_result(status=400, msg='参数目录中不得出现逗号字符","'))
        if param_type == 1 and source_id == 0:
            abort(400, **make_result(status=400, msg='数据源不得为空'))
        if not param_value:
            abort(400, **make_result(status=400, msg='参数值不得为空'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))
        if param_mark < 0 or param_mark > 1:
            abort(400, **make_result(status=400, msg='参数权限标识错误'))
        if param_type != 2 and param_value.startswith('$'):
            abort(400, **make_result(status=400, msg='非上下文参数[参数值]不能以$开头'))
        if param_type == 2 and not param_value.startswith('$'):
            abort(400, **make_result(status=400, msg='上下文参数[参数值]只能以$开头'))
        return Response(param_id=param_id, param_type=param_type, param_name=param_name, param_index=param_index,
                        source_id=source_id, param_value=param_value, param_desc=param_desc, is_deleted=is_deleted,
                        param_mark=param_mark, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_test_param(source_id, param_value):
        """测试SQL参数"""
        if not source_id:
            abort(400, **make_result(status=400, msg='数据源不得为空'))
        if not param_value:
            abort(400, **make_result(status=400, msg='参数值不得为空'))
        return Response(source_id=source_id, param_value=param_value)

    @staticmethod
    @make_decorator
    def verify_delete_many_params(param_id_arr, user_id):
        """批量删除参数"""
        if not param_id_arr:
            abort(400, **make_result(status=400, msg='参数id不存在'))
        return Response(param_id_arr=param_id_arr, user_id=user_id)
