# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from scheduler.generate_dag import generate_interface_dag_by_dispatch
from configs import api


class Test(Resource):
    @staticmethod
    def get(test_id):
        """测试接口"""
        result = generate_interface_dag_by_dispatch(test_id)
        for _, item in result.items():
            item['in'] = list(item['in'])
            item['out'] = list(item['out'])
        return {'status': 200, 'msg': '成功', 'data': result}, 200


ns = api.namespace('test', description='测试')
ns.add_resource(Test, '/<int:test_id>/')
