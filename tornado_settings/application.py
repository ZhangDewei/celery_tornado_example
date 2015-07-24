#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: application.py
#         Desc:
#       Author: linfeng.yuan
#        Email: linfeng.yuan@woqutech.com
#     HomePage: www.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-07-20 15:28:46
#      History:
#=============================================================================
'''
import tornado.web
import os
import sys
import tornado_settings
import yaml
import logging
import traceback

class Application(tornado.web.Application):
    def __init__(self):
        handlers = self._load_handlers()
        settings = dict(
            login_url="/auth/login",
            xsrf_cookies=False,
            debug=True,
            )
        tornado.web.Application.__init__(self,handlers,**settings)

    def _load_handlers(self):
        configfile = yaml.load(open(os.path.join(tornado_settings.CURPATH, "tornado_settings/handlers.yml")))
        legal_handlers = list()
        handlers = configfile['handlers']
        for handler in handlers:
            url = handler['url']
            clz_path = handler['handler']
            clz = self._import_clz(clz_path)
            opts = handler.get('opts',None)
            if not clz:
                logging.error("FAILED TO LOAD %s"%clz_path)
                continue

            if opts is None:
                hndlr = (url,clz)
            else:
                hndlr = (url,clz,opts)

            if hndlr not in legal_handlers:
                legal_handlers.append(hndlr)

        return legal_handlers

    def _import_clz(self, clz_path):
        full_path = clz_path.split('.')
        if len(full_path) == 1:
            return None
        mod_path = '.'.join(full_path[:-1])
        clz_name = full_path[-1]
        try:
            module = __import__(mod_path, fromlist=[clz_name])
            return getattr(module, clz_name, None)
        except Exception, e:
            logging.error("ERROR when import module %s"%(mod_path,))
            return None
