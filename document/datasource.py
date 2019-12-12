# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 任务列表请求值
datasource_list_request = api.doc(params={
    'source_name': '数据源名称',
    'source_type': '数据库类型: 0.全部, 1.mysql, 2.mongo, 3.mssql, 4.hive, 5.impala',
    'source_host': '数据库ip或域名',
    'is_deleted': '是否使用: 0全部, 1使用, 2失效',
    'page': '页码',
    'limit': '条数'
})

# 测试数据源连接请求
datasource_test_request = api.doc(body=api.model('datasource_test_request', {
    'source_id': fields.String(description='数据源id')
}, description='测试数据源连接请求'))

# 新增数据源详情请求
datasource_add_detail_request = api.doc(body=api.model('datasource_add_detail_request', {
    'source_name': fields.String(description='数据源名称'),
    'source_type': fields.String(description='数据库类型: 1.mysql, 2.mongo, 3.mssql, 4.hive, 5.impala'),
    'auth_type': fields.Integer(description='认证方式(仅hive和impala使用):0.无,1.NOSASL,2.PLAIN,3.GSSAPI,4.LDAP'),
    'source_host': fields.String(description='数据库ip或域名'),
    'source_port': fields.Integer(description='数据库端口'),
    'source_database': fields.String(description='数据库库名'),
    'source_user': fields.String(description='用户名'),
    'source_password': fields.String(description='密码'),
    'source_desc': fields.String(description='数据源描述')
}, description='新增数据源详情请求'))
