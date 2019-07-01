# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, redirect
from flask import session


@app.route('/login/')
def Login():
    """登录页面"""
    if session.get('login'):
        return redirect('/index/')
    return render_template('login.html')
