#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-07-28 16:39:55
# @Author  : Qiman Chen
# @Version : $Id$

"""
根据first fit的原则的算法实现
"""
import copy
# 导入物理路径数据结构
from path_data_struct import OpticPath
# 建立新的链路
from creat_link import creat_rack_osm_wss_link_with_id
# 建立bypass链路
from create_switch_link import creat_rack_switch_link
from topology_wss_op import RackLink
from modify_osm_link import change_osm_link

from global_params import INIT_BANDWIDTH
from global_params import INIT_COMPUTER_RESOURCE
from wss_osm_para import BVTNUM, WSSSLOT, DEGREE


class PP(object):
	"""
	指针对象
	"""
	pass


def get_rack_resources_userate(topology):
	"""
	生成整个系统中rack资源的使用情况

	# 1. 根据rack的利用率来实现
		a. 计算资源
		b. trans
		c. 上层连接端口的使用率
	"""
	racks = topology.racks # 对应的物理结点

	cpu_status = {} # 所有rack计算资源使用的情况
	# 发射机和接收机使用的次数
	trans_status = {} # 所有rack的发射机使用的情况
	recv_status = {} # 所有rack的接收机的使用情况

	# up wss 统计输出端口
	# down wss 统计输入端口
	up_wss_out_port_status = {} # 所有rack的up wss的上层接口的使用情况
	down_wss_in_port_status = {} # 所有rack的down wss的下行接口的使用情况

	index_link = topology.index_link # 每个rack连接的rack
	osm_link = topology.link

	for rack in racks:
		# 获取资源状态
		# rack_avaliable_cpu = racks[rack].avaliable_resource
		# rack_trans_using = racks[rack].trans_using
		# rack_recv_using = racks[rack].recv_using
		rack_up_wss = racks[rack].up_wss
		rack_down_wss = racks[rack].down_wss

		# 更新对应的信息列表
		# 记录使用的资源最少
		cpu_status[rack] = racks[rack].computer_resource - racks[rack].avaliable_resource
		trans_status[rack] = len(racks[rack].trans_using)
		recv_status[rack] = len(racks[rack].recv_using)

		# 更新对应wss中 端口（到各个rack的次数）的使用次数
		mid_port_status = {}
		for out_rack in index_link[int(rack)-1]:
			mid_osm_link = osm_link[rack][out_rack-1] # 对应rack之间的osm链路
			start_port = mid_osm_link.start_port.physic_port.wss_port
			slot_use = start_port.slot_use
			# 记录对应连接rack对应wss端口的使用次数
			mid_port_status[out_rack] = len(slot_use) if slot_use else 0
		up_wss_out_port_status[rack] = mid_port_status

		mid_port_status = {}
		for in_port in rack_down_wss.in_port:
			slot_use = rack_down_wss.in_port[in_port].slot_use
			mid_port_status[in_port] = len(slot_use) if slot_use else 0
		down_wss_in_port_status[rack] = mid_port_status
	return cpu_status, trans_status, recv_status, up_wss_out_port_status, down_wss_in_port_status

def get_resource_rate(rack_num, cpu_status, trans_status, recv_status, up_wss_out_port_status, down_wss_in_port_status):
	"""
	每一映射只需要计算一次
	获取每个rack的资源使用权重比
	cpu，trans，recv，up_wss out_port, down_wss in_port -- 使用次数
	"""
	# 对应参数的初始参数
	init_cpu = INIT_COMPUTER_RESOURCE*BVTNUM
	init_slot = WSSSLOT//4
	init_bd = INIT_BANDWIDTH
	init_bvt = BVTNUM
	init_degree = DEGREE
	init_port_num = init_slot * init_degree # 上层连接端口的总数

	# 连接osm的端口使用的总次数
	use_num_up_wss_out_port = {rack_id: sum(port_use_num.values()) for rack_id, port_use_num in up_wss_out_port_status.items()}
	use_num_down_wss_in_port = {rack_id: sum(port_use_num.values()) for rack_id, port_use_num in down_wss_in_port_status.items()}

	# 根据权重来求对应的比率
	rate_list = {} # 存储相应rack的比率
	for rack_id in range(1, rack_num+1):
		rack_id = str(rack_id)
		# 计算 计算资源使用率，发射机的使用率，接收机使用率，上层端口使用率之和
		rate_list[rack_id] = cpu_status[rack_id]/init_cpu + trans_status[rack_id]/init_bvt + recv_status[rack_id]/init_bvt\
		+ use_num_up_wss_out_port[rack_id]/init_port_num + use_num_down_wss_in_port[rack_id]/init_port_num
	return rate_list

# 当判断的两rack之间没有对应的链路时，就建路
# 释放资源时，会删除对应的空闲链路
def chose_first_node(topology, on, pre_rack, rack_mapped, vnode, fm, vnf_id, rate_list, cpu_status, trans_status, recv_status, up_wss_out_port_status, down_wss_in_port_status):
	"""
	得到第一个rack -- 请求链的第一个物理结点

	# 1. 根据rack的利用率来实现
		a. 计算资源
		b. trans
		c. 上层连接端口的使用率
	"""
	# 1. 先初步确定rack
	# 条件
	# 使用的计算资源少的，同时对应的连接出去的端口使用的次数少的
	# 若这些都一样，再根据相应的trans和recv的使用次数来确定

	# 物理系统中的参数
	rack_num = topology.rack_num # 系统中包含的rack数
	racks = topology.racks
	osm_link = topology.link
	index_link = topology.index_link
	rack_link = topology.rack_link

	# 需要映射的vnf的需要的资源
	vnf_need_cpu = vnode[vnf_id].computer_require
	vnf_need_bd = vnode[vnf_id].bandwidth_require

	# 已经被选择的结点
	rack_mapped_list = list(rack_mapped.value.values())

	blocking_type = None # 阻塞类型

	second_chose_rack = [] # 第二阶段选择
	# 第一个结点
	if on == 0:
		# 排序找出相应的结点 -- 从小到大
		sorted_rate = sorted(list(rate_list.items()), key=lambda x: x[1])
		# 只取前面degree -- 4个rack
		# 只是通过物理层的情况，选择出相应的rack
		# first_chose_rack -- 存储rack的编号
		first_chose_rack = [sorted_rate[rack_index][0] for rack_index in range(len(sorted_rate)) if rack_index < DEGREE]
		# 再根据vnf确定对应的物理结点
		# 2. 再根据vnf进一步确定
		# a. 先确定选出来的rack的cpu是否满足
		# b. 确定选出的rack的上层连接度（是否是最小）
		# c. 确定是否满足相应的带宽需求（没有链路时，建立一条新的链路）
		# d. 确定相应的结点

		# TODO 尝试提前判断第一个结点的连接的下一结点的情况
		for rack_id in first_chose_rack:
			if racks[rack_id].avaliable_resource >= vnf_need_cpu:
				second_chose_rack.append(int(rack_id))
				break
		else:
			blocking_type = "noStartHost"
	else:
		# 其他结点
		pre_vnf = fm.value[on-1]
		rack_link_rate_list = {}

		# pre_rack 连接的rack情况
		for rack_id in index_link[pre_rack-1]:
			rack_link_rate_list[rack_id] = rate_list[str(rack_id)]
		# 根据相应的权重比 -- 排序
		sorted_rate = sorted(list(rack_link_rate_list.items()), key=lambda x:x[1])

		# 每次只考虑一个
		for end_rack_id, rate in sorted_rate:
			# 找到一个满足相应计算资源的rack
			if end_rack_id in rack_mapped_list:
				# 排除已经使用过的结点
				continue
			if racks[str(end_rack_id)].avaliable_resource >= vnf_need_cpu:
				mid_osm_link = osm_link[str(pre_rack)][int(end_rack_id)-1]
				if not mid_osm_link.wss_link:
					# 当没有任何链路时, 建立一条新的链路，并直接返回
					new_rack_id, new_rack_ob = creat_rack_osm_wss_link_with_id(topology, int(pre_rack), int(end_rack_id))
					# 找到对应的结点 -- 直接返回
					second_chose_rack.append((new_rack_id, new_rack_ob))
					break
				signal_link = 0
				for wss_link_id, wss_link_ob in mid_osm_link.wss_link.items():
					# 如果选中的两个rack之间已经建立了多条rack，那么就可以存在多个选择
					if wss_link_ob.bandwidth_avaliable >= vnode[pre_vnf].bandwidth_require:
						second_chose_rack.append((wss_link_id, rack_link[wss_link_id]))
						signal_link += 1
				if signal_link == 0:
					# 建立一条新的链路
					new_rack_link = creat_rack_osm_wss_link_with_id(topology, int(pre_rack), int(end_rack_id))
					if isinstance(new_rack_link, tuple):
						# 建立成功
						second_chose_rack.append((new_rack_link[0], new_rack_link[1]))
						break
					else:
						# 返回各种不同的阻塞原因
						if new_rack_link in ["noStartOutPort", "noEndInPort", "noStartInPort", "noEndOutPort", "noSameSlot"]:
							blocking_type = 'noStartSlot'
						elif new_rack_link in ['notTrans', 'notRecv']:
							blocking_type = 'noTrans'
						else:
							raise ValueError("生成链路判断错误！")
		else:
			blocking_type = "noStartHost"

	# 当没有找到合适的rack时，返回对应的blocking原因
	if not second_chose_rack:
		return blocking_type
	return second_chose_rack


class VNodePath(object):
	"""
	映射节点路径类
	"""
	
	def __init__(self, map_id, rack_id=None, vnf_id=None, next=None):
		self.id = map_id # 映射的第几个结点
		self.rack = rack_id # 映射的rack
		self.vnf = vnf_id  # 映射的vnf
		self.next = next # 映射的下一个结点


class ShortPath(object):
	"""
	记录相应的物理路径
	"""
	def __init__(self, path_id):
	
		# 链路编号 -- 第几条链路
		self.id = path_id

		# usecase4使用参数
		# 映射请求的编号 -- 方便存储整个请求
		self.request_num = None
		# 请求的长度
		self.request_len = None
		# 映射链路的第一个rack
		self.first_rack = None

		# 路径类型 -- 转接或正常类型
		self.path_type = None
		# 映射的vnf
		self.start_vnf = None
		self.end_vnf = None
		# 起始rack
		self.start_rack = None
		# 终止rack
		self.end_rack = None
		# 对应的物理网络链路
		self.rack_link = None
		# 连接的下一端口
		self.next = None


def request_mapping(topology, event, case_states):
	"""
	请求处理模块
	请求映射成功类型
	1. 正常映射 - normal
	2. case1 - case1
	3. case2 - case2
	4. case3 - case3
	5. case4 - case4
	"""
	success_type = 'normal'
	request_state = None # 请求的处理状态，True or False
	loss_type = None # 请求映射失败的原因

	vnode = event.request # 请求结点列表
	r_g_a = event.req_graph_ar # 请求关系矩阵
	vnf_num = event.vnf_num # vnf的个数
	request_num = event.request_id
	rack_links = topology.rack_link
	racks = topology.racks
	links = topology.link
	rack_num = topology.rack_num
	
	fm = PP() # 存储整个已经映射的vnf -- 字典
	fm.value = {} # {映射顺序：vnf_id}

	rack_mapped = PP() # 记录已经操作的rack
	rack_mapped.value = {}

	# 生成各种资源使用情况列表
	start_resource_rate = get_rack_resources_userate(topology)
	# return cpu_status, trans_status, recv_status, up_wss_out_port_status, down_wss_in_port_status
	
	# 每次映射可以被选择的vnf列表
	chose_vnf_list = [None  for _ in range(vnf_num)]
	# 记录每次选中的vnf列表
	chosed_vnf_list = [None for _ in range(vnf_num)]
	
	# 每次选中的物理结点
	chose_node_list = [None for _ in range(vnf_num)]
	# 第一个结点返回的rack列表
	# 其他结点返回的RackLink对象
	# 每次操作的对象
	chosed_node_list = [None for _ in range(vnf_num)]

	# 得到各种资源的权重比
	resource_state = get_resource_rate(rack_num, *start_resource_rate)
	
	sub_node_path = VNodePath(-1) # 映射结点路径
	sub_path = ShortPath(0) # 映射路径
	# 从0开始 -- 当i为0时，不用映射链路
	sub_path.request_num = event.request_id

	sub_path.request_len = vnf_num
	sub_path.path_type = 'normal'
	blocking_type = None # 阻塞
	vnfList = list(vnode.keys()) # request中包含的网络功能
	i = 0
	while i < vnf_num:
		# 开始寻找对应的链路
		
		# 第一个结点,不用映射物理路径
		if i == 0:
			# 判断不是回溯步骤
			if not chose_vnf_list[i]:
				# 判断是否先后顺序
				# 当整个没有相应的选择时,并且选中vnf的个数多于一个时
				chose_vnf_list[i] = decide_vnf(vnode, r_g_a, fm)
				chosed_vnf_list[i] = copy.deepcopy(chose_vnf_list[i])
			# 当检测到选择的结点列表为空时
			if not chosed_node_list[i]:
				# 选择相应的物理节点
				# 清除之前映射的fm
				try:
					del fm.value[i]
				except:
					pass
				try:
					del rack_mapped.value[i]
				except:
					pass
				# 当检测到没有其他可选vnf时
				if not chosed_vnf_list[i]:
					# 没有其他可选的vnf
					return blocking_type, None, None, success_type

				for vnf in chosed_vnf_list[i]:
					
					chose_node_list[i] = chose_first_node(topology, i, None, rack_mapped, vnode, fm, vnf, resource_state, *start_resource_rate)
					# 确定相应的物理链路-- 加入到链路列表中
					if isinstance(chose_node_list[i], str):
						# 没有找到相应的物理结点时
						blocking_type = chose_node_list[i]
						continue
					chosed_node_list[i] = copy.deepcopy(chose_node_list[i])
					fm.value[i] = chosed_vnf_list[i].pop(0)
					break
				# 当找不到对应的物理结点时
				if isinstance(chose_node_list[i], str):
					return blocking_type, None, None, success_type
			# 清除之前映射的路径
			sub_path.next = None
			# 建立相应的物理路径
			chose_rack = chosed_node_list[i].pop(0)
			rack_mapped.value[i] = chose_rack
			i += 1
			
		else:
			# 不是第一个结点
			# 得到前一个物理结点
			pre_rack = rack_mapped.value[i-1]

			# 没有进行初次判断时
			if not chose_vnf_list[i]:
				# 当整个没有相应的选择时,并且选中vnf的个数多于一个时
				chose_vnf_list[i] = decide_vnf(vnode, r_g_a, fm)
				chosed_vnf_list[i] = copy.deepcopy(chose_vnf_list[i])
			# 当检测到选择的结点列表为空时
			if not chosed_node_list[i]:
				# 选择相应的物理节点
				# 当检测到没有其他可选vnf时
				# 清除之前的fm
				try:
					del fm.value[i]
				except:
					pass
				try:
					del rack_mapped.value[i]
				except:
					pass
				if not chosed_vnf_list[i]:
					chose_vnf_list[i] = None
					i -= 1
					continue
				# 选择相应的物理节点
				for vnf in chosed_vnf_list[i]:
					chose_node_list[i] = chose_first_node(topology, i, pre_rack, rack_mapped, vnode, fm, vnf, resource_state, *start_resource_rate)
					# 确定相应的物理链路-- 加入到链路列表中
					if isinstance(chose_node_list[i], str):
						blocking_type = chose_node_list[i]
						continue
					chosed_node_list[i] = copy.deepcopy(chose_node_list[i])
					fm.value[i] = chosed_vnf_list[i].pop(0)
					break
				# 没有找到合适的物理结点
				if isinstance(chose_node_list[i], str):
					chose_vnf_list[i] = None
					i -= 1
					continue
			# 清除之前映射的结点
			csub_path = sub_path
			# 注意链路的映射是从1开始的
			while csub_path.next and csub_path.id < i-1:
				csub_path = csub_path.next
			csub_path.next = None
			# 处理当前映射
			# 确认当前映射的rack
			chose_rack = chosed_node_list[i].pop(0)
			rack_mapped.value[i] = chose_rack[1].end_rack.rack_num

			csub_path = sub_path
			while csub_path.next:
				csub_path = csub_path.next
			mid_path = ShortPath(i)
			mid_path.rack_link = chose_rack[0]
			mid_path.start_vnf = fm.value[i-1]
			mid_path.path_type = "normal"
			mid_path.end_vnf = fm.value[i]
			csub_path.next = mid_path
			i += 1

		# 其他节点
		# 如果映射失败，返回到上一层检查是否有其他可选节点
		# 如果所有的选择都进行到底了，则返回相应的映射失败的方案
		# 如果整个映射完成，则返回对应的sub_path
	# 取得相应的路径的第一个rack存储到对应rack中
	first_rack = rack_links[sub_path.next.rack_link].start_rack.rack_num
	# 取得相应的vnf顺序
	sorted_vnf = list(fm.value.values())
	sorted_rack = list(rack_mapped.value.values())
	service_chain = '_'.join(map(str, sorted_vnf))
	sub_path.first_rack = first_rack
	# 对应的映射方案放入到rack内部
	if not topology.racks[str(first_rack)].mapping_sc:
		topology.racks[str(first_rack)].mapping_sc = {}
	topology.racks[str(first_rack)].mapping_sc[sub_path.request_num] = (vnf_num, sorted_rack, sorted_vnf, sub_path)

	return None, sub_path, sub_node_path, success_type

def chose_vnf(r_g_a, fm):
	"""
	确定可选的vnf
	# 先确定这一部分
	# 1. 选择除可选的vnf的顺序
	"""

	# 不同顺序等级的vnf
	fi_level = r_g_a.fi_level
	se_level = r_g_a.se_level
	th_level = r_g_a.th_level
	fo_level = r_g_a.fo_level
	mid_level = r_g_a.mid_level

	vnf_chosed_list = [] # 选出的可选的vnf列表

	vnf_mapped_list = fm.value.values() # 已经映射的vnf列表 -- 排除在外

	# 检测level1
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

def decide_vnf(vnode, r_g_a, fm):
	"""
	从可选vnf list中确定相应的vnf
	# 2. 选择出需要资源最多的vnf
	"""

	cpu_rate = 0.5 # 计算资源权重占比
	bd_rate = 0.5 # 带宽权重占比

	# 找出再当前层级的vnf
	check_vnf = chose_vnf(r_g_a, fm)

	compare_list = {} # 比较队列 -- 找出占比最大的

	for vnf_id in check_vnf:
		compare_list[vnf_id] = cpu_rate * vnode[vnf_id].computer_require + bd_rate * vnode[vnf_id].bandwidth_require

	max_vnf = max(compare_list.values())

	for vnf_id in compare_list:
		if compare_list[vnf_id] == max_vnf:
			return [vnf_id]
	else:
		raise ValueError("vnf选择出错!")