# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result
from models.user import UserModel
from configs import db


class UserOperation(object):
    """用户操作类"""
    @staticmethod
    @make_decorator
    def get_user_menu(user_info):
        """获取用户菜单"""
        user_id = user_info.get('id', 0)
        if not user_id:
            abort(403, **make_result(status=403, msg='用户未登录'))
        result = UserModel.get_user_menu(db.etl_db, user_id)
        return Response(menu_list=result)


