# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator, Response
from server.status import make_result
from flask_restful import abort


class LoginVerify(object):
    @staticmethod
    @make_decorator
    def verify_login_data(username, password):
        if not username:
            abort(400, **make_result(status=400, msg='用户名不能为空'))
        if not password:
            abort(400, **make_result(status=400, msg='密码不能为空'))

        return Response(username=username, password=password)
