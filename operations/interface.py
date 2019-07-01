# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result
from models.interface import InterfaceModel
from configs import db


class InterfaceOperation(object):
    @staticmethod
    @make_decorator
    def get_interface_list(interface_name, start_time, end_time, interface_type, is_deleted, page, limit):
        """获取接口列表"""
        condition = []
        if interface_name:
            condition.append('interface_name LIKE "%%%%%s%%%%"' % interface_name)
        if start_time:
            condition.append('insert_time >= %s' % start_time)
        if end_time:
            condition.append('insert_time <= %s' % end_time)
        if interface_type:
            condition.append('interface_type = %s' % interface_type)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = InterfaceModel.get_interface_list(db.etl_db, condition, page, limit)
        total = InterfaceModel.get_interface_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_interface_graph(interface_id):
        """获取接口拓扑结构"""
        # 接口任务依赖
        job_nodes = InterfaceModel.get_interface_graph(db.etl_db, interface_id)
        return Response(job_nodes=job_nodes)

    @staticmethod
    @make_decorator
    def get_interface_detail(interface_id):
        """获取接口详情"""
        # 接口详情
        detail = InterfaceModel.get_interface_detail(db.etl_db, interface_id)
        return Response(detail=detail)

    @staticmethod
    @make_decorator
    def update_interface_detail(interface_id, interface_name, interface_desc, retry, user_id, is_deleted):
        """修改接口详情"""
        InterfaceModel.update_interface_detail(db.etl_db, interface_id, interface_name, interface_desc, retry, user_id,
                                               is_deleted)
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def add_interface(interface_name, interface_desc, retry, user_id):
        """新增接口"""
        interface_id = InterfaceModel.add_interface(db.etl_db, interface_name, interface_desc, retry, user_id)
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def delete_interface(interface_id, user_id):
        """删除接口"""
        # 查询是否在调度内
        if InterfaceModel.get_schedule_detail(db.etl_db, interface_id):
            abort(400, **make_result(status=400, msg='调度任务运行中, 请停止调度任务后删除'))
        # 查询是否有任务依赖
        ids = InterfaceModel.get_job_prep_by_interface(db.etl_db, interface_id)
        job_ids = []
        out_ids = []
        for items in ids:
            if items['job_id']:
                job_ids.append(items['job_id'])
            if items['out_id']:
                out_ids.append(items['out_id'])
        if set(out_ids) - set(job_ids):
            abort(400, **make_result(status=400, msg='接口中任务作为其他任务依赖, 请停止依赖任务后删除'))
        # 删除接口
        InterfaceModel.delete_interface(db.etl_db, interface_id, user_id)
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def get_interface_id_list():
        """获取接口id列表"""
        result = InterfaceModel.get_interface_id_list(db.etl_db)
        return Response(result=result)