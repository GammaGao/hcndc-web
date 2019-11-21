# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 新增调度任务
scheduler_add_request = api.doc(body=api.model('scheduler_add_request', {
    'id': fields.String(description='调度id'),
    'func': fields.String(description='调度函数'),
    'args': fields.String(description='调度参数'),
    'trigger': fields.String(description='调度器类型'),
    'minute': fields.String(description='分'),
    'hour': fields.String(description='时'),
    'day': fields.String(description='天'),
    'month': fields.String(description='月'),
    'week': fields.Integer(description='周')
}, description='新增调度任务'))
