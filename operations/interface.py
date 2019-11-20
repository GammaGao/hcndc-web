# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result
from models.interface import InterfaceModel
from configs import db


class InterfaceOperation(object):
    @staticmethod
    @make_decorator
    def get_interface_list(interface_name, interface_index, start_time, end_time, is_deleted, page, limit):
        """获取任务流列表"""
        condition = []
        if interface_name:
            condition.append('interface_name LIKE "%%%%%s%%%%"' % interface_name)
        if interface_index:
            condition.append('interface_index IN (%s)' % ','.join('"%s"' % item for item in interface_index))
        if start_time:
            condition.append('insert_time >= %s' % start_time)
        if end_time:
            condition.append('insert_time <= %s' % end_time)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = InterfaceModel.get_interface_list(db.etl_db, condition, page, limit)
        for item in result:
            item['run_time'] = item['run_time'].strftime('%Y-%m-%d') if item['run_time'] else ''
        total = InterfaceModel.get_interface_count(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def get_interface_graph(interface_id):
        """获取任务流拓扑结构"""
        # 任务流任务依赖
        job_nodes = InterfaceModel.get_interface_graph(db.etl_db, interface_id)
        return Response(job_nodes=job_nodes)

    @staticmethod
    @make_decorator
    def get_interface_detail(interface_id):
        """获取任务流详情"""
        # 任务流详情
        detail = InterfaceModel.get_interface_detail(db.etl_db, interface_id)
        detail['run_time'] = detail['run_time'].strftime('%Y-%m-%d') if detail['run_time'] else ''
        return Response(detail=detail)

    @staticmethod
    @make_decorator
    def update_interface_detail(interface_id, interface_name, interface_desc, interface_index, run_time, retry, user_id,
                                is_deleted):
        """修改任务流详情"""
        InterfaceModel.update_interface_detail(db.etl_db, interface_id, interface_name, interface_desc, interface_index,
                                               run_time, retry, user_id, is_deleted)
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def add_interface(interface_name, interface_desc, interface_index, parent_interface, child_interface, run_time,
                      retry, user_id):
        """新增任务流"""
        # 任务流名称查重
        if InterfaceModel.get_interface_detail_by_name(db.etl_db, interface_name):
            abort(400, **make_result(status=400, msg='任务流名称重复, 已存在数据库中'))
        # 新增任务流
        interface_id = InterfaceModel.add_interface(db.etl_db, interface_name, interface_desc, interface_index,
                                                    run_time, retry, user_id)
        # 新增任务流前置
        parent_arr = []
        for item in parent_interface:
            parent_arr.append({
                'interface_id': interface_id,
                'parent_id': item,
                'insert_time': int(time.time()),
                'update_time': int(time.time()),
                'creator_id': user_id,
                'updater_id': user_id
            })
        InterfaceModel.add_interface_parent(db.etl_db, parent_arr) if parent_arr else None
        # 新增任务流后置
        child_arr = []
        for item in child_interface:
            child_arr.append({
                'interface_id': interface_id,
                'child_id': item,
                'insert_time': int(time.time()),
                'update_time': int(time.time()),
                'creator_id': user_id,
                'updater_id': user_id
            })
        InterfaceModel.add_interface_child(db.etl_db, child_arr) if child_arr else None
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def delete_interface(interface_id, user_id):
        """删除任务流"""
        # 查询是否在调度内
        if InterfaceModel.get_schedule_detail(db.etl_db, interface_id):
            abort(400, **make_result(status=400, msg='调度任务运行中, 请停止调度任务后删除'))
        # # 查询是否有任务依赖
        # ids = InterfaceModel.get_job_prep_by_interface(db.etl_db, interface_id)
        # job_ids = []
        # out_ids = []
        # for items in ids:
        #     if items['job_id']:
        #         job_ids.append(items['job_id'])
        #     if items['out_id']:
        #         out_ids.append(items['out_id'])
        # if set(out_ids) - set(job_ids):
        #     abort(400, **make_result(status=400, msg='任务流中任务作为其他任务依赖, 请停止依赖任务后删除'))
        # 删除任务流
        InterfaceModel.delete_interface(db.etl_db, interface_id, user_id)
        return Response(interface_id=interface_id)

    @staticmethod
    @make_decorator
    def get_interface_id_list():
        """获取任务流id列表"""
        result = InterfaceModel.get_interface_id_list(db.etl_db)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def get_interface_index():
        """获取所有任务流目录"""
        result = InterfaceModel.get_interface_index(db.etl_db)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def delete_interface_many(flow_id_arr, user_id):
        """批量删除任务流"""
        err_msg = []
        for interface_id in flow_id_arr:
            # 查询是否在调度内
            if InterfaceModel.get_schedule_detail(db.etl_db, interface_id):
                err_msg.append('任务流ID: [%s], 调度运行中, 请停止调度任务后删除' % interface_id)
            # # 查询是否有任务依赖
            # ids = InterfaceModel.get_job_prep_by_interface(db.etl_db, interface_id)
            # job_ids = []
            # out_ids = []
            # for items in ids:
            #     if items['job_id']:
            #         job_ids.append(items['job_id'])
            #     if items['out_id']:
            #         out_ids.append(items['out_id'])
            # if set(out_ids) - set(job_ids):
            #     abort(400, **make_result(status=400, msg='任务流中任务作为其他任务依赖, 请停止依赖任务后删除'))
        # 删除任务流
        if not err_msg:
            condition = '(%s)' % ','.join(str(item) for item in flow_id_arr)
            InterfaceModel.delete_interface_many(db.etl_db, condition, user_id)
        return Response(msg=err_msg)
