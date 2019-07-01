# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, session, redirect


@app.route('/job/')
def Job():
    """任务列表"""
    if session.get('login'):
        return render_template('job/job_list.html')
    return redirect('/login/')


@app.route('/job/detail/<int:id>/')
def JobDetail(id):
    """任务详情"""
    if session.get('login'):
        return render_template('job/job_detail.html', job_id=id)
    return redirect('/login/')


@app.route('/job/update/<int:id>/')
def JobUpdate(id):
    """任务修改"""
    if session.get('login'):
        return render_template('job/job_update.html', job_id=id)
    return redirect('/login/')


@app.route('/job/add/')
def JobAdd():
    """新增任务"""
    if session.get('login'):
        return render_template('job/job_add.html')
    return redirect('/login/')
