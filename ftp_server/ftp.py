# !/usr/bin/env python
# -*- coding: utf-8 -*-

import ftplib


class FtpLink(object):
    def __init__(self, host, port, user, password):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port)
        self.ftp.login(user, password)

    def test_dir(self, remote_path):
        """检测文件夹是否存在"""
        try:
            self.ftp.cwd(remote_path)
            return True
        except ftplib.error_perm:
            return False
