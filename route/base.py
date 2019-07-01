# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, session, redirect


@app.route('/base/')
def Base():
    """基础配置"""
    if session.get('login'):
        return render_template('base/exec_host_list.html')
    return redirect('/login/')


@app.route('/base/exec/host/update/<int:id>/')
def ExecHostUpdate(id):
    """执行服务器修改"""
    if session.get('login'):
        return render_template('base/exec_host_update.html', server_id=id)
    return redirect('/login/')


@app.route('/base/exec/host/add/')
def ExecHostAdd():
    """新增执行服务器"""
    if session.get('login'):
        return render_template('base/exec_host_add.html')
    return redirect('/login/')


@app.route('/base/alert/')
def Alert():
    """预警配置"""
    if session.get('login'):
        return render_template('base/alert_list.html')
    return redirect('/login/')


@app.route('/base/alert/update/<int:id>/')
def AlertUpdate(id):
    """预警配置修改"""
    if session.get('login'):
        return render_template('base/alert_update.html', conf_id=id)
    return redirect('/login/')


@app.route('/base/alert/add/')
def AlertAdd():
    """预警配置新增"""
    if session.get('login'):
        return render_template('base/alert_add.html')
    return redirect('/login/')
