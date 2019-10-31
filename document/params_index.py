# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 参数菜单新增请求
params_index_add_request = api.doc(body=api.model('params_index_add_request', {
    'parent_id': fields.Integer(description='父级参数目录id'),
    'index_name': fields.String(description='目录名称'),
    'index_desc': fields.String(description='目录描述'),
    'index_mark': fields.Integer(description='目录权限标识: 0.全部操作, 1.禁止修改')
}, description='参数新增请求'))
