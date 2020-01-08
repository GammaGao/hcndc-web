# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, session, redirect

from configs import app
from server.request import get_arg


@app.route('/ftp/event/')
def FtpEvent():
    """文件事件列表"""
    if session.get('login'):
        return render_template('ftp_event/ftp_event_list.html')
    return redirect('/login/')


@app.route('/ftp/event/update/<int:ftp_event_id>/')
def FtpEventUpdate(ftp_event_id):
    """文件事件修改"""
    if session.get('login'):
        return render_template('ftp_event/ftp_event_update.html', ftp_event_id=ftp_event_id)
    return redirect('/login/')


@app.route('/ftp/event/add/')
def FtpEventAdd():
    """文件事件调度"""
    if session.get('login'):
        return render_template('ftp_event/ftp_event_add.html')
    return redirect('/login/')


@app.route('/ftp/event/run/')
def FtpEventRun():
    """立即执行参数配置页面"""
    ftp_event_id = get_arg('ftp_event_id', '')
    if session.get('login'):
        return render_template('ftp_event/ftp_event_start.html', ftp_event_id=ftp_event_id)
    return redirect('/login/')
