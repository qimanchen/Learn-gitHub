#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-01 16:31:10
# @Author  : Qiman Chen
# @Version : $Id$

"""
各种路径的数据结构
"""


class OpticPath(object):
	"""
	光路数据结构
	两个rack之间相连的物理光路
	物理映射链路
	"""
	def __init__(self):

		# 链路的编号 -- 物理链路的第几条
		self.path_num = None
		# 起始rack
		self.start_rack = None
		# 起始rack中，上行wss的光路
		self.start_rack_wss_path = None
		# 发射收发机
		self.start_rack_send_bvt = None

		# 终止rack
		self.end_rack = None
		# 终止rack中，下行wss的光路
		self.end_rack_wss_path = None
		# 接收收发机
		self.end_rack_recv_bvt = None

		# osm中的连接
		# OSMOpticalLink
		self.osm_path = None

		# 光路中的slot -- 波长
		self.slot_plan = None # [1,2,3,4]

		# 光路中带宽 -- 可用的带宽 -- 受bvt的影响
		self.bandwidth_avaliable = None
		# host
		self.start_host = None
		self.end_host = None

		self.next_path = None # OpticalPath 对象 表示它连接的下一条光路
		self.pre_path = None # OpticalPath 对象 表示它连接的上一条光路，第一条光路除外
		self.virtual_path = None # 该光学链路对应的虚拟链路


class VirtualPath(object):
	"""
	虚拟链路数据结构
	两个VNF之间的连接
	"""
	def __init__(self):
		pass