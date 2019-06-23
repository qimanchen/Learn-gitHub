#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-20 15:40:38
# @Author  : Qiman Chen
# @Version : $Id$

"""
映射算法主体
与算法相关的函数
"""
import copy
# 导入物理路径数据结构
from path_data_struct import OpticPath
# 建立新的链路
from creat_link import creat_rack_osm_wss_link
from topology_wss_op import RackLink


class PP(object):
	"""
	指针对象
	"""
	pass


class VNodePath(object):
	"""
	映射节点路径类
	"""
	
	def __init__(self, rack_id, vnf_id, next=None):
		self.rack = rack_id # 映射的rack
		self.vnf = vnf_id  # 映射的vnf
		self.next = next # 映射的下一个结点

	
class ShortPath(object):
	"""
	记录最大带宽矩阵中元素
	"""

	def __init__(self):
	
		# 链路编号 -- 第几条链路
		self.id = None
		# 起始rack
		self.start_rack = None
		# 终止rack
		self.end_rack = None
		# 起始wss端口
		self.wss_trans = None
		# 终止wss端口
		self.wss_recv = None
		# 对应的RackLink对象
		self.rack_link = None
		# 相应的资源
		self.bandwidth = None
		# 记录相应的CPU
		self.cpu = None
		# 最后一个host的cpu
		self.end_cpu = None
		# 记录对应start_host中的链路记录
		self.start_host_vnf_list = None
		# 记录对应end_host中的链路记录--只针对最后一条链路而言
		self.end_host_vnf_list = None
		# 连接的下一端口
		self.next = None


# 所有仿真通用的
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
		counter = 0
		for j in vnode.keys():
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
			max_mat[in_rack-1][counter] = max_bandwidth
			counter += 1
	return max_mat


# WF n*n的矩阵
# WL n*n*n的矩阵
# n是vnf的个数
# Fm 大小为 n的矩阵 -- 记录vnf的状态（是否被映射）
# 之前算法使用的
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


# 之前算法使用的
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

def get_vnf(r_g_a, fm):
	"""
	得到当前需要映射的vnf，多个同级关系的
	需要进行顺序确定的
	:param r_g_a: vnf等级关系 PP实例化对象
	:param fm: 映射的vnf字典，记录着整个的顺序
	:return: 需要判断关系的vnf列表
	"""
	fi_level = r_g_a.fi_level
	se_level = r_g_a.se_level
	th_level = r_g_a.th_level
	fo_level = r_g_a.fo_level
	mid_level = r_g_a.mid_level
	
	vnf_chosed_list = [] # 需要判断关系的vnfs
	
	vnf_mapped_list = fm
	
	
	# 检测第一等级的vnf
	for vnf_id in fi_level:
		if vnf_id not in vnf_mapped_list:
			vnf_chosed_list.append(vnf_id)
	
	if not vnf_chosed_list:
		# 检测level2
		for vnf_id in se_level:
			if vnf_id not in vnf_mapped_list:
				vnf_chosed_list.append(vnf_id)
	
	if not vnf_chosed_list:
		# 检测level3
		for vnf_id in th_level:
			if vnf_id not in vnf_mapped_list:
				vnf_chosed_list.append(vnf_id)
				
	if not vnf_chosed_list:
		# 检测level4
		for vnf_id in fo_level:
			if vnf_id not in vnf_mapped_list:
				vnf_chosed_list.append(vnf_id)
	
	# 检测与其他vnf都无关系的vnf
	for vnf_id in mid_level:
		if vnf_id not in vnf_mapped_list:
			vnf_chosed_list.append(vnf_id)
			
	return vnf_chosed_list


def vnss(topology, vnode, max_mat,fm, check_vnf, on, pre_rack):
	"""
	有多个vnf可选时判断vnf之间的顺序
	:param on: 当前映射顺序
	:param pre_rack: 前一个选择的rack编号
	"""
	rack_num = topology.rack_num # 物理节点的个数
	
	index_links = topology.index_link # 记录着每个rack连接着那些其他rack
	
	rack_links = topology.rack_link # 获取整topology中建立的链路
	
	vnode_ids = list(vnode.keys()) # 记录着每个vnf所在的index
	
	mid_sum_max_band = {} # 记录多个不同vnf的最大带宽和
	
	max_vnf = [] # 记录最大的vnfs
	# 选中的结点
	chosed_vnf = []
	# 检测是否是第一个节点
	if not fm.value.values():
		# 第一个节点
		for vnf_id in check_vnf:	
			next_vnfs = get_next_vnf(r_g_a, vnf_id, check_vnf)
			# 遍历所有的rack
			mid_max = 0 # 暂时最大值
			for rack in range(rack_num):
				# 找到对应vnf的索引位置
				mid_sum = 0
				for vnf in next_vnfs:
					mid_sum += max_mat[rack][vnode_ids.index(vnf)]
				if mid_max < mid_sum:
					mid_max = mid_sum
			mid_sum_max_band[vnf_id] = mid_max
		
		#确定顺序
		max_band = max(mid_sum_max)
		for vnf in mid_sum_max_band:
			if mid_sum_max_band[vnf]  ==  max_band:
				max_vnf.append(vnf)
		
		#多个相同的vnf，选择具有最大带宽需求的优先
		max_band_list = [vnode(i).bandwidth_require for i in max_vnf]
		max_band = max(max_band_list)
		for i in range(len(max_vnf)):
			if max_band_list[i] == max_band:
				chosed_vnf.append(max_vnf[i])
	else:
		# 检测其他节点，通过前一节点锁定范围
		for vnf_id in check_vnf:
			next_vnfs = get_next_vnf(r_g_a, vnf_id, check_vnf)
			mid_max = 0
			# 从多个物理结点找出最大带宽的结点
			for rack in index_links[pre_rack-1]:
				mid_sum = 0
				for vnf in next_vnfs:
					mid_sum += max_mat[rack][vnode_ids.index(vnf)]
				if mid_max < mid_sum:
					mid_max = mid_sum
			mid_sum_max_band[vnf_id] = mid_max
			
		#确定顺序
		max_band = max(mid_sum_max)
		for vnf in mid_sum_max_band:
			if mid_sum_max_band[vnf]  ==  max_band:
				max_vnf.append(vnf)
		
		#多个相同的vnf，选择具有最大带宽需求的优先
		max_band_list = [vnode(i).bandwidth_require for i in max_vnf]
		max_band = max(max_band_list)
		for i in range(len(max_vnf)):
			if max_band_list[i] == max_band:
				chosed_vnf.append(max_vnf[i])
				
	return chosed_vnf


def enss(topology, vnode, max_mat,fm, vnf_id, on, pre_rack):
	"""
	确定某个vnf可以映射的物理结点
	第一个结点时只是确定第一个rack
	后面再来确认对应的host和RackLink
	:param on: 当前映射顺序
	:param pre_rack: 前一个选择的rack编号
	"""
	rack_num = topology.rack_num # 物理节点的个数
	
	osm_link = topology.link
	
	racks = topology.racks #对应的物理结点的个数
	
	index_links = topology.index_link # 记录着每个rack连接着那些其他rack
	
	rack_links = topology.rack_link # 获取整topology中建立的链路
	
	vnode_ids = list(vnode.keys()) # 记录着每个vnf所在的index
	
	mid_sum_max_band = [] # 记录多个不同vnf的最大带宽和
	
	max_vnf = [] # 记录最大的vnfs
	# 选中的结点
	chosed_node = []
	# 确认可操作vnf
	check_vnf = get_vnf(r_g_a,fm.value.values())
	pre_vnf = fm.value[on]
	
	blocking_type = None
	
	# 检测是否是第一个节点
	if not fm.value.values():
		# 第一个节点
		next_vnfs = get_next_vnf(r_g_a, vnf_id, check_vnf)
		mid_max = 0
		for rack in range(rack_num):
			mid_sum = 0
			# 先找出具有最大带宽的rack
			for vnf in next_vnfs:
				mid_sum += max_mat[rack][vnode_ids.index(vnf)]
			mid_sum_max_band.append(mid_sum)
		# 得到最大的带宽
		max_band = max(mid_sum_max_band)
		# 取得有最大带宽的rack的列表
		max_band_rack = [i+1 for i in range(rack_num) if mid_sum_max_band[i] == max_band]
		# 筛选出满足计算资源的rack
		for rack_id in max_band_rack:
			for host in racks[str(rack_id)].host_using.values:
				if host.avaliable_resource >= vnode[vnf_id].computer_require:
					chosed_node.append(rack_id)
					break
	else:
		# 不是第一个结点需要考虑链路的选择
		next_vnfs = get_next_vnf(r_g_a, vnf_id, check_vnf)
		mid_rack_sum_band = []
		mid_max = 0
		for rack in index_links[pre_rack-1]:
			mid_sum = 0
			# 先找出具有最大带宽的rack
			for vnf in next_vnfs:
				mid_sum += max_mat[rack][vnode_ids.index(vnf)]
			mid_sum_max_band.append(mid_sum)
		# 得到最大的带宽
		max_band = max(mid_sum_max_band)
		# 取得有最大带宽的rack的列表
		max_band_rack = [i+1 for i in range(rack_num) if mid_sum_max_band[i] == max_band]
		
		for rack_id in max_band_rack:
			mid_link = osm_link[str(pre_rack)][rack_id-1]
			for wss_link in mid_link.wss_link:
				mid_rack_link = rack_links["{}_{}_{}".format(pre_rack, rack_id, wss_link)]
				if mid_rack_link.start_host.avaliable_resource >= vnode[pre_vnf].computer_require:
					if mid_rack_link.end_host.avaliable_resource >= vnode[vnf_id].computer_require:
						if mid_rack_link.start_wss_link.bandwidth_avaliable >= vnode[pre_vnf].bandwidth_require:
							chosed_node.append(mid_rack_link)
						else:
							blocking_type = "noBvt"
					else:
						blocking_type = "noEndHost"
				else:
					blocking_type = "noStart_Host"
	if not chosed_node:
		return blocking_type

	return chosed_node
			
	
def get_next_vnf(r_g_a, vnf_id, check_vnf):
	"""
	得到某个vnf的下面可能相连的vnf
	"""
	fi_level = r_g_a.fi_level
	se_level = r_g_a.se_level
	th_level = r_g_a.th_level
	fo_level = r_g_a.fo_level
	mid_level = r_g_a.mid_level
	
	# 检测到的下一个可能映射的vnf
	next_vnfs = []
	
	# vnf从当前可选中选择出可能的下一节点
	for i in check_vnf:
		if i !=  vnf_id:
			next_vnfs .append(i)
	
	# 当同等级的vnf不存在时,则考虑它的下一级节点
	if not next_vnfs:
		# 结点是等级1
		if fi_level and vnf_id in fi_level:
			if se_level:
				next_vnfs.extend(se_level)
			elif th_level:
				next_vnfs.extend(th_level)
			elif fo_level:
				next_vnfs.extend(fo_level)
		elif se_level and vnf_id in se_level:
			if th_level:
				next_vnfs.extend(th_level)
			elif fo_level:
				next_vnfs.extend(fo_level)
		elif th_level and vnf_id in th_level:
			if fo_level:
				next_vnfs.extend(fo_level)
				
	return next_vnfs
		

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
	
	fm = PP() # 存储整个已经映射的vnf -- 字典
	fm.value = {} # {映射顺序：vnf_id}
	
	# 每次映射可以被选择的vnf列表
	chose_vnf_list = [None  for _ in range(vnf_num)]
	# 记录每次选中的vnf列表
	chosed_vnf_list = []
	
	# 每次选中的物理结点
	chose_node_list = [None for _ in range(vnf_num)]
	# 第一个结点返回的rack列表
	# 其他结点返回的RackLink对象
	# 每次操作的对象
	chosed_node_list = []

	max_mat = create_max_array(topology, vnode, vnf_num) # 最大带宽矩阵
	
	sub_node_path = VNodePath() # 映射结点路径
	sub_path = ShortPath() # 映射路径
	blocking_type = 0
	
	for i in range(vnf_num):
		# 开始寻找对应的链路
		backtrack_top = 1 # 用于回溯的参数
		
		# 第一个结点,不用映射物理路径
		if i == 0:
			# 找出需要判断关系的vnf
			check_vnf = get_vnf(r_g_a,fm.value.values())
			# 判断是否先后顺序
			# 当整个没有相应的选择时,并且选中vnf的个数多于一个时
			if not chose_vnf_list[i] and len(check_vnf) > 1:
				chose_vnf_list[i] = vnss(topology, vnode, max_mat,fm, check_vnf, i, None)
				chosed_vnf_list[i] = copy.deepcopy(chose_vnf_list[i])
			elif not chose_vnf_list[i]:
				chose_vnf_list[i] = check_vnf
				chosed_vnf_list[i] = copy.deepcopy(chose_vnf_list[i])
			# 选择相应的物理节点
			for vnf in chosed_vnf_list[i]:
				chose_node_list[i] = enss(topology, vnode, max_mat, fm, vnf,i,None)
				# 确定相应的物理链路-- 加入到链路列表中
				if isinstance(chose_node_list[i], str):
					blocking_type = chose_node_list[i]
					continue
				csub_node_path = sub_node_path
				chose_rack = chose_node_list[i].pop()
				vnf = chosed_vnf_list.pop()
				csub_node_path.next = VNodePath(chose_rack, vnf)
		else:
			# 不是第一个结点
		
		# 其他节点
		# 如果映射失败，返回到上一层检查是否有其他可选节点
		# 如果所有的选择都进行到底了，则返回相应的映射失败的方案
		# 如果整个映射完成，则返回对应的sub_path


	return sub_path, request_state, loss_type