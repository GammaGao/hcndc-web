# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import session


def login(data):
    """登入"""
    session['login'] = {
        'id': data.get('id', 0),
        'user_name': data.get('user_name', ''),
        'role': data.get('role', 0),
        'permission': data.get('permission', [])
    }


def login_out():
    """登出"""
    session.pop('login')


def get_info():
    """获取信息"""
    user_info = session.get('login', {})
    result = {
        'id': user_info.get('id', 0),
        'user_name': user_info.get('user_name', ''),
        'role': user_info.get('role', 0),
        'permission': user_info.get('permission', [])
    }
    return result
