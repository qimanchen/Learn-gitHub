#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-20 15:40:38
# @Author  : Qiman Chen
# @Version : $Id$

"""
映射算法主体
与算法相关的函数
"""
# 导入物理路径数据结构
from path_data_struct import OpticPath

def create_max_array(topology, vnode, vnf_num):
	"""
	构建最大带宽关系矩阵
	每个节点对应着各种vnf的最大带宽矩阵
	"""
	rack_num = topology.rack_num # 物理节点的个数
	osm = topology.osm
	osm.optical_link 

	max_mat = [[0 for i in range(vnf_num)] for _ in range(rack_num)]




def read_rga_link():
	"""
	读取关系拓扑图
	"""


def request_mapping(topology, event):
	"""
	请求处理模块
	"""
	sub_path = None # 映射处理后的物理链路
	request_state = None # 请求的处理状态，True or False
	loss_type = None # 请求映射失败的原因

	vnode = event.request # 请求结点列表
	r_g_a = event.req_graph_ar # 请求关系矩阵
	vnf_num = event.vnf_num # vnf的个数

	max_mat = create_max_array(topology, vnode, vnf_num)

	for i in range(vnf_num):
		# 开始寻找对应的链路
		backtrack_top = 1 # 用于回溯的参数

		if i == 0:
			# 第一个结点
			backtarck_in = 0



	return sub_path, request_state, loss_type