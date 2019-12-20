# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# ftp配置列表请求值
ftp_list_request = api.doc(params={
    'ftp_name': 'ftp配置名称',
    'ftp_type': 'ftp类型: 0.全部, 1.ftp, 2.sftp',
    'ftp_host': 'ftp域名',
    'is_deleted': '是否失效: 0.全部, 1.使用, 2.失效',
    'page': '页码',
    'limit': '条数'
})

# 测试ftp连接请求
ftp_test_request = api.doc(body=api.model('ftp_test_request', {
    'ftp_id': fields.String(description='FTP配置id'),
    'ftp_type': fields.Integer(description='ftp类型: 1.ftp, 2.sftp'),
    'ftp_host': fields.String(description='ftp域名'),
    'ftp_port': fields.Integer(description='ftp端口'),
    'ftp_user': fields.String(description='ftp用户名'),
    'ftp_passwd': fields.String(description='ftp密码')
}, description='测试ftp连接请求'))

# 新增ftp详情请求
ftp_add_detail_request = api.doc(body=api.model('ftp_add_detail_request', {
    'ftp_name': fields.String(description='ftp名称'),
    'ftp_desc': fields.String(description='ftp描述'),
    'ftp_type': fields.Integer(description='ftp类型: 1.ftp, 2.sftp'),
    'ftp_host': fields.String(description='ftp域名'),
    'ftp_port': fields.Integer(description='ftp端口'),
    'ftp_user': fields.String(description='ftp用户名'),
    'ftp_passwd': fields.String(description='ftp密码')
}, description='新增ftp详情请求'))

# 修改ftp详情请求
ftp_update_detail_request = api.doc(body=api.model('ftp_update_detail_request', {
    'ftp_id': fields.Integer(description='FTP配置id'),
    'ftp_name': fields.String(description='ftp名称'),
    'ftp_desc': fields.String(description='ftp描述'),
    'ftp_type': fields.Integer(description='ftp类型: 1.ftp, 2.sftp'),
    'ftp_host': fields.String(description='ftp域名'),
    'ftp_port': fields.Integer(description='ftp端口'),
    'ftp_user': fields.String(description='ftp用户名'),
    'ftp_passwd': fields.String(description='ftp密码'),
    'is_deleted': fields.Integer(description='是否失效: 0.正常, 1.失效')
}, description='新增ftp详情请求'))
