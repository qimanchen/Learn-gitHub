#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-17 09:42:24
# @Author  : Qiman Chen
# @Version : $Id$

"""
事件控制模块
"""
# 待释放请求
from global_params import LIGHTPATH_REQ_END


class PhysicPath(object):
	"""
	实际的物理路径
	可能包含多跳
	"""
	def __init__(self):
		self.fir_ID = None
		self.end_num = None
		self.end_ID = None
		self.link_ID = None
		self.cost = None
		self.down = None


class SPath(object):
	"""
	物理路径
	"""
	def __init__(self):
		self.ID = None
		self.first_ID = None
		self.end_ID = None
		self.state = None
		self.hop = None
		self.cost = None
		self.eb_node = None
		self.eb_node_cap = None
		self.next = None
		self.down = None


class RequestEvent(object):
	"""
	请求事件模块
	"""
	def __init__(self, request_id=0, event_type=None, request_array=None):
		self.request_id = request_id # 请求id

		# 事件类型
		# 1. 新生成的事件
		# 2. 运行中的事件
		# 3. 要释放的事件
		self.type = event_type # 事件类型
		self.request = request_array # 请求数组
		self.req_graph_ar = None # 请求的关系矩阵

		self.create_time = None # 事件请求生成时间
		self.service_time = None # 事件服务时间
		self.vnf_num = None # vnf的个数
		self.next = None # 下一条事件，RequestEvent
		self.sub_path = None # 对应的物理路径


def event_handler(topology, h, fail_num, process_request, no_banwidth_num, no_slot_num, no_cpu):
	"""
	fail_num = Point(0) # 失败的请求
	process_request = Point(1) # 处理的请求的数量
	no_bandwidth_num = Point(0) # 由于没有带宽资源失败的请求的数量
	no_slot_num = Point(0) # 由于没有slot而请求失败的数量
	no_cpu = Point(0) # 由于没有计算资源而请求失败
	处理请求
	不是新的请求

	:param topology: 拓扑对象
	:param h: 事件对象 event_queue
	"""
	code = h.next.type # 事件类型

	# 当事件为新的事件时，需要进行映射
	if code == 1:
		pass
		# 映射请求
	elif code == 10:
		pass
		# 释放请求
	elif code == 100:
		pass
		# 请求末尾
