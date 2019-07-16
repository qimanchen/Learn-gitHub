#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-07-10 22:31:07
# @Author  : Qiman Chen
# @Version : $Id$

"""
修改osm的链接：
原则：
	1. 目前要修改的链路是没有被使用的
	2. 目标（修改后）端口是没有被使用的
	3. 不同rack之间只能有一个端口到另一个rack
"""


def change_osm_link(topology, start_rack_num, end_rack_num, used_rack, require_cpu):
	"""
	变动osm某条链路
	:param start_rack_num: 要修改链路的起始结点
	:param end_rack_num: 要修改链路的终结点
	:param used_rack: 前面链路已经在使用的rack -- 这些rack不能成为新的终点rack和新的输入rack
	"""
	# 需要变动的参数
	osm = topology.osm
	# 这些rack之间的关系 -- 是否存在链路
	link = topology.link
	# 记录每个rack连接有那些rack
	index_link = topology.index_link

	# 确定当前需要改变的链路是没有在使用的
	if link[str(start_rack_num)][end_rack_num-1].link_use:
		# 链路还在使用中 -- 不可改变其链接
		return 'linkUsing'

	"""
	变动osm连接的几步：
	1. 确认对应要变动的链路
		start rack，end rack
		start rack已经连接的rack（不可再次连接这些rack）
		已经连接end rack的rack (这些rack连接的目标rack也不可作为新的结点)
	2. 找到变动后的终结点
	"""
	# 确定可用rack列表
	rack_list = list(map(int, topology.racks.keys())) # 物理拓扑中所有的rack

	# 当前start rack已经连接的rack -- 不可为新的终结点
	start_rack_link_rack_list = index_link[start_rack_num-1]
	# 查看者连接当前end rack的rack
	# 找出这些rack连接的rack -- end rack除外 -- 不可用作终结点
	no_use_rack = set()
	no_use_input_rack = [] # 不可作为 end rack新的输入rack
	for rack in range(len(index_link)):
		if rack+1 == start_rack_num:
			# 跳过start rack
			continue
		if end_rack_num in index_link[rack]:
			no_use_input_rack.append(rack+1)
			no_use_rack.update(set(index_link[rack]))
	no_use_rack.update(set(start_rack_link_rack_list)) # 不能作为start rack的新的输入rack

	# 加入已经使用过的rack
	no_use_rack.update(set(used_rack))

	no_use_rack.add(start_rack_num) # 去除start rack本身
	no_use_input_rack.append(start_rack_num) # 去除start rack 本身
	no_use_input_rack.append(end_rack_num) # 去除end rack 本身

	no_use_input_rack.extend(used_rack)
	no_use_input_rack = list(set(no_use_input_rack))

	useable_new_end_rack = set(rack_list) ^ no_use_rack # 可用start rack输出的新rack
	# 维护一个字典，保存每个新 end rack 原来的input rack
	dict_useable_new_end_rack = {rack:[] for rack in useable_new_end_rack}

	# 确定出对应的end rack的新的 input rack
	for start_rack in rack_list:
		if start_rack in no_use_input_rack:
			continue
		for end_rack in useable_new_end_rack:
			# 当这个end_rack是 start_rack的out rack
			if end_rack in index_link[start_rack-1]:
				dict_useable_new_end_rack[end_rack].append(start_rack)

	# 检测出可用变动rack
	new_end_rack = None 
	new_start_rack = None # end rack的新的start rack
	for end_rack, start_racks in dict_useable_new_end_rack.items():
		for start_rack in start_racks:
			if not link[str(start_rack)][end_rack-1].link_use:
				# 找到一条可用的
				# 判断对应的new_end_rack的计算资源是否满足
				if topology.racks[str(new_end_rack)] >= require_cpu:
					new_end_rack = end_rack
					new_start_rack = start_rack
					break
		if new_end_rack:
			break

	if not new_end_rack:
		# 没有合适的终结点
		return "noNewEndRack"
	# 确定需要操作的osm rack
	origin_start_osm_link = link[str(start_rack_num)][end_rack_num-1]
	origin_start_osm_link_start_port = origin_start_osm_link.start_port
	origin_start_osm_link_end_port = origin_start_osm_link.end_port


	origin_end_osm_link = link[str(new_start_rack)][new_end_rack-1]
	origin_end_osm_link_start_port = origin_end_osm_link.start_port
	origin_end_osm_link_end_port = origin_end_osm_link.end_port

	# 先删除原先链路
	link[str(start_rack_num)][end_rack_num-1] = 'None'
	link[str(new_start_rack)][new_end_rack-1] = 'None'
	index_link[start_rack_num-1].remove(end_rack_num)
	index_link[new_start_rack-1].remove(new_end_rack)

	osm.delete_connect(origin_start_osm_link_start_port.port_num)
	osm.delete_connect(origin_end_osm_link_start_port.port_num)

	osm.create_connect(origin_start_osm_link_start_port.port_num, origin_end_osm_link_end_port.port_num)
	osm.create_connect(origin_end_osm_link_start_port.port_num, origin_start_osm_link_end_port.port_num)

	link[str(start_rack_num)][new_end_rack-1] = osm.optical_link[str(origin_start_osm_link_start_port.port_num)]
	link[str(new_start_rack)][end_rack_num-1] = osm.optical_link[str(origin_end_osm_link_start_port.port_num)]
	index_link[start_rack_num-1].append(new_end_rack)
	index_link[new_start_rack-1].append(end_rack_num)
	# 并更新这个信息列表
	topology.link = link
	topology.index_link = index_link

	# 返回对应rack找到的新的结点
	return new_end_rack
