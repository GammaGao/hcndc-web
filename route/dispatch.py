# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, session, redirect

from configs import app
from server.request import get_arg


@app.route('/dispatch/')
def Dispatch():
    """调度列表"""
    if session.get('login'):
        return render_template('dispatch/dispatch_list.html')
    return redirect('/login/')


@app.route('/dispatch/update/<int:dispatch_id>/')
def DispatchUpdate(dispatch_id):
    """调度修改"""
    if session.get('login'):
        return render_template('dispatch/dispatch_update.html', dispatch_id=dispatch_id)
    return redirect('/login/')


@app.route('/dispatch/add/')
def DispatchAdd():
    """新增调度"""
    if session.get('login'):
        return render_template('dispatch/dispatch_add.html')
    return redirect('/login/')


@app.route('/dispatch/run/')
def DispatchRun():
    """立即执行参数配置页面"""
    dispatch_id = get_arg('dispatch_id', '')
    if session.get('login'):
        return render_template('dispatch/dispatch_start.html', dispatch_id=dispatch_id)
    return redirect('/login/')
