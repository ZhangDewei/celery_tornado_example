#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: __init__.py
#         Desc: 
#       Author: linfeng.yuan
#        Email: linfeng.yuan@woqutech.com
#     HomePage: www.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-07-09 19:26:16
#      History:
#=============================================================================
'''
from workers import regist_task
from workers import QMonitor

regist_task(QMonitor)
