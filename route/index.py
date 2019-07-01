# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, session, redirect


@app.route('/home/')
@app.route('/index/')
def Index():
    """首页"""
    if session.get('login'):
        return render_template('interface/interface_list.html')
    return redirect('/login/')
