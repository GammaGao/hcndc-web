# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, session, redirect


@app.route('/interface/')
def Interface():
    """工作流列表"""
    if session.get('login'):
        return render_template('interface/interface_list.html')
    return redirect('/login/')


@app.route('/interface/detail/<int:id>/')
def InterfaceDetail(id):
    """工作流详情"""
    if session.get('login'):
        return render_template('interface/interface_detail.html', interface_id=id)
    return redirect('/login/')


@app.route('/interface/update/<int:id>/')
def InterfaceUpdate(id):
    """工作流修改"""
    if session.get('login'):
        return render_template('interface/interface_update.html', interface_id=id)
    return redirect('/login/')


@app.route('/interface/add/')
def InterfaceAdd():
    """新增工作流"""
    if session.get('login'):
        return render_template('interface/interface_add.html')
    return redirect('/login/')


@app.route('/test/')
def AllJobShow():
    """所有任务展示"""
    return render_template('test.html')
