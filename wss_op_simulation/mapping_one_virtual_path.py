#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-01 16:12:48
# @Author  : Qiman Chen
# @Version : $Id$

"""
映射一条虚拟链路

需要参数提供相应的：
topology对象
物理起点
物理终点
"""

class PhysicPath(object):
	"""
	主要处理物理路径的映射
	"""

def creat_new_path(topology, start_rack, end_rack):
	"""
	建立新的光路：
	主要针对wss内部的建路
	bvt的选择
	slot的匹配
	"""
	# 对应的osm的链路
	osm_link_object = topology.link[str(start_rack)][int(end_rack)-1]

	# 确定需要操作的wss端口
	# 对应着start rack的上行wss的输出端口
	start_rack_wss_port = osm_link_object.start_port.physic_port.wss_port
	# 对应着end rack的下行wss的输入端口
	end_rack_wss_port = osm_link_object.end_port.physic_port.wss_port

	# 确定需要操作的wss
	start_rack_wss = topology.racks[str(start_rack)].up_wss
	end_rack_wss = topology.racks[str(end_rack)].down_wss

	# 确定需要操作的rack对象
	start_rack_object = topology.racks[str(start_rack)]
	end_rack_object = topology.racks[str(end_rack)]

def mapping_virtual_path(start_rack, end_rack, topology, require_bandwidth=0):
	"""
	映射第一条链路
	1. wss的建路
	2. bvt的设置
	3. slot的设置
	4. 相关资源的更新

	:param require_bandwidth: 虚拟链需要的带宽
	"""
	# 对应的osm的链路
	osm_link_object = topology.link[str(start_rack)][int(end_rack)-1]

	# 确定需要操作的wss端口
	# 对应着start rack的上行wss的输出端口
	start_rack_wss_port = osm_link_object.start_port.physic_port.wss_port
	# 对应着end rack的下行wss的输入端口
	end_rack_wss_port = osm_link_object.end_port.physic_port.wss_port

	# 确定需要操作的wss
	start_rack_wss = topology.racks[str(start_rack)].up_wss
	end_rack_wss = topology.racks[str(end_rack)].down_wss

	# 确定需要操作的rack对象
	start_rack_object = topology.racks[str(start_rack)]
	end_rack_object = topology.racks[str(end_rack)]

	# 操作start rack

	# 操作end rack

def select_slot_plan(start_rack_object, end_rack_object, start_rack_wss_port, end_rack_wss_port):
	"""
	确定光路的slot plan
	slot plan要确定两端的wss都是可用的
	"""

def select_bvt_plan(start_rack_object, end_rack_object):
	"""
	确定目标rack的bvt
	"""


def delete_virtul_path(start_rack, end_rack, topology):
	"""
	释放一条虚拟链路占用的资源
	"""