# !/usr/bin/env python
# -*- coding: utf-8 -*-

from server.decorators import make_decorator
from server.status import make_result
from util import session

class LoginFilter(object):
    @staticmethod
    @make_decorator
    def user_login(result):
        result = {
            'id': result['id'],
            'user_name': result['user_name'],
            'role': result['role'],
            'permission': [i for i in result['permission'].split(',') if i]
        }
        session.login(result)
        return make_result(200), 200