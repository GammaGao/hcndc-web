# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# ftp配置列表请求值
ftp_list_request = api.doc(params={
    'ftp_name': 'ftp名称',
    'ftp_type': 'ftp类型: 0.全部, 1.ftp, 2.sftp',
    'ftp_host': 'ftp域名',
    'is_deleted': '是否使用: 0.全部, 1.使用, 2.失效',
    'page': '页码',
    'limit': '条数'
})

# 测试ftp连接请求
ftp_test_request = api.doc(body=api.model('ftp_test_request', {
    'ftp_id': fields.String(description='ftp_id')
}, description='测试ftp连接请求'))
