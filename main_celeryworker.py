#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: tasks.py
#         Desc:
#       Author: orain.xiong
#        Email: orain.xiong@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-05-29 22:14:06
#      History:
#=============================================================================
'''
from celery import Celery
from celery_config import Config
from celery_config import init_queue_conf

if __name__ == "__main__":
    import sys
    PERF_GROUP = sys.argv[1]
    del sys.argv[1]
    app = Celery()
    app.config_from_object(Config)
    app.conf.CELERY_IMPORTS = "workers"
    app.conf.update(CELERY_QUEUES=init_queue_conf(PERF_GROUP))
    app.start()
