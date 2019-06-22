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
# 导入请求处理函数
from algorithm import request_mapping
# 导入物理网路建路和删路函数
from creat_link import creat_rack_osm_wss_link
from creat_link import release_rack_osm_wss_link


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


def event_handler(topology, h, pp):
	"""
	pp = PP() # 仿真测试参数类
	pp.fail_num = 0 # 失败请求数
	pp.process_request = 1 # 处理的请求数
	pp.no_bandwidth_num = 0 # 由于没有带宽资源失败的请求数
	pp.no_slot_num = 0 # 由于没有slot而失败的请求数
	pp.no_cpu = 0 # 由于没有计算资源而失败的请求数
	pp.switch_wss = 0 # 通过wss转接而实现映射的请求

	:param topology: 拓扑对象
	:param h: 事件对象 event_queue
	:param pp: 测试参数类实例
	"""
	code = h.next.type # 事件类型

	# 当事件为新的事件时，需要进行映射
	if code == 1:
		pp.process_request += 1
		# 映射请求
		sub_path, request_state, loss_type = request_mapping(topology) # 返回对应的物理路径，请求处理状态，请求失败类型

		if request_state:
			# 请求处理成功
			pass
		else:
			# 请求处理失败
			pp.fail_num += 1
			if loss_type == 1:
				pp.no_cpu +=1
			elif loss_type == 2:
				pp.no_slot_num += 1
			elif loss_type == 3:
				pp.no_bandwidth_num += 1


	elif code == 10:
		pass
		# 释放请求
	elif code == 100:
		pass
		# 请求末尾
