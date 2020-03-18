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
from creat_link import release_rack_osm_wss_link
# 建立bypass链路
from create_switch_link import creat_rack_switch_link
from topology_wss_op import RackLink
from modify_osm_link import change_osm_link
from wss_osm_para import BVTNUM, DEGREE, WSSSLOT, CASETYPE


class PP(object):
	"""
	指针对象
	"""
	pass


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

# 所有仿真通用的
def create_max_array(topology, vnode, vnf_num):
	"""
	构建最大带宽关系矩阵
	每个节点对应着各种vnf的最大带宽矩阵
	# 2019/8/24新思路
	# 这个函数只进行对应的已建链路的最大带宽的判断--不进行具体资源大小的判断
	# 不进行链路的新建，只进行链路带宽和的计算

	:param topology: 整个仿真系统的topo对象
	:param vnode: {vnode_num: } # vnf结点字典
	:param vnf_num: vnf的个数
	"""
	# racks = topology.racks
	# rack_num = topology.rack_num
	# osm_links = topology.link
	rack_links = topology.rack_link
	# index_link = topology.index_link

	not_use_link_list = []
	for not_use_link in rack_links:
		if rack_links[not_use_link].start_wss_link.bandwidth_avaliable==rack_links[not_use_link].start_wss_link.bandwidth:
			not_use_link_list.append(not_use_link)
	for not_use_link in not_use_link_list:
		release_rack_osm_wss_link(topology, not_use_link)

	racks = topology.racks
	rack_num = topology.rack_num
	osm_links = topology.link
	rack_links = topology.rack_link
	index_link = topology.index_link

	# max_mat = [[0 for i in range(vnf_num)] for _ in range(rack_num)]
	max_mat = [None for _ in range(rack_num)]

	# 针对每个rack, rack的编号是从1开始的
	for in_rack in range(1, rack_num+1):
		# 针对每个vnf
		counter = 0
		mid_max = {} # 记录每个vnf对应的最大的带宽
		for j in vnode.keys():
			max_bandwidth = 0 # 得到最大的带宽值
			for out_rack in index_link[in_rack-1]:
				# 注意对应的out rack的编号需要加1
				osm_link = osm_links[str(in_rack)][out_rack-1]
				# 检测到rack之间存在链路
				if osm_link != "None":
					# 检测到还没建立任何光路，建立初始链路
					if not osm_link.wss_link:
						# 建立新的链路
						creat_state = creat_rack_osm_wss_link(topology, in_rack, out_rack)
						max_bandwidth = creat_state.start_wss_link.bandwidth_avaliable + \
						(DEGREE*WSSSLOT//4 - sum(creat_state.start_rack.up_wss.out_port_usenum.values()))*\
						creat_state.start_wss_link.bandwidth
						# 直接跳过
						continue
					# 遍历两结点之间已经建立的链路
					for wss_ports, wss_link in osm_link.wss_link.items():
						# 找到对应的终结点
						# 去除之前资源限制的判断 -- 2019/8/24
						wss_ports_start_rack = wss_ports.split('_')[0]
						start_rack = racks[wss_ports_start_rack]
						# 最大带宽考虑其余端口的使用情况
						mid_max_bandwidth = wss_link.bandwidth_avaliable + \
						(DEGREE*WSSSLOT//4 - sum(start_rack.up_wss.out_port_usenum.values()))*wss_link.bandwidth
						if mid_max_bandwidth > max_bandwidth:
							max_bandwidth = mid_max_bandwidth
			mid_max[j] = max_bandwidth
		max_mat[in_rack-1] = mid_max
	return max_mat


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


def vnss(r_g_a, topology, vnode, max_mat,fm, check_vnf, on, pre_rack):
	"""
	有多个vnf可选时判断vnf之间的顺序
	:param on: 当前映射顺序
	:param pre_rack: 前一个选择的rack编号
	"""
	rack_num = topology.rack_num
	index_links = topology.index_link
	rack_links = topology.rack_link
	vnode_ids = list(vnode.keys())
	
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
					mid_sum += max_mat[rack-1][vnf]
				if mid_max < mid_sum:
					mid_max = mid_sum
			mid_sum_max_band[vnf_id] = mid_max
		
		#确定顺序
		max_band = max(mid_sum_max_band.values())
		for vnf in mid_sum_max_band:
			if mid_sum_max_band[vnf]  ==  max_band:
				max_vnf.append(vnf)
		
		#多个相同的vnf，选择具有最大带宽需求的优先
		max_band_list = [vnode[i].bandwidth_require for i in max_vnf]
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
					mid_sum += max_mat[rack-1][vnf]
				if mid_max < mid_sum:
					mid_max = mid_sum
			mid_sum_max_band[vnf_id] = mid_max
			
		#确定顺序
		max_band = max(mid_sum_max_band.values())
		for vnf in mid_sum_max_band:
			if mid_sum_max_band[vnf]  ==  max_band:
				max_vnf.append(vnf)
		
		#多个相同的vnf，选择具有最大带宽需求的优先
		max_band_list = [vnode[i].bandwidth_require for i in max_vnf]
		max_band = max(max_band_list)
		for i in range(len(max_vnf)):
			if max_band_list[i] == max_band:
				chosed_vnf.append(max_vnf[i])
				
	return chosed_vnf


def enss(r_g_a, topology, vnode, max_mat,fm, vnf_id, on, pre_rack, rack_mapped):
	"""
	确定某个vnf可以映射的物理结点
	第一个结点时只是确定第一个rack
	后面再来确认对应的host和RackLink
	:param on: 当前映射顺序
	:param pre_rack: 前一个选择的rack编号
	"""
	rack_num = topology.rack_num
	osm_link = topology.link
	racks = topology.racks
	index_links = topology.index_link
	rack_links = topology.rack_link

	vnode_ids = list(vnode.keys()) # 记录着每个vnf所在的index
	vnf_num = len(vnode)
	mid_sum_max_band = {} # 记录多个不同vnf的最大带宽和, rack: max_band
	max_vnf = [] # 记录最大的vnfs
	# 选中的结点
	chosed_node = []
	# 确认可操作vnf
	check_vnf = get_vnf(r_g_a,fm.value.values())
	blocking_type = None
	
	# 检测是否是第一个节点
	if not fm.value.values():
		# 第一个节点
		next_vnfs = get_next_vnf(r_g_a, vnf_id, check_vnf)
		# 选择串口连接数最小的
		first_chosed_using_port_num = {}
		for first_chosed_rack in racks:
			first_chosed_using_port_num[first_chosed_rack] = sum([i for i in racks[first_chosed_rack].up_wss.out_port_usenum.values()])
		min_first_chosed_using_port_num = min(first_chosed_using_port_num.values())
		for min_rack in first_chosed_using_port_num:
			if first_chosed_using_port_num[min_rack] == min_first_chosed_using_port_num:
				chosed_node.append(int(min_rack))
		# mid_max = 0
		# for rack in range(rack_num):
		# 	mid_sum = 0
		# 	# 先找出具有最大带宽的rack
		# 	for vnf in next_vnfs:
		# 		mid_sum += max_mat[rack][vnf]
		# 	mid_sum_max_band[rack+1] = mid_sum
		# # 得到最大的带宽
		# max_band = max(mid_sum_max_band.values())
		# # 取得有最大带宽的rack的列表
		# max_band_rack = [i for i in mid_sum_max_band if mid_sum_max_band[i] == max_band]
		# 筛选出满足计算资源的rack
		# for rack_id in max_band_rack:
		# 	# 检测是否符合带宽要求
		# 	for rack_link in osm_link[str(rack_id)]:
		# 		if rack_link != 'None':
		# 			# TODO
		# 			for wss_link in rack_link.wss_link:
		# 				if racks[str(rack_id)].avaliable_resource >= vnode[vnf_id].computer_require:
		# 					if rack_link.wss_link[wss_link].bandwidth_avaliable >= vnode[vnf_id].bandwidth_require:
		# 						chosed_node.append(rack_id)
		# 					else:
		# 						start_up_wss = racks[str(rack_id)].up_wss
		# 						end_down_wss = racks[str(rack_id)].down_wss
		# 						start_rack = racks[str(rack_id)]
		# 						# 检测是否有bvt剩余
		# 						# start_rack
		# 						if start_rack.trans_list.keys() == start_rack.trans_using.keys():
		# 							blocking_type = "noTrans"
		# 						else:
		# 							blocking_type = "other"
		# 				else:
		# 					blocking_type = 'noStartHost'
	else:
		rack_mapped_list = list(rack_mapped.value.values())
		pre_vnf = fm.value[on-1]
		# 不是第一个结点需要考虑链路的选择
		next_vnfs = get_next_vnf(r_g_a, vnf_id, check_vnf)
		mid_rack_sum_band = []
		mid_max = 0
		for rack in index_links[pre_rack-1]:
			mid_sum = 0
			# 防止同一条链产生回路
			if rack not in rack_mapped_list:
				# 先找出具有最大带宽的rack
				for vnf in next_vnfs:
					mid_sum += max_mat[rack-1][vnf]
				mid_sum_max_band[rack] = mid_sum
		# 得到最大的带宽
		max_band = max(mid_sum_max_band.values())
		# 取得有最大带宽的rack的列表
		# 此处取得的最大带宽可能已经不存在了 -- case处理过程中被释放掉了
		max_band_rack = [i for i in mid_sum_max_band if mid_sum_max_band[i] == max_band]
		# 存在这样的链路
		# 对应着有最大的带宽，但是没有对应的链路建立
		if not max_band_rack:
			raise ValueError("出现没有最大的带宽和的情况")
		for rack_id in max_band_rack:
			mid_link = osm_link[str(pre_rack)][rack_id-1]
			# 注意此处可能出现没有对应wsslink的情况
			# 重新添加一条链路
			# if not mid_link.wss_link:
			# 	creat_rack_osm_wss_link(topology, pre_rack, rack_id)
			for wss_link in mid_link.wss_link:
				# 确认是否是对应的的rack链路
				mid_id_list = wss_link.split('_')
				if int(mid_id_list[0]) == pre_rack and int(mid_id_list[1]) == rack_id:
					mid_rack_link = rack_links[wss_link]
					if mid_rack_link.start_rack.avaliable_resource >= vnode[pre_vnf].computer_require:
						if mid_rack_link.end_rack.avaliable_resource >= vnode[vnf_id].computer_require:
							if mid_rack_link.start_wss_link.bandwidth_avaliable >= vnode[pre_vnf].bandwidth_require:
									chosed_node.append((wss_link, mid_rack_link))
							else:
								# 检测实际阻塞原因
								# 检测slot是否还有剩余
								# start_rack
								start_up_wss = racks[str(mid_rack_link.start_rack.rack_num)].up_wss
								end_down_wss = racks[str(mid_rack_link.end_rack.rack_num)].down_wss

								# 找出对应的与osm连接的wss端口
								start_wss_link = mid_rack_link.start_wss_link
								end_wss_link = mid_rack_link.end_wss_link

								up_wss_out_port = start_wss_link.out_port
								down_wss_in_port = end_wss_link.in_port

								start_rack = racks[str(mid_rack_link.start_rack.rack_num)]
								end_rack = racks[str(mid_rack_link.end_rack.rack_num)]
								# 检测是否有bvt剩余
								# start_rack
								if len(start_rack.trans_list) == len(start_rack.trans_using):
									blocking_type = "noTrans"
								elif len(up_wss_out_port.slot_use) == len(up_wss_out_port.slot_plan):
									blocking_type = "noStartSlot"
								# end_rack
								elif len(down_wss_in_port.slot_use) == len(down_wss_in_port.slot_plan):
									blocking_type = "noEndSlot"
								elif len(end_rack.recv_list) == len(end_rack.recv_using):
									blocking_type = "noRecv"
								else:
									# TODO 注意会出现这种情况，目前还没有找到原因
									# 由于已建立链路不能满足对应的需求
									# 导致出现这种情况
									# 处理方法
									# 1. 建立一条新的链路来满足
									# 2. 直接判定为失效
									blocking_type = "other"
								# blocking_type = "noBvt"
						else:
							blocking_type = "noEndHost"
					else:
						blocking_type = "noStartHost"
		if (blocking_type=="other" or blocking_type is None) and not chosed_node:
			# 两种情况
			# 1. 已建立链路没法满足对应的带宽需求
			# 2. 对应选择出的最大带宽的rack链路被释放掉了--case处理时
			# 尝试构建一种新的策略 -- 在此处判断一下
			# 由于所有对应的链路都没有相应的链路建立
			# 尝试建立一条新的链路
			# 这条新建的链路一定会被使用
			# 由于最大带宽的结点没有满足资源需求（其中有max-mat中的被释放了）
			# 方案一
			# 1. 先找出用的最少的端口
			# 2. 再判断对应的rack的链路是否满足对应的带宽需求
			# 3. 如果没有满足的则判断是否可以建立新的链路
			# 方案二 - 采用
			# 直接通过上面找到的最大的结点（被释放的）建立新的链路
			# 当所有的存在链路都不满足时，建立一条新的链路

			link_pre_rack = list(mid_sum_max_band.keys())
			# 直接判断所有对应可选rack中对应的端口数用的是最少的
			chosed_used_num_dict = {}
			for m_rack in link_pre_rack:
				chosed_used_num_dict[m_rack] = len(osm_link[str(pre_rack)][m_rack-1].start_port.physic_port.wss_port.slot_use)
			# 进行排序--根据对应slot_use
			sorted_chosed_rack = sorted(chosed_used_num_dict, key=lambda x: chosed_used_num_dict[x])
			chosed_new_create_link_object = None
			for mm_rack in sorted_chosed_rack:
				# 判断对应的结点的带宽资源是否满足
				if racks[str(mm_rack)].avaliable_resource >= vnode[vnf_id].computer_require:
					mm_osm_link = osm_link[str(pre_rack)][mm_rack-1]
					# 判断负载均衡是否符合
					normalLinkLength = len(mm_osm_link.wss_link) if mm_osm_link.wss_link else 0
					# 中转链长度 - 不占用发射机
					midLinkLength = len(mm_osm_link.mid_link) if mm_osm_link.mid_link else 0
					# bypass链长度
					bypassLinkLength = len(mm_osm_link.wss_switch_link) if mm_osm_link.wss_switch_link else 0
					# 注意判断条件（边界条件）
					# 20200217的更新
					balance_bvt = BVTNUM//DEGREE
					load_balance_bvt = balance_bvt if BVTNUM/DEGREE<=balance_bvt else balance_bvt+1
					###
					if (normalLinkLength + bypassLinkLength) < WSSSLOT//4:
						chosed_new_create_link_object = creat_rack_osm_wss_link(topology, pre_rack, mm_rack)
						if isinstance(chosed_new_create_link_object, str):
							if chosed_new_create_link_object in ["noStartOutPort","noStartInPort", "noSameSlot"]:
								blocking_type = "noStartSlot"
							elif chosed_new_create_link_object in ["noEndInPort", "noEndOutPort"]:
								blocking_type = "noEndSlot"
							elif chosed_new_create_link_object == 'notTrans':
								blocking_type = "noTrans"
							elif chosed_new_create_link_object == 'notRecv':
								blocking_type = "noRecv"
						else:
							chosed_new_create_link_id = f'{pre_rack}_{mm_rack}_{chosed_new_create_link_object.start_wss_link.in_port.port_num}_{chosed_new_create_link_object.start_wss_link.out_port.port_num}_{chosed_new_create_link_object.slot_plan}'

							chosed_node.append((chosed_new_create_link_id, chosed_new_create_link_object))
							break
					else:
						blocking_type = "noStartSlot"
				else:
					blocking_type = "noEndHost"
			else:
				blocking_type = "noStartSlot"

	if not chosed_node:
		# if on == vnf_num-1:
		# 	case1(topology, pre_rack, vnode, fm, rack_mapped, on)
		return blocking_type

	if len(chosed_node) > 1 and isinstance(chosed_node[0], tuple):
		# 从非第一结点开始选择
		# 判断优先使用连接端口使用最少的
		key_id = ['_'.join(key[0].split('_')[:2]) for key in chosed_node]
		key_id = set(key_id)

		port_use_num = {} # 记录对应端口使用的次数
		# 统计选中的rack与pre_rack的端口使用次数
		for key in key_id:
			start_rack_id, end_rack_id = map(int, key.split('_'))
			port_use_num[key] = len(osm_link[str(start_rack_id)][end_rack_id-1].start_port.physic_port.wss_port.slot_use)
		# 如果所有的使用次数都一样，优先使用大rack号的rack
		# 否则选用使用端口次数小的那一端
		min_use_num = min(port_use_num.values())
		chose_min_port = [key for key in port_use_num if port_use_num[key] == min_use_num]

		# 根据rack编号-- 从大到小进行编号
		chose_min_port = sorted(chose_min_port, key=lambda x: int(x.split('_')[1]), reverse=True)

		# 从已选结点中根据上面那个进行排序
		new_chosed_node = []

		# 根据start_endrack进行分类
		node_type = {}
		for node in chosed_node:
			rack_type = '_'.join(node[0].split('_')[:2])
			if rack_type not in node_type:
				node_type[rack_type] = []
			node_type[rack_type].append(node)

		for rack_com in chose_min_port:
			new_chosed_node.extend(node_type[rack_com])
		chosed_node = new_chosed_node

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
def cacl_port_use_num(topology, pre_rack_num, end_rack_num):
	"""
	计算某个rack的某个端口的使用总数
	"""
	osm_link = topology.link
	target_osm_link = osm_link[str(pre_rack_num)][int(end_rack_num)-1]
	# 计算对应的start端口的使用次数
	return target_osm_link.start_port.physic_port.wss_port.slot_num

def case3(topology, pre_rack, vnode, fm, rack_mapped, on):
	"""
	链路usecase3

	当找不到最后一条链路时，且对应的usecase2
	不可用时，建立bypass路径
	"""

	# 清除之前的vnf和rack
	if on in fm.value:
		del fm.value[on]
	if on in rack_mapped.value:
		del rack_mapped.value[on]

	# 找到还未映射的vnf
	vnfs = list(vnode.keys())
	mapped_vnfs = list(fm.value.values())
	chose_vnf = None # 将要操作的对象
	for vnf in vnfs:
		if vnf not in mapped_vnfs:
			chose_vnf = vnf
			break

	# 取得对应的物理参数
	index_rack = topology.index_link # 各个rack的连接矩阵
	racks = topology.racks

	# 确定pre_rack连接的rack
	avaliable_racks = [] # mid rack集合
	used_racks = list(rack_mapped.value.values()) # 前面已经使用的rack不可再次使用
	for rack in index_rack[pre_rack-1]:
		if rack not in used_racks:
			avaliable_racks.append(rack)
	if not avaliable_racks:
		return False, None, 'noRacks'

	# 确定对应的end rack
	# 计算端口的使用次数
	# 优先判断端口数最小的rack -- 出端使用次数最小的端口
	mid_rack_port_use_num = []
	for rack in avaliable_racks:
		port_uses = cacl_port_use_num(topology, pre_rack, rack)
		mid_rack_port_use_num.append([rack, port_uses])
	mid_rack_port_use_num = sorted(mid_rack_port_use_num, key=lambda x:x[1])
	avaliable_racks = [rack[0] for rack in mid_rack_port_use_num]

	end_racks = {rack:[] for rack in avaliable_racks}

	for rack in avaliable_racks:
		for in_rack in index_rack[rack-1]:
			if in_rack not in used_racks:
				end_racks[rack].append(in_rack)

	# 最后一个vnf需要的计算资源
	require_cpu = vnode[chose_vnf].computer_require
	rack_link = 'noRacks'
	for mid_rack, rack in end_racks.items():
		mid_rack_port_use_num = []
		for mrack in rack:
			port_uses = cacl_port_use_num(topology, mid_rack, mrack)
			mid_rack_port_use_num.append([mrack, port_uses])
		mid_rack_port_use_num = sorted(mid_rack_port_use_num, key=lambda x:x[1])
		rack = [mrack[0] for mrack in mid_rack_port_use_num]
		for in_rack in rack:
			if racks[str(in_rack)].avaliable_resource >= require_cpu:
				rack_link = creat_rack_switch_link(topology, pre_rack, mid_rack, in_rack)
				if not isinstance(rack_link, str):
					# 创建成功相应的链路
					fm.value[on] = chose_vnf
					# 确定rack link的相关id参数
					start_wss_in_port = rack_link.start_wss_link.in_port.port_num
					start_wss_out_port = rack_link.start_wss_link.out_port.port_num
					start_wss_slot_plan = rack_link.slot_plan
					return True, f'{pre_rack}_{mid_rack}_{in_rack}_{start_wss_in_port}_{start_wss_out_port}_{start_wss_slot_plan}', True
	else:
		return False, None, rack_link

def case1(topology, pre_rack, vnode, fm, rack_mapped, on):
	"""
	case1 执行
	切换osm的连接
	"""
	# 清除之前的vnf和rack
	if on in fm.value:
		del fm.value[on]
	if on in rack_mapped.value:
		del rack_mapped.value[on]

	# 找到还未映射的vnf
	vnfs = list(vnode.keys())
	mapped_vnfs = list(fm.value.values())
	chose_vnf = None # 将要操作的对象
	for vnf in vnfs:
		if vnf not in mapped_vnfs:
			chose_vnf = vnf
			break
	# 最后一个vnf需要的计算资源
	require_cpu = vnode[chose_vnf].computer_require

	# 确定pre_rack连接的rack
	avaliable_racks = [] # mid rack集合
	used_racks = list(rack_mapped.value.values()) # 前面已经使用的rack不可再次使用
	for rack in topology.index_link[pre_rack-1]:
		if rack not in used_racks:
			avaliable_racks.append(rack)
	rack_link = 'noRacks'
	for rack in avaliable_racks:
		# 取得新的rack
		new_end_rack = change_osm_link(topology, pre_rack, rack, used_racks, require_cpu)
		if not isinstance(new_end_rack, str):
			# 直接创建一条新的链路返回
			rack_link = creat_rack_osm_wss_link(topology, pre_rack, new_end_rack)
			if isinstance(rack_link, type(RackLink)):
				# 找到对应的新链返回
				fm.value[on] = chose_vnf
				upwssinport = rack_link.start_wss_link.in_port.port_num
				upwssoutport = rack_link.start_wss_link.out_port.port_num
				slotplan = rack_link.slot_plan
				return True, f'{pre_rack}_{new_end_rack}_{upwssinport}_{upwssoutport}_{slotplan}', True
	else:
		return False, None, rack_link

def case2(topology, pre_rack, vnode, fm, rack_mapped, on):
	"""
	执行case1
	切换对应的wss的链接
	"""
	# 找到还没有映射的vnf
	# 清除之前未映射成功的vnf和相应的rack
	# 如果没找到要还原此步
	if on in fm.value:
		del fm.value[on]
	if on in rack_mapped.value:
		del rack_mapped.value[on]

	vnfs = list(vnode.keys())
	mapped_vnfs = list(fm.value.values()) # 已经映射的vnf
	chose_vnf = None # 确定对应的vnf的对象
	for vnf in vnfs:
		if vnf not in mapped_vnfs:
			chose_vnf = vnf
			break
	index_rack = topology.index_link # 各个rack连接矩阵
	racks = topology.racks # 对应的rack
	# 确定pre_rack连接的rack
	avaliable_racks = []
	used_racks = list(rack_mapped.value.values()) # 前面几个vnf已经使用了的rack -- 不可再次使用
	for rack in index_rack[pre_rack-1]:
		if rack not in used_racks:
			avaliable_racks.append(rack)

	# if not avaliable_racks:
	# 	# 没有可用的rack
	# 	if fm_value:
	# 		fm.value[on] = fm_value
	# 	if rack_mapped_value:
	# 		rack_mapped.value[on] = rack_mapped_value
	# 	return False, None, 'noRacks'

	# 最后一个vnf对象
	require_cpu = vnode[chose_vnf].computer_require
	# 测试
	rack_link = 'noRacks'
	for rack in avaliable_racks:
		# if racks[str(rack)].avaliable_resource >= require_cpu:
		rack_link = creat_rack_osm_wss_link(topology, pre_rack, rack)
		if isinstance(rack_link, type(RackLink)):
			# 找到了合适的链路，返回链路对象
			# 对应链路的参数
			fm.value[on] = chose_vnf
			startrack = rack_link.start_rack.rack_num
			endrack = rack_link.end_rack.rack_num
			upwssinport = rack_link.start_wss_link.in_port.port_num
			upwssoutport = rack_link.start_wss_link.out_port.port_num
			slotplan = rack_link.slot_plan
			return True, f'{startrack}_{endrack}_{upwssinport}_{upwssoutport}_{slotplan}', True
	
	return False, None, rack_link

def get_link_blocking_type(case_num, case, blocking_value):
	"""
	统计对应的case中阻塞的类型的次数
	"""

	if blocking_value == 'noStartOutPort' or blocking_value == 'noStartInPort':
		case[case_num][0] += 1
		# case.noStartPort+= 1
	elif blocking_value == 'noEndInPort' or blocking_value == 'noEndOutPort':
		case[case_num][1] += 1
		# case.noEndPort += 1
	elif blocking_value == 'notTrans':
		case[case_num][2] += 1
		# case.noTrans += 1
	elif blocking_value == 'notRecv':
		case[case_num][3] += 1
		# case.noRecv += 1
	elif blocking_value == 'noSameSlot':
		case[case_num][4] += 1
		# case.noSameSlot += 1
	elif blocking_value == 'noRacks':
		case[case_num][5] += 1
	return case

	
def request_mapping(topology, event, case_states):
	"""
	请求处理模块
	请求映射成功类型
	1. 正常映射 - normal
	2. case1 - case1
	3. case2 - case2
	4. case3 - case3
	5. case4 - case4
	:param case_states: 统计case的情况
	"""

	# 两种资源变换
	# 1. wss端口变换
	# 2. slot的变换

	# 创建统计case不可行原因数组
	# case_test = [[0 for i in range(6)] for i in range(4)]
	case_test = case_states.test

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
	
	fm = PP() # 存储整个已经映射的vnf -- 字典
	fm.value = {} # {映射顺序：vnf_id}

	rack_mapped = PP() # 记录已经操作的rack
	rack_mapped.value = {}
	
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

	max_mat = create_max_array(topology, vnode, vnf_num) # 最大带宽矩阵
	
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
				# 找出需要判断关系的vnf
				check_vnf = get_vnf(r_g_a,fm.value.values())
				# 判断是否先后顺序
				# 当整个没有相应的选择时,并且选中vnf的个数多于一个时
				if len(check_vnf) > 1:
					chose_vnf_list[i] = vnss(r_g_a, topology, vnode, max_mat,fm, check_vnf, i, None)
					chosed_vnf_list[i] = copy.deepcopy(chose_vnf_list[i])
				else:
					# 当只有一个vnf可选时
					chose_vnf_list[i] = check_vnf
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
					return blocking_type, sub_path, None, success_type, topology

				for vnf in chosed_vnf_list[i]:
					
					chose_node_list[i] = enss(r_g_a, topology, vnode, max_mat, fm, vnf,i,None, None)
					# 更新rack_links -- 每次建立了新的连接
					rack_links = topology.rack_link
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
					return blocking_type, sub_path, None, success_type, topology
			# 清除之前映射的路径
			sub_path.next = None
			# 建立相应的物理路径
			chose_rack = chosed_node_list[i].pop(0)
			rack_mapped.value[i] = chose_rack
			# 检测是否使用usecase4
			# sub_path -- 中存了
			# sub_path.request_num = event.request_id
			# sub_path.request_len = vnf_num
			# (vnf_num, sorted_rack, sorted_vnf, sub_path) -- requestPath中存储的数据
			# 取得相应的路径的第一个rack存储到对应rack中
			# first_rack = rack_links[sub_path.next.rack_link].start_rack.rack_num
			# # 取得相应的vnf顺序
			# sorted_vnf = list(fm.value.values())
			# sorted_rack = list(rack_mapped.value.values())
			# sub_path.first_rack = first_rack
			# topology.racks[str(first_rack)].mapping_sc[sub_path.request_num] = (vnf_num, sorted_rack, sorted_vnf, sub_path)
			if topology.racks[str(chose_rack)].mapping_sc and CASETYPE=="case4":
				# 只有当存在着映射链路时才进行设置
				for requestNum, requestPath in topology.racks[str(chose_rack)].mapping_sc.items():
					if set(requestPath[2]) > set(vnfList) and (len(requestPath[2]) - len(vnfList)) == 1:
						# 判断不同的结点是在链路的前面还是后面
						# 判断已经存在着对应着bypass的路径不允许再次bypass
						if requestPath[3].path_type == "bypass":
							continue
						# 取出不同的结点
						diff_vnf = list(set(requestPath[2]) ^ set(vnfList))[0]
						# 判断
						diff_vnf_index = requestPath[2].index(diff_vnf)
						if diff_vnf_index == 0:
							# 前面，直接使用后面的链路 -- 如果资源足够
							# 检测对应的资源是否足够
							pre_sub_path = requestPath[3]
							cpre_sub_path = pre_sub_path.next.next
							check_state = True # 检测是否可用的状态
							while cpre_sub_path:
								mid_rack_link = rack_links[cpre_sub_path.rack_link]
								start_vnf = cpre_sub_path.start_vnf
								start_rack_num = mid_rack_link.start_rack.rack_num
								wss_link_id = cpre_sub_path.rack_link
								if not cpre_sub_path.next:
									# 判断是路径尾部
									# 判断资源是否满足再次的映射
									end_vnf = cpre_sub_path.end_vnf
									end_rack_num = mid_rack_link.end_rack.rack_num
									if racks[str(start_rack_num)].avaliable_resource < vnode[start_vnf].computer_require:
										check_state = False
										break
									if racks[str(end_rack_num)].avaliable_resource < vnode[end_vnf].computer_require:
										check_state = False
										break
									if rack_links[wss_link_id].start_wss_link.bandwidth_avaliable < vnode[start_vnf].bandwidth_require:
										check_state = False
										break
								else:
									# 不是路径尾部
									# 判断资源是否满足再次的满足
									# 测试
									if racks[str(start_rack_num)].avaliable_resource < vnode[start_vnf].computer_require:
										check_state = False
										break
									if rack_links[wss_link_id].start_wss_link.bandwidth_avaliable < vnode[start_vnf].bandwidth_require:
										check_state = False
										break
								cpre_sub_path = cpre_sub_path.next
							if check_state:
								# 找到满足条件的
								sub_path.first_rack = requestPath[2][1]
								sub_path.next = requestPath[3].next.next
								if not topology.racks[str(sub_path.first_rack)].mapping_sc:
									topology.racks[str(sub_path.first_rack)].mapping_sc = {}
								topology.racks[str(sub_path.first_rack)].mapping_sc[sub_path.request_num] = (requestPath[0]-1, requestPath[1][1:], requestPath[2][1:], sub_path)
								return None, sub_path, sub_node_path,'case_repeat', topology
						elif diff_vnf_index == len(requestPath[2])-1:
							# 后面，直接使用前面的链路 -- 如果资源足够
							pre_sub_path = requestPath[3]
							cpre_sub_path = pre_sub_path.next
							check_state = True # 检测是否可用的状态
							while cpre_sub_path.next:
								mid_rack_link = rack_links[cpre_sub_path.rack_link]
								start_vnf = cpre_sub_path.start_vnf
								start_rack_num = mid_rack_link.start_rack.rack_num
								wss_link_id = cpre_sub_path.rack_link
								if not cpre_sub_path.next.next:
									# 判断是路径尾部
									# 判断资源是否满足再次的映射
									end_vnf = cpre_sub_path.end_vnf
									end_rack_num = mid_rack_link.end_rack.rack_num
									if racks[str(start_rack_num)].avaliable_resource < vnode[start_vnf].computer_require:
										check_state = False
										break
									if racks[str(end_rack_num)].avaliable_resource < vnode[end_vnf].computer_require:
										check_state = False
										break
									if rack_links[wss_link_id].start_wss_link.bandwidth_avaliable < vnode[start_vnf].bandwidth_require:
										check_state = False
										break
								else:
									# 不是路径尾部
									# 判断资源是否满足再次的满足
									if racks[str(start_rack_num)].avaliable_resource < vnode[start_vnf].computer_require:
										check_state = False
										break
									if rack_links[wss_link_id].start_wss_link.bandwidth_avaliable < vnode[start_vnf].bandwidth_require:
										check_state = False
										break
								cpre_sub_path = cpre_sub_path.next
							if check_state:
								sub_path.first_rack = requestPath[2][0]
								csub_path = sub_path
								# 防止修改元数据
								crequest_path = copy.deepcopy(requestPath[3].next)
								# 去除最后一个结点和最后一条链路
								while crequest_path.next:
									mid_crequest_path = crequest_path.next
									crequest_path.next = None
									csub_path.next = crequest_path
									csub_path = csub_path.next
									crequest_path = mid_crequest_path
									if not crequest_path.next:
										# 排除最后一条链路
										break
								if not topology.racks[str(sub_path.first_rack)].mapping_sc:
									topology.racks[str(sub_path.first_rack)].mapping_sc = {}
								topology.racks[str(sub_path.first_rack)].mapping_sc[sub_path.request_num] = (requestPath[0]-1, requestPath[1][:-1], requestPath[2][:-1], sub_path)
								return None, sub_path, sub_node_path,'case_repeat', topology
						else:
							# 在链路的中间，建立新的bypass链路
							pre_sub_path = requestPath[3]
							cpre_sub_path = pre_sub_path.next
							check_state = True # 检测是否可用的状态
							# 判断状态是否可用
							while cpre_sub_path:
								mid_rack_link = rack_links[cpre_sub_path.rack_link]
								start_vnf = cpre_sub_path.start_vnf
								end_vnf = cpre_sub_path.end_vnf
								start_rack_num = mid_rack_link.start_rack.rack_num
								wss_link_id = cpre_sub_path.rack_link
								if not cpre_sub_path.next:
									# 判断链路的尾结点
									end_rack_num = mid_rack_link.end_rack.rack_num
									if start_vnf != diff_vnf and racks[str(start_rack_num)].avaliable_resource < vnode[start_vnf].computer_require:
										check_state = False
										break
									if racks[str(end_rack_num)].avaliable_resource < vnode[end_vnf].computer_require:
										check_state = False
										break
									if start_vnf != diff_vnf and rack_links[wss_link_id].start_wss_link.bandwidth_avaliable < vnode[start_vnf].bandwidth_require:
										check_state = False
										break
								else:
									# 不是尾节点
									if start_vnf != diff_vnf and racks[str(start_rack_num)].avaliable_resource < vnode[start_vnf].computer_require:
										check_state = False
										break
									if start_vnf != diff_vnf and end_vnf != diff_vnf and rack_links[wss_link_id].start_wss_link.bandwidth_avaliable < vnode[start_vnf].bandwidth_require:
										check_state = False
										break

								cpre_sub_path = cpre_sub_path.next
							if check_state:
								# 找到符合条件的情况
								sub_path.first_rack = requestPath[2][0]
								sub_path.path_type = 'bypass'
								sstart_rack = requestPath[1][diff_vnf_index-1]
								mid_rack = requestPath[1][diff_vnf_index]
								eend_rack = requestPath[1][diff_vnf_index+1]
								rack_string = '_'.join(map(str,[sub_path.first_rack, mid_rack, eend_rack]))

								# 判断对应的链路是否已经存在
								wss_switch_link = links[str(sstart_rack)][mid_rack-1].wss_switch_link
								check_link_id = None
								if wss_switch_link:
									# 当这样的链路存在时
									for wss_switch_link_id, wss_switch_link_object in wss_switch_link.items():
										if list(wss_switch_link_id.split('_'))[:3] == list(rack_string.split('_')):
											# 找到的链路不满足
											# 找到对应转接链路是否满足相应的转接的带宽
											if wss_switch_link_object.bandwidth_avaliable < vnode[requestPath[2][diff_vnf_index-1]].bandwidth_require:
												continue
											else:
												check_link_id = wss_switch_link_id
								if check_link_id:
									# 找到已存在的链路
									# 直接使用
									# mid_path.rack_link = chose_rack[0]
									# mid_path.start_vnf = fm.value[i-1]
									# mid_path.path_type = "normal"
									# mid_path.end_vnf = fm.value[i]
									csub_path = sub_path
									cpre_sub_path = copy.deepcopy(requestPath[3].next)

									while cpre_sub_path:
										start_rack = rack_links[cpre_sub_path.rack_link].start_rack.rack_num
										end_rack = rack_links[cpre_sub_path.rack_link].end_rack.rack_num
										if start_rack != mid_rack and end_rack != mid_rack:
											# 防止修改以后元数据丢失
											mid_cpre_sub_path = cpre_sub_path.next
											cpre_sub_path.next = None
											csub_path.next = cpre_sub_path
											csub_path = csub_path.next
											cpre_sub_path = mid_cpre_sub_path
											continue
										elif end_rack==mid_rack:
											mid_path = ShortPath(10)
											mid_path.rack_link = check_link_id
											mid_path.start_vnf = cpre_sub_path.start_vnf
											mid_path.end_vnf = cpre_sub_path.next.end_vnf
											mid_path.path_type = "bypass"
											csub_path.next = mid_path
											csub_path = csub_path.next
											# 直接跳过中间的链路
											cpre_sub_path = cpre_sub_path.next.next
									if not topology.racks[str(sub_path.first_rack)].mapping_sc:
										topology.racks[str(sub_path.first_rack)].mapping_sc = {}
									mapped_rack = requestPath[1][:diff_vnf_index] + requestPath[1][diff_vnf_index+1:]
									mapped_vnf = requestPath[2][:diff_vnf_index] + requestPath[2][diff_vnf+1:]
									topology.racks[str(sub_path.first_rack)].mapping_sc[sub_path.request_num] = (requestPath[0]-1, mapped_rack, mapped_vnf, sub_path)
									return None, sub_path, sub_node_path,'case4', topology

								# 判断资源是否足够
								else:
									# 没有找到 -- 尝试建立新的链路
									new_switch_link = creat_rack_switch_link(topology, sstart_rack, mid_rack, eend_rack)
									rack_links = topology.rack_link
									if not isinstance(new_switch_link, str):
										# 成功找到链路
										# 确定链路的id
										start_wss_in_port = new_switch_link.start_wss_link.in_port.port_num
										start_wss_out_port = new_switch_link.start_wss_link.out_port.port_num
										start_wss_slot_plan = new_switch_link.slot_plan
										new_switch_link_id = f'{sstart_rack}_{mid_rack}_{eend_rack}_{start_wss_in_port}_{start_wss_out_port}_{start_wss_slot_plan}'
										# 将新建链路加入到path中
										csub_path = sub_path
										cpre_sub_path = copy.deepcopy(requestPath[3].next)

										while cpre_sub_path:
											start_rack = rack_links[cpre_sub_path.rack_link].start_rack.rack_num
											end_rack = rack_links[cpre_sub_path.rack_link].end_rack.rack_num
											if start_rack != mid_rack and end_rack != mid_rack:
												mid_cpre_sub_path = cpre_sub_path.next
												cpre_sub_path.next = None
												csub_path.next = cpre_sub_path
												csub_path = csub_path.next
												cpre_sub_path = mid_cpre_sub_path
												continue
											elif end_rack==mid_rack:
												mid_path = ShortPath(10)
												# 注意rack_link中存的是链路的id
												mid_path.rack_link = new_switch_link_id
												mid_path.start_vnf = cpre_sub_path.start_vnf
												mid_path.end_vnf = cpre_sub_path.next.end_vnf
												mid_path.path_type = "bypass"
												csub_path.next = mid_path
												csub_path = csub_path.next
												# 直接跳过中间的链路
												cpre_sub_path = cpre_sub_path.next.next
										if not topology.racks[str(sub_path.first_rack)].mapping_sc:
											topology.racks[str(sub_path.first_rack)].mapping_sc = {}
										mapped_rack = requestPath[1][:diff_vnf_index] + requestPath[1][diff_vnf_index+1:]
										mapped_vnf = requestPath[2][:diff_vnf_index] + requestPath[2][diff_vnf+1:]
										topology.racks[str(sub_path.first_rack)].mapping_sc[sub_path.request_num] = (requestPath[0]-1, mapped_rack, mapped_vnf, sub_path)
										return None, sub_path, sub_node_path,'case4', topology
									else:
										case_test = get_link_blocking_type(3, case_test, new_switch_link)
			i += 1
			
		else:
			# 不是第一个结点
			# 得到前一个物理结点
			pre_rack = rack_mapped.value[i-1]

			# 没有进行初次判断时
			if not chose_vnf_list[i]:
				# 判断是否先后顺序
				check_vnf = get_vnf(r_g_a,fm.value.values())
				# 当整个没有相应的选择时,并且选中vnf的个数多于一个时
				if len(check_vnf) > 1:
					chose_vnf_list[i] = vnss(r_g_a, topology, vnode, max_mat,fm, check_vnf, i, pre_rack)
					chosed_vnf_list[i] = copy.deepcopy(chose_vnf_list[i])
				else:
					chose_vnf_list[i] = check_vnf
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
					chose_node_list[i] = enss(r_g_a, topology, vnode, max_mat, fm, vnf,i,pre_rack, rack_mapped)
					rack_links = topology.rack_link
					# 确定相应的物理链路-- 加入到链路列表中
					if isinstance(chose_node_list[i], str):
						blocking_type = chose_node_list[i]
						continue
					chosed_node_list[i] = copy.deepcopy(chose_node_list[i])
					fm.value[i] = chosed_vnf_list[i].pop(0)
					break
				# 没有找到合适的物理结点
				if isinstance(chose_node_list[i], str):
					if i == (vnf_num - 1):
						# 如果是最后一条链路，采用case
						# 判断case之前判断是否释放对应的没有使用到的链路
						csub_path = sub_path.next
						using_link_list = []
						while csub_path:
							# 找出对应的已经找到的使用链路
							using_link_list.append(csub_path.rack_link)
							csub_path = csub_path.next
						# 排除前面已经预选出的链路 -- 存储在checked_node_list中
						# 解决已开新的链路而没有使用-导致链路没有使用
						# 1. 查找对应已经安排链路
						# 2. 找到再chosed_node_list中存储的链路
						# 3. 其他的链路（没有被使用的)直接释放掉
						# 排除第一步选择结点

						for check_chose_node_list_node_index in range(1,len(chosed_node_list)):
							if isinstance(chosed_node_list[check_chose_node_list_node_index], list):
								using_link_list.extend([i[0] for i in chosed_node_list[check_chose_node_list_node_index]])
						# 找到未使用的链路并释放
						not_use_link_list = []
						for not_use_link in rack_links:
							if rack_links[not_use_link].start_wss_link.bandwidth_avaliable==rack_links[not_use_link].start_wss_link.bandwidth:
								if not_use_link not in using_link_list:
									not_use_link_list.append(not_use_link)
						for not_use_link in not_use_link_list:
							release_rack_osm_wss_link(topology, not_use_link)
						rack_links = topology.rack_link
						# case1
						# 确定pre_rack
						# 确定vnf
						states = False
						while CASETYPE=="case3":
							cTopology = copy.deepcopy(topology)
							# states, linked, block_type = case2(topology, pre_rack, vnode, fm, rack_mapped, i)
							# if states:
							# 	rack_links = topology.rack_link
							# 	success_type = "case2"
							# 	mid_path_type = "normal"
							# 	break
							# case_test = get_link_blocking_type(1, case_test, block_type)
							states, linked, block_type = case3(topology, pre_rack, vnode, fm, rack_mapped, i)
							if states:
								rack_links = topology.rack_link
								sub_path.path_type = "bypass"
								success_type = "case3"
								mid_path_type = "bypass"
								break
							case_test = get_link_blocking_type(2, case_test, block_type)
							# states, linked, block_type = case1(topology, pre_rack, vnode, fm, rack_mapped, i)
							# if states:
							# 	rack_links = topology.rack_link
							# 	success_type = "case1"
							# 	mid_path_type = "normal"
							# 	break
							# case_test = get_link_blocking_type(0, case_test, block_type)
							# 映射失败，整个状态恢复
							del topology
							topology = cTopology
							rack_links = topology.rack_link
							mid_path_type = None
							break

						if states:
							# 清除之前映射的结点
							csub_path = sub_path
							# 注意链路的映射是从1开始的
							while csub_path.next and csub_path.id < i-1:
								csub_path = csub_path.next
							csub_path.next = None
							# 将找到的新链路加入到sub_path中
							csub_path = sub_path
							while csub_path.next:
								csub_path = csub_path.next
							mid_path = ShortPath(i)
							# 针对rack_link只传递相应的id，不传object -- 否则会导致memoryError
							mid_path.rack_link = linked
							mid_path.start_vnf = fm.value[i-1]
							mid_path.end_vnf = fm.value[i]
							mid_path.path_type = mid_path_type
							csub_path.next = mid_path

							# 确认相应的存储参数
							sub_path.first_rack = rack_links[sub_path.next.rack_link].start_rack.rack_num
							rack_mapped.value[i] = rack_links[linked].end_rack.rack_num
							sorted_vnf = list(fm.value.values())
							sorted_rack = list(rack_mapped.value.values())
							# 对应的映射方案放入到rack内部
							if not topology.racks[str(sub_path.first_rack)].mapping_sc:
								topology.racks[str(sub_path.first_rack)].mapping_sc = {}
							topology.racks[str(sub_path.first_rack)].mapping_sc[sub_path.request_num] = (vnf_num, sorted_rack, sorted_vnf, sub_path)
							return None, sub_path, sub_node_path, success_type, topology	
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
	return None, sub_path, sub_node_path, success_type, topology