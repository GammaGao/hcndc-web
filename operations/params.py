# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from configs import db, log
from server.decorators import make_decorator, Response
from server.status import make_result
from models.params import ParamsModel
from models.datasource import DataSourceModel
from util.db_util import get_db_data_one


class ParamsOperation(object):
    @staticmethod
    @make_decorator
    def get_params_list(param_type, param_name, param_index, source_id, is_deleted, page, limit):
        """获取任务列表"""
        condition = []
        if param_type == 1:
            condition.append('param_type = 0')
        elif param_type == 2:
            condition.append('param_type = 1')
        elif param_type == 3:
            condition.append('param_type = 2')
        if param_name:
            condition.append('param_name LIKE "%%%%%s%%%%"' % param_name)
        if param_index:
            condition.append('param_index IN (%s)' % ','.join('"%s"' % item for item in param_index))
        if source_id:
            condition.append('source_id = %s' % source_id)
        if is_deleted == 1:
            condition.append('is_deleted = 0')
        elif is_deleted == 2:
            condition.append('is_deleted = 1')

        condition = 'WHERE ' + ' AND '.join(condition) if condition else ''

        result = ParamsModel.get_params_list_all(db.etl_db, condition, page, limit)
        total = ParamsModel.get_params_count_all(db.etl_db, condition)
        return Response(result=result, total=total)

    @staticmethod
    @make_decorator
    def add_params_detail(param_type, param_name, param_index, source_id, param_value, param_desc, user_id):
        """新增参数"""
        # 参数名称查重
        if ParamsModel.get_params_detail_by_name(db.etl_db, param_name):
            abort(400, **make_result(status=400, msg='参数名称重复, 已存在数据库中'))
        param_id = ParamsModel.add_params_detail(db.etl_db, param_type, param_name, param_index, source_id, param_value,
                                                 param_desc, user_id)
        return Response(param_id=param_id)

    @staticmethod
    @make_decorator
    def get_params_detail(param_id):
        """获取参数详情"""
        result = ParamsModel.get_params_detail(db.etl_db, param_id)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def update_params_detail(param_id, param_type, param_name, param_index, source_id, param_value, param_desc,
                             is_deleted, user_id):
        """修改参数详情"""
        # 参数名称查重
        param_detail = ParamsModel.get_params_detail_by_name(db.etl_db, param_name)
        if param_detail and param_detail['param_id'] != param_id:
            abort(400, **make_result(status=400, msg='参数名称重复, 已存在数据库中'))
        # 修改参数
        ParamsModel.update_params_detail(db.etl_db, param_id, param_type, param_name, param_index, source_id,
                                         param_value, param_desc, is_deleted, user_id)
        return Response(param_id=param_id)

    @staticmethod
    @make_decorator
    def delete_params_detail(param_id, user_id):
        """删除参数"""
        err_msg = []
        result = ParamsModel.get_params_detail_not_delete(db.etl_db, param_id)
        for param_detail in result:
            if param_detail['param_type'] == 2:
                err_msg.append('参数ID: [%s]为上下文参数, 不能删除' % param_id)
            if param_detail['job_id']:
                err_msg.append('参数ID: [%s], 在任务: [%s]调用中, 请停止调用后删除' %
                               (param_id, ','.join(item['job_id'] for item in result)))
        if not err_msg:
            ParamsModel.delete_params_detail(db.etl_db, param_id, user_id)
        return Response(msg=err_msg)

    @staticmethod
    @make_decorator
    def test_params_detail(source_id, param_value):
        """测试SQL参数"""
        item = DataSourceModel.get_datasource_by_id(db.etl_db, source_id)
        if not item:
            abort(400, **make_result(status=400, msg='该数据源id不存在'))
        # 获取数据源数据
        result_data = get_db_data_one(item['source_type'], item['source_host'], item['source_port'],
                                      item['source_user'], item['source_password'], item['source_database'],
                                      item['auth_type'], param_value)
        return Response(result=result_data['result'], msg=result_data['msg'], flag=result_data['flag'])

    @staticmethod
    @make_decorator
    def get_params_list_all():
        """获取所有参数"""
        result = ParamsModel.get_params_all(db.etl_db)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def get_params_index_all():
        """获取所有参数目录"""
        result = ParamsModel.get_params_index_all(db.etl_db)
        return Response(result=result)

    @staticmethod
    @make_decorator
    def delete_params_may(param_id_arr, user_id):
        """批量删除参数"""
        err_msg = []
        for param_id in param_id_arr:
            result = ParamsModel.get_params_detail_not_delete(db.etl_db, param_id)
            for param_detail in result:
                if param_detail['param_type'] == 2:
                    err_msg.append('参数ID: [%s]为上下文参数, 不能删除' % param_id)
                if param_detail['job_id']:
                    err_msg.append('参数ID: [%s], 在任务: [%s]调用中, 请停止调用后删除' %
                                   (param_id, ','.join(item['job_id'] for item in result)))
        if not err_msg:
            condition = '(%s)' % ','.join(str(item) for item in param_id_arr)
            ParamsModel.delete_params_many(db.etl_db, condition, user_id)
        return Response(msg=err_msg)
