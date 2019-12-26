# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus.resource import Resource
from scheduler.generate_dag import generate_interface_dag_by_dispatch
from configs import api
from scheduler.event_scheduler import get_event_job


class Test(Resource):
    @staticmethod
    def get(test_id):
        """测试接口"""
        result = generate_interface_dag_by_dispatch(test_id)
        for _, item in result.items():
            item['in'] = list(item['in'])
            item['out'] = list(item['out'])
        return {'status': 200, 'msg': '成功', 'data': result}, 200


class Test2(Resource):
    @staticmethod
    def get(test_id):
        result = get_event_job(test_id)
        return {'status': 200, 'msg': '成功', 'data': result}, 200


ns = api.namespace('test', description='测试')
ns.add_resource(Test, '/test/<int:test_id>/')
ns.add_resource(Test2, '/test2/<int:test_id>/')
