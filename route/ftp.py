# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, session, redirect

from configs import app


@app.route('/ftp/')
def Ftp():
    """FTP配置列表"""
    if session.get('login'):
        return render_template('ftp/ftp_list.html')
    return redirect('/login/')


@app.route('/ftp/update/<int:ftp_id>/')
def FtpUpdate(ftp_id):
    """FTP配置修改"""
    if session.get('login'):
        return render_template('ftp/ftp_update.html', ftp_id=ftp_id)
    return redirect('/login/')


@app.route('/ftp/add/')
def FtpAdd():
    """FTP配置新增"""
    if session.get('login'):
        return render_template('ftp/ftp_add.html')
    return redirect('/login/')
