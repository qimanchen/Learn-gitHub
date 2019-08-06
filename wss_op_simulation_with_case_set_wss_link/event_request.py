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

from global_params import RequestEvent
# 导入请求处理函数
from algorithm import request_mapping
# 测试新算法
# from algorithm_first_fit import request_mapping
# 导入物理网路建路和删路函数
from creat_link import creat_rack_osm_wss_link
from creat_link import release_rack_osm_wss_link
# 导入更新物理网络资源和释放物理网络资源的函数
from creat_link import renew_resources
from creat_link import release_resources
# 导入请求改变函数
from request_set import add_request


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
	vnode = h.next.request
	blocking_type = None

	# 当事件为新的事件时，需要进行映射
	if code == 1:
		pp.process_request += 1
		# 映射请求
		# 对应的值分别是，阻塞类型(正常返回None), 对应的物理路径， 对应的结点和vnf链表
		blocking_type, sub_path, sub_node_path, success_type = request_mapping(topology, h.next)

		if not blocking_type:
			# 请求处理成功
			# 更新物理网络的资源状态
			if success_type == "normal":
				pp.normal += 1
			elif success_type == "case_repeat":
				pp.case_repeat += 1
			elif success_type == "case1":
				pp.case1 += 1
			elif success_type == "case2":
				pp.case2 += 1
			elif success_type == "case3":
				pp.case3 += 1
			elif success_type == "case4":
				pp.case4 += 1
			pp.success += 1
			csub_path = sub_path
			renew_resources(topology, csub_path, vnode)
		else:
			# 请求处理失败
			pp.fail_num += 1
			if blocking_type == 'noEndHost' or blocking_type == "noStartHost":
				pp.no_cpu +=1
			elif blocking_type == 'noTrans' or blocking_type == "noRecv":
				pp.no_bandwidth_num += 1
				pp.no_trans += 1
			elif blocking_type == "noStartSlot":
				pp.no_bandwidth_num += 1
				pp.no_slot_num += 1
				pp.no_start_slot += 1
			elif blocking_type == "noEndSlot":
				pp.no_bandwidth_num += 1
				pp.no_slot_num += 1
				pp.no_end_slot += 1
			elif blocking_type == "other":
				pp.no_bandwidth_num += 1

		# 更新请求状态
		service_time = h.next.service_time + h.next.create_time
		add_request(h, LIGHTPATH_REQ_END, h.next.req_graph_ar, h.next.request, service_time, 0, h.next.request_id, h.next.vnf_num,sub_path)
		# 更新请求队列
		tmp_h = h.next
		h.next = tmp_h.next

	elif code == 10:
		# 释放请求
		release_resources(h.next.sub_path, h.next.request, topology)
		tmp_h = h.next
		h.next = tmp_h.next
	elif code == 100:
		pass
		# 请求末尾
