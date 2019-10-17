# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 参数列表请求值
params_list_request = api.doc(params={
    'param_type': '参数类型: 0.全部, 1.静态参数, 2.SQL参数',
    'param_name': '参数名称',
    'source_id': '数据源id',
    'param_value': '参数值: 静态值或SQL查询',
    'is_deleted': '是否使用: 0.全部, 1.使用, 2.失效',
    'page': '页码',
    'limit': '条数'
})
