#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-17 09:42:24
# @Author  : Qiman Chen
# @Version : $Id$

"""
时间控制模块
"""


class RequestEvent(object):
	"""
	请求事件模块
	"""

	def __init__(self, request_id, event_type=None):
		self.request_id = request_id # 请求id

		# 事件类型
		# 1. 新生成的事件
		# 2. 运行中的事件
		# 3. 要释放的事件
		self.event_type = event_type

		self.create_time = None # 事件请求生成时间
		self.service_time = None # 事件服务时间
		 