# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 任务流列表请求值
interface_list_request = api.doc(params={
    'interface_name': '任务流名称',
    'interface_index': '任务流目录',
    'start_time': '开始创建时间',
    'end_time': '结束创建时间',
    'is_deleted': '是否使用: 0全部, 1正常, 2删除',
    'page': '页码',
    'limit': '条数'
})

# 任务流列表返回值
interface_list_response_success = api.response(200, '成功', api.model('interface_list_response_success', {
    'state': fields.Integer(description=200),
    'msg': fields.String(description='成功'),
    'data': fields.Nested(model=api.model('job_list_response_data', {
        'interface_id': fields.String(description='任务流id'),
        'user_name': fields.String(description='创建者'),
        'interface_name': fields.String(description='任务流名称'),
        'interface_desc': fields.String(description='任务流描述'),
        'is_deleted': fields.Integer(description='是否失效: 0.正常, 1.失效'),
    }), description='任务流列表返回值')
}))

# 任务流图请求
interface_graph = api.doc(params={
    'graph_type': '图表类型: 1.任务流中任务依赖, 2.局部-任务流依赖, 3.全局-任务流依赖'
})

# 任务流修改请求
interface_update_request = api.doc(body=api.model('interface_update_request', {
    'interface_name': fields.String(description='任务流名称'),
    'interface_desc': fields.String(description='任务流描述'),
    'interface_index': fields.String(description='任务流目录'),
    'old_parent': fields.String(description='原前置任务流'),
    'parent_interface': fields.String(description='前置任务流'),
    'run_time': fields.String(description='数据日期: %Y-%m-%d'),
    'retry': fields.Integer(description='重试次数'),
    'is_deleted': fields.Integer(description='是否失效: 0.正常, 1.失效')
}, description='任务流修改请求参数'))

# 新增任务流请求
interface_add_request = api.doc(body=api.model('interface_add_request', {
    'interface_name': fields.String(description='任务流名称'),
    'interface_desc': fields.String(description='任务流描述'),
    'interface_index': fields.String(description='任务流目录'),
    'parent_interface': fields.String(description='前置任务流'),
    'run_time': fields.String(description='数据日期: %Y-%m-%d'),
    'retry': fields.Integer(description='重试次数'),
}, description='新增任务流请求参数'))
