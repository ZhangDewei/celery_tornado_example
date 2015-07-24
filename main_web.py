#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: main_web.py
#         Desc:
#       Author: linfeng.yuan
#        Email: linfeng.yuan@woqutech.com
#     HomePage: www.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-07-23 13:48:36
#      History:
#=============================================================================
'''
#from tornado.options import define, options, parse_command_line
import tornado.options
import tornado.ioloop
import tornado.web
from tornado_settings import application, DEFAULT_PORT
import workers
import tcelery


def main():
    tcelery.setup_nonblocking_producer()
    tornado.options.define("port", default=DEFAULT_PORT, help="run on the given port", type=int)
    tornado.options.parse_command_line()

    app = application.Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
