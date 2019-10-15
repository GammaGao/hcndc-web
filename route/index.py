# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, session, redirect

from configs import app


@app.route('/favicon.ico')
def favicon():
    """静态图标映射"""
    return redirect('/static/favicon.ico')


@app.route('/home/')
@app.route('/index/')
def Index():
    """首页"""
    if session.get('login'):
        return render_template('interface/interface_list.html')
    return redirect('/login/')
