# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from flask_restful import abort

from server.status import make_result
from configs import api, log
from server.decorators import Response
from server.request import get_payload
from document.login import login_data_request, login_data_response_success
from filters.login import LoginFilter
from operations.login import LoginOperation
from verify.login import LoginVerify
from util import session


class Login(Resource):
    @staticmethod
    @login_data_request
    @login_data_response_success
    @LoginFilter.user_login(result=dict)
    @LoginOperation.get_user(username=str, password=str)
    @LoginVerify.verify_login_data(username=str, password=str)
    def post():
        """登入"""
        payload = get_payload()
        username = payload.get('username', '')
        password = payload.get('password', '')

        params = Response(
            username=username,
            password=password
        )
        log.info('用户登录[params: %s]' % str(params))
        return params

    @staticmethod
    def delete():
        """登出"""
        try:
            session.login_out()
            return make_result(200, msg='成功'), 200
        except Exception as e:
            log.error('用户登出出错 [ERROR: %s]' % e, exc_info=True)
            abort(400, **make_result(status=400, msg='无用户登陆信息'))


class User(Resource):
    @staticmethod
    def get():
        """获取用户信息"""
        result = session.get_info()
        return make_result(200, msg='成功', data=result), 200


ns = api.namespace('login', description='登陆')
ns.add_resource(Login, '/api/')
