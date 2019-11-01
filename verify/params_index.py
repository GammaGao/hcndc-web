# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class ParamsIndexVerify(object):
    @staticmethod
    @make_decorator
    def verify_add_param_index(parent_id, index_name, index_desc, index_mark, user_id):
        """新增参数菜单"""
        if not index_name:
            abort(400, **make_result(status=400, msg='参数目录名称不得为空'))
        if index_mark < 0 or index_mark > 1:
            abort(400, **make_result(status=400, msg='目录权限标识错误'))
        return Response(parent_id=parent_id, index_name=index_name, index_desc=index_desc, index_mark=index_mark,
                        user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_update_param_index(index_id, index_name, user_id):
        """修改参数菜单"""
        if not index_id:
            abort(400, **make_result(status=400, msg='参数目录id为空'))
        if not index_name:
            abort(400, **make_result(status=400, msg='参数目录名称不得为空'))
        return Response(index_id=index_id, index_name=index_name, user_id=user_id)
