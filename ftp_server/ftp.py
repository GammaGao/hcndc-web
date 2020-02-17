# !/usr/bin/env python
# -*- coding: utf-8 -*-

import ftplib


class FtpLink(object):
    def __init__(self, host, port, user, password, encoding='utf-8'):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port)
        self.ftp.encoding = encoding
        if user and password:
            self.ftp.login(user, password)

    def test_dir(self, remote_path):
        """检测文件夹是否存在"""
        try:
            self.ftp.cwd(remote_path)
            return True
        except ftplib.error_perm:
            return False

    def test_file(self, remote_path, file_name):
        """检测文件是否存在"""
        try:
            self.ftp.cwd(remote_path)
            return file_name in self.ftp.nlst()
        except ftplib.error_perm:
            return False

    def close(self):
        """关闭连接"""
        self.ftp.close()
