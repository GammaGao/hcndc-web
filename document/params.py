# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 参数列表请求值
params_list_request = api.doc(params={
    'param_type': '参数类型: 0.全部, 1.静态参数, 2.SQL参数, 3.上下文参数',
    'param_name': '参数名称',
    'source_id': '数据源id',
    'param_value': '参数值: 静态值,SQL查询,上下文参数以$开始',
    'is_deleted': '是否使用: 0.全部, 1.使用, 2.失效',
    'index_id': '参数目录id: 0为全部',
    'page': '页码',
    'limit': '条数'
})

# 参数新增请求
params_add_request = api.doc(body=api.model('params_add_request', {
    'param_type': fields.Integer(description='参数类型: 0.静态参数, 1.SQL参数'),
    'param_name': fields.String(description='参数名称'),
    'param_index': fields.String(description='参数目录'),
    'source_id': fields.Integer(description='数据源id'),
    'param_value': fields.String(description='参数值: 静态值或SQL查询'),
    'param_desc': fields.String(description='描述')
}, description='参数新增请求'))

# 参数修改请求
params_update_request = api.doc(body=api.model('params_update_request', {
    'param_type': fields.Integer(description='参数类型: 0.静态参数, 1.SQL参数'),
    'param_name': fields.String(description='参数名称'),
    'param_index': fields.String(description='参数目录'),
    'source_id': fields.Integer(description='数据源id'),
    'param_value': fields.String(description='参数值: 静态值或SQL查询'),
    'param_desc': fields.String(description='描述'),
    'is_deleted': fields.Integer(description='是否失效: 0.正常, 1.失效')
}, description='参数修改请求'))

# 参数测试请求
params_test_request = api.doc(body=api.model('params_test_request', {
    'source_id': fields.Integer(description='数据源id'),
    'param_value': fields.String(description='参数值: 静态值或SQL查询')
}))
