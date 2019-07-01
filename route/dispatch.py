# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, session, redirect


@app.route('/dispatch/')
def Dispatch():
    """调度列表"""
    if session.get('login'):
        return render_template('dispatch/dispatch_list.html')
    return redirect('/login/')


@app.route('/dispatch/update/<int:id>/')
def DispatchUpdate(id):
    """调度修改"""
    if session.get('login'):
        return render_template('dispatch/dispatch_update.html', dispatch_id=id)
    return redirect('/login/')


@app.route('/dispatch/add/')
def DispatchAdd():
    """新增调度"""
    if session.get('login'):
        return render_template('dispatch/dispatch_add.html')
    return redirect('/login/')
