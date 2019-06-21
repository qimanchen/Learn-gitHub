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
# 建立新的链路
from creat_link import creat_rack_osm_wss_link
from topology_wss_op import RackLink


class ShortPath(object):
	"""
	记录最大带宽矩阵中元素
	"""

	def __init__(self):
		# 起始rack
		self.start_rack = None
		# 终止rack
		self.end_rack = None
		# 起始wss端口
		self.wss_trans_port = None
		# 终止wss端口
		self.wss_recv_port = None


def create_max_array(topology, vnode, vnf_num):
	"""
	构建最大带宽关系矩阵
	每个节点对应着各种vnf的最大带宽矩阵

	:param topology: 整个仿真系统的topo对象
	:param vnode: {vnode_num: } # vnf结点字典
	:param vnf_num: vnf的个数
	"""
	rack_num = topology.rack_num # 物理节点的个数
	
	osm_links = topology.link # 以rack节点为索引检索最大带宽

	rack_links = topology.rack_link # 获取整topology中建立的链路
	# 同样以OSMOpticalLink的对象内的wss_link对应着外部的索引
	# 取出recv的数量

	# 当检测到没有实际的物理路径时，建立一条新的链路以支持

	# 对应物理资源
	# 对应的带宽资源 

	max_mat = [[0 for i in range(vnf_num)] for _ in range(rack_num)]

	# 针对每个rack, rack的编号是从1开始的
	for in_rack in range(1, rack_num+1):
		# 针对每个vnf
		for j in range(1, vnf_num+1):
			# 针对每个in_rack的out_rack是否满足映射对应的最大带宽矩阵
			# 当检测到没有足够的资源时，建立一条新的链路 RackLink
			# 或当检测到初始状态（还没建立过任何一条链路时，建立一条新的链路）
			max_bandwidth = 0 # 得到最大的带宽值
			for out_rack in range(rack_num):
				# 注意对应的out rack的编号需要加1
				osm_link = osm_links[str(in_rack)][out_rack]
				# 检测到rack之间存在链路
				if osm_link != "None":
					# 检测到还没建立任何光路，建立初始链路
					if osm_link.wss_link is None:
						# 建立新的链路
						creat_state = creat_rack_osm_wss_link(topology, in_rack, out_rack+1)
						# 建路失败
						if not isinstance(creat_state, type(RackLink)):
							pass
					# 遍历所有两个rack之间建立的链路，找出最大带宽的需求
					# 记录是否所有存在链路都符合对应的需求
					count = 0
					for wss_ports, wss_link in osm_link.wss_link.items():
						# 找到对应的终结点
						if rack_links['{}_{}_{}'.format(in_rack, out_rack+1, wss_ports)].end_host.avaliable_resource >= vnode[j].computer_require:
							count += 1 # 标记存在可用的链路
							# 找到所有的最大的带宽值
							if wss_link.bandwidth_avaliable > max_bandwidth:
								max_bandwidth = wss_link.bandwidth_avaliable
					# 当所有的存在链路都不满足时，建立一条新的链路
					if count == 0:
						creat_state = creat_rack_osm_wss_link(topology, in_rack, out_rack+1)
						# 建路成功
						if isinstance(creat_state, type(RackLink)):
							# 直接等于最大带宽值
							max_bandwidth = creat_state.start_wss_link.bandwidth_avaliable

			max_mat[in_rack-1][j-1] = max_bandwidth

	return max_mat


# WF n*n的矩阵
# WL n*n*n的矩阵
# n是vnf的个数
# Fm 大小为 n的矩阵 -- 记录vnf的状态（是否被映射）

def read_rga_link(r_g_a, n, on):
	"""
	读取关系拓扑图
	:param r_g_a: vnf之间的关系拓扑
	:param n: 请求中vnf的个数
	:param on: 映射的第on+1个结点 -- on从0开始
	:param fm:
	:param wf:
	:param wl:
	"""
	mid = r_g_a # 请求链关系拓扑

	mid_i = 0
	mid_first = 0
	counter = 0
	counterr = 0
	fm = [0 for _ in range(n)]
	wf = [[0 for _ in range(n)] for _ in range(n)]
	wl = [[[0 for _ in range(n)] for _ in range(n)] for _ in range(n)]

	# 寻找到最前面的vnf
	for j in range(n):

		if (mid[mid_i][j] != 2) and (j == (n-1)) and (fm[mid_i] == 0):
			mid_first = mid_i
			wf[on][mid_i] = 1
			break
		elif (mid[mid_i][j] != 2) and (j == (n-1)) and (fm[mid_i] != 0):
			mid_i += 1

			if mid == n:
				mid_i == 0
			j = -1
			if mid_i == n:
				mid_i = 0
		elif (mid[mid_i][j] == 2) and (fm[mid_i] == 0) and (j == n-1) and fm[j] != 0:
			mid_first = mid_i
			wf[on][mid_i] = 1
			break
		elif mid[mid_i][j] == 2 and fm[j] == 0:
			mid_i = j
			j = -1

		if j == n-1:
			for i in range(n):
				if wf[on][i] == 0:
					counter += 1
			if counter == n:
				mid_i += 1
				if mid_i == n:
					mid_i = 0
				j = -1
				counter = 0
			else:
				counter = 0
	# 寻找并行的vnf
	for j in range(n):
		if mid[mid_first][j] == 32676 and fm[j] == 0:
			for i in range(n):
				if mid[j][i] == 2:
					if mid[i][mid_first] == 32676:
						counter += 1
			if counterr == 0:
				wf[on][j] = 1
			else:
				counterr = 0

	fail_in = 0
	# 寻找后面的vnf
	for j in range(n):
		if wf[on][j] == 1:
			for in_j in range(n):
				if mid[j][in_j] == 32676 and fm[in_j] == 0:
					wl[on][j][in_j] = 1
				elif mid[j][in_j] == -2:
					for in_in_j in range(n):
						if mid[in_j][in_in_j] == 2 and mid[in_in_j][j] == 2 and in_in_j != j:
							fail_in += 1
					if fail_in == 0:
						wl[on][j][in_j] = 1
				fail_in = 0
	return fm, wf, wl


def chose_y_n(wf, n, on):
	"""
	从vnf forwarding graph中选择一个vnf
	:param wf:
	:param n: vnf的个数
	:param on: 映射的第on+1个vnf
	"""
	counter = 0
	for i in range(n):
		if wf[on][i] == 1:
			counter += 1
	if counter >= 2:
		return 1
	else:
		return 0


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