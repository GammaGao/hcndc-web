# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 登陆
login_data_request = api.doc(body=api.model('login_data_request', {
    'username': fields.String(description='用户名'),
    'password': fields.String(description='密码')
    }, description='用户登录请求参数')
)

# 登陆返回值
login_data_response_success = api.response(200, '成功', api.model('login_response_success', {
    'state': fields.Integer(description=200),
    'msg': fields.String(description='成功')
}))