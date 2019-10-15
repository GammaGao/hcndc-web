# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class DataSourceVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_datasource_list(source_name, source_type, source_host, is_deleted, page, limit):
        """获取数据源列表"""
        if source_type < 0 or source_type > 5:
            abort(400, **make_result(status=400, msg='数据库类型错误'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))

        return Response(source_name=source_name, source_type=source_type, source_host=source_host,
                        is_deleted=is_deleted, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_test_datasource_link(source_type, auth_type, collection_name, source_host, source_port, source_database,
                                    source_user, source_password, check_sql):
        """测试数据源连接"""
        if source_type < 1 or source_type > 5:
            abort(400, **make_result(status=400, msg='数据库类型错误'))
        if auth_type < 0 or auth_type > 4:
            abort(400, **make_result(status=400, msg='认证方式类型错误'))
        if not source_host:
            abort(400, **make_result(status=400, msg='数据库ip或域名不存在'))
        if not source_port:
            abort(400, **make_result(status=400, msg='数据库端口不存在'))
        if not check_sql:
            abort(400, **make_result(status=400, msg='校验SQL不存在'))
        # 认证类型
        if auth_type == 1:
            auth_type = 'NOSASL'
        elif auth_type == 2:
            auth_type = 'PLAIN'
        elif auth_type == 3:
            auth_type = 'GSSAPI'
        elif auth_type == 4:
            auth_type = 'LDAP'
        else:
            auth_type = 'NOSASL'
        return Response(source_type=source_type, auth_type=auth_type, collection_name=collection_name,
                        source_host=source_host, source_port=source_port, source_database=source_database,
                        source_user=source_user, source_password=source_password, check_sql=check_sql)

    @staticmethod
    @make_decorator
    def verify_add_datasource_detail(source_name, source_type, auth_type, collection_name, source_host, source_port,
                                     source_database, source_user, source_password, check_sql, source_desc, user_id):
        """新增数据源"""
        if not source_name:
            abort(400, **make_result(status=400, msg='数据源名称不存在'))
        if source_type < 1 or source_type > 5:
            abort(400, **make_result(status=400, msg='数据库类型错误'))
        if auth_type < 0 or auth_type > 4:
            abort(400, **make_result(status=400, msg='认证方式类型错误'))
        if not source_host:
            abort(400, **make_result(status=400, msg='数据库ip或域名不存在'))
        if not source_port:
            abort(400, **make_result(status=400, msg='数据库端口不存在'))
        if not check_sql:
            abort(400, **make_result(status=400, msg='校验SQL不存在'))
        return Response(source_name=source_name, source_type=source_type, auth_type=auth_type,
                        collection_name=collection_name, source_host=source_host, source_port=source_port,
                        source_database=source_database, source_user=source_user, source_password=source_password,
                        check_sql=check_sql, source_desc=source_desc, user_id=user_id)
