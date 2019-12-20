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
    def verify_test_datasource_link(source_id, source_type, auth_type, source_host, source_port,
                                    source_database, source_user, source_password):
        """测试数据源连接"""
        return Response(source_id=source_id, source_type=source_type, auth_type=auth_type, source_host=source_host,
                        source_port=source_port, source_database=source_database, source_user=source_user,
                        source_password=source_password)

    @staticmethod
    @make_decorator
    def verify_add_datasource_detail(source_name, source_type, auth_type, source_host, source_port,
                                     source_database, source_user, source_password, source_desc, user_id):
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
        return Response(source_name=source_name, source_type=source_type, auth_type=auth_type, source_host=source_host,
                        source_port=source_port, source_database=source_database, source_user=source_user,
                        source_password=source_password, source_desc=source_desc, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_delete_datasource(source_id, user_id):
        """删除数据源"""
        if not source_id:
            abort(400, **make_result(status=400, msg='数据源id不存在'))
        return Response(source_id=source_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_get_datasource_detail(source_id):
        """获取数据源详情"""
        if not source_id:
            abort(400, **make_result(status=400, msg='数据源id不存在'))
        return Response(source_id=source_id)

    @staticmethod
    @make_decorator
    def verify_update_datasource_detail(source_id, source_name, source_type, auth_type, source_host, source_port,
                                        source_database, source_user, source_password, source_desc, is_deleted,
                                        user_id):
        """修改数据源"""
        if not source_id:
            abort(400, **make_result(status=400, msg='数据源id不存在'))
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
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='状态参数错误'))
        return Response(source_id=source_id, source_name=source_name, source_type=source_type, auth_type=auth_type,
                        source_host=source_host, source_port=source_port, source_database=source_database,
                        source_user=source_user, source_password=source_password, source_desc=source_desc,
                        is_deleted=is_deleted, user_id=user_id)
