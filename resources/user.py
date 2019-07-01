# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource

from server.status import make_result
from configs import api
from util import session


class User(Resource):
    @staticmethod
    def get():
        """获取用户信息"""
        result = session.get_info()
        return make_result(200, msg='成功', data=result), 200


ns = api.namespace('user', description='用户')
ns.add_resource(User, '/api/')
