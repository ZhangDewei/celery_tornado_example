#!/bin/bash
/usr/bin/python -u main_celeryworker.py A worker -E -l info --hostname=PERF_GROUP_A@%h -P threads --loglevel=info
