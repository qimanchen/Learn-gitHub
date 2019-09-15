#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-09-08 18:25:40
# @Author  : Qiman Chen
# @Version : $Id$

"""
日志装饰器
"""
import functools
from global_params import count_wss_oprator


def log_wss_link_create(func):
	@functools.wraps(func)
	def wrapper(*args,**kwargs):
		# global CREATE_WSS_LINK
		ret = func(*args, **kwargs)
		if not isinstance(ret, str):
			count_wss_oprator.CREATE_WSS_LINK += 1
		return ret
	return wrapper

def log_wss_link_release(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		# global RELEASE_WSS_LINK
		ret = func(*args, **kwargs)
		count_wss_oprator.RELEASE_WSS_LINK += 1
		return ret
	return wrapper