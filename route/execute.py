# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, session, redirect


@app.route('/execute/flow/')
def ExecuteFlow():
    """任务流日志列表"""
    if session.get('login'):
        return render_template('execute/execute_flow.html')
    return redirect('/login/')


@app.route('/execute/job/')
def ExecuteJob():
    """任务日志列表"""
    if session.get('login'):
        return render_template('execute/execute_job.html')
    return redirect('/login/')


@app.route('/execute/flow/history/<int:dispatch_id>/')
def ExecuteFlowHistory(dispatch_id):
    """任务流历史日志"""
    if session.get('login'):
        return render_template('execute/execute_flow_history.html', dispatch_id=dispatch_id)
    return redirect('/login/')


@app.route('/execute/flow/detail/<int:exec_id>/')
def ExecuteFlowDetail(exec_id):
    """任务流执行详情"""
    if session.get('login'):
        return render_template('execute/execute_flow_detail.html', exec_id=exec_id)
    return redirect('login')


@app.route('/execute/job/log/<int:exec_id>/<int:job_id>/<int:page_type>/')
def ExecuteJobLog(exec_id, job_id, page_type):
    """任务执行日志"""
    if session.get('login'):
        return render_template('execute/execute_job_log.html', exec_id=exec_id, job_id=job_id, page_type=page_type)
    return redirect('login')


@app.route('/execute/job/history/<int:job_id>/')
def ExecuteJobHistory(job_id):
    """任务历史日志"""
    if session.get('login'):
        return render_template('execute/execute_job_history.html', job_id=job_id)
    return redirect('login')


@app.route('/execute/restart/<int:exec_id>/')
def ExecuteRestart(exec_id):
    """断点重跑参数设置"""
    if session.get('login'):
        return render_template('execute/execute_restart.html', exec_id=exec_id)
    return redirect('login')
