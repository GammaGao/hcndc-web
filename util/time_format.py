# !/usr/bin/env python
# -*- coding: utf-8 -*-

import math


def seconds_format(seconds):
    """秒数转化"""
    day = 24 * 60 * 60
    hour = 60 * 60
    minute = 60
    if seconds < 60:
        return "%d秒" % math.ceil(seconds)
    elif seconds > day:
        days = divmod(seconds, day)
        return "%d天 %s" % (int(days[0]), seconds_format(days[1]))
    elif seconds > hour:
        hours = divmod(seconds, hour)
        return '%d小时 %s' % (int(hours[0]), seconds_format(hours[1]))
    else:
        minutes = divmod(seconds, minute)
        return "%d分钟 %d秒" % (int(minutes[0]), math.ceil(minutes[1]))
