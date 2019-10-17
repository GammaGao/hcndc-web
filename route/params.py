# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app

from flask import render_template, session, redirect


@app.route('/params/')
def Params():
    """参数列表"""
    if session.get('login'):
        return render_template('params/params_list.html')
    return redirect('/login/')


@app.route('/params/update/<int:id>/')
def ParamsUpdate(id):
    """参数修改"""
    if session.get('login'):
        return render_template('params/params_update.html', param_id=id)
    return redirect('/login/')


@app.route('/params/add/')
def ParamsAdd():
    """新增参数"""
    if session.get('login'):
        return render_template('params/params_add.html')
    return redirect('/login/')
