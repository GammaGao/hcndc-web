# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from server.decorators import Response
from server.status import make_result
from operations.user import UserOperation
from filters.user import UserFilter
from configs import api
from util import session


class User(Resource):
    @staticmethod
    def get():
        """获取用户信息"""
        result = session.get_info()
        return make_result(200, msg='成功', data=result), 200


class UserMenu(Resource):
    @staticmethod
    @UserFilter.filter_menu_data(menu_list=list)
    @UserOperation.get_user_menu(user_info=dict)
    def get():
        """获取用户菜单"""
        user_info = session.get_info()
        return Response(user_info=user_info)


ns = api.namespace('user', description='用户')
ns.add_resource(User, '/api/')
ns.add_resource(UserMenu, '/menu/api/')
