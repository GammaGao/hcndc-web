# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 接口列表请求值
interface_list_request = api.doc(params={
    'interface_name': '项目名称',
    'start_time': '开始创建时间',
    'end_time': '结束创建时间',
    'is_deleted': '是否使用: 0全部, 1正常, 2删除',
    'page': '页码',
    'limit': '条数'
})

# 接口列表返回值
interface_list_response_success = api.response(200, '成功', api.model('interface_list_response_success', {
    'state': fields.Integer(description=200),
    'msg': fields.String(description='成功'),
    'data': fields.Nested(model=api.model('job_list_response_data', {
        'interface_id': fields.String(description='接口id'),
        'user_name': fields.String(description='创建者'),
        'interface_name': fields.String(description='接口名称'),
        'interface_desc': fields.String(description='接口描述'),
        'run_period': fields.String(description='账期'),
        'is_deleted': fields.Integer(description='是否删除: 0否, 1是'),
    }), description='接口列表返回值')
}))

# 接口修改请求
interface_update_request = api.doc(body=api.model('interface_update_request', {
    'interface_name': fields.String(description='接口名称'),
    'interface_desc': fields.String(description='接口描述'),
    'retry': fields.Integer(description='重试次数'),
    'is_deleted': fields.Integer(description='是否删除: 0否, 1是')
}, description='接口修改请求参数'))

# 新增接口请求
interface_add_request = api.doc(body=api.model('interface_add_request', {
    'interface_name': fields.String(description='接口名称'),
    'interface_desc': fields.String(description='接口描述'),
    'retry': fields.Integer(description='重试次数'),
}, description='新增接口请求参数'))
