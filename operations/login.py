# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator, Response
from models.login import LoginModel
from server.status import make_result, APIStatus
from configs import db

from flask_restful import abort

class LoginOperation(object):
    @staticmethod
    @make_decorator
    def get_user(username, password):
        """用户登陆"""
        result = LoginModel.get_user(db.etl_db, username, password)

        if not result:
            abort(400, **make_result(status=400, msg='用户名或密码错误'))

        return Response(result=result)