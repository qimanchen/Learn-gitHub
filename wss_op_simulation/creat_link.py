#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-05-31 10:32:32
# @Author  : Qiman Chen
# @Version : $Id$

"""
各种建路子程序和路查询子程序
"""
# 确认建立的新路
from topology_wss_op import RackLink
from global_params import INIT_BANDWIDTH
from global_params import INIT_COMPUTER_RESOURCE


def creat_rack_osm_wss_link(topo_object, start_rack_num, end_rack_num):
	"""
	确认了start_rack和end_rack
	发现已经建立的链路不可用
	需要建立新的链路:
	1.建立新的wss的连接
	2.确认recv连接
	3. 更新osm_link的使用状态
	:param topo_object: 传入topo_object对整体系统的改变
	:param start_rack_num: 起点rack -- rack_num
	:param end_rack_num: 终结点rack -- rack_num

	几种返回值:
	notRecv -- 没有接收机
	notTrans -- 没有发射机
	notStartHost -- 发射rack没有host
	notEndHost -- 接收rack没有host
	notStartWave -- 发射端没有波长资源
	notEndWave -- 接收端没有波长资源
	notWave -- startRack和endrack没有相应的波长资源
	"""

	# 先确认资源是否足够
	topology = topo_object # topo object

	# 确认操作rack对象
	start_rack = topo_object.racks[str(start_rack_num)]

	end_rack = topo_object.racks[str(end_rack_num)]

	# 确认操作wss对象
	start_rack_up_wss = start_rack.up_wss
	end_rack_down_wss = end_rack.down_wss

	# 检查是否有可用的发射机 -- start_rack
	trans = start_rack.get_avaliable_trans()
	if not trans:
		return 'notTrans'
	# 检查是否有可用的接收机 -- end_rack
	recv = end_rack.get_avaliable_recv()
	if not recv:
		return 'notRecv'
	# 检查startrack是否有可用波长
	# 检查endrack是否有同样的可用波长
	slot_plan = select_slot(start_rack_up_wss, end_rack_down_wss)
	# 没有相应的波长资源,返回相应的标记信息
	try:
		if isinstance(slot_plan, str):
			return slot_plan
	except:
		pass
	# # 检测是否有相应的host可用
	# start_host = start_rack.get_avaliable_host()
	# if not start_host:
	# 	return 'notStartHost'
	# end_host = end_rack.get_avaliable_host()
	# if not end_host:
	# 	return 'notEndHost'

	# 进行相应的设置
	# 确认相应的设备使用
	# trans
	start_rack.trans_using[str(trans.trans_num)] = trans
	# recv
	end_rack.recv_using[str(recv.recv_num)] = recv
	# # start_host
	# start_rack.host_using[str(start_host.host_num)] = start_host
	# # end_host
	# end_rack.host_using[str(end_host.host_num)] = end_host

	# 通过rack的连接来确认
	# 确定相应的osm链
	osm_link = topology.link[str(start_rack_num)][end_rack_num-1]
	# 改变osm_link的状态
	osm_link.link_use = True
	
	osm_start_port = osm_link.start_port # 确认osm输入端口
	osm_end_port = osm_link.end_port # 确认osm输出端口 -- osmPort object
	
	# 确认start_rack_up_wss的输出端口 -- WssPort object
	start_wss_out_port = osm_start_port.physic_port.wss_port
	# 确认start_rack_up_wss的输入端口 -- 根据trans
	start_wss_in_port = trans.trans_port
	# 确认trans连接的rack
	trans.to_rack = start_rack_num
	# start_rack_up_wss 建路
	start_rack_up_wss.set_connect(slot_plan, start_wss_in_port.port_num, start_wss_out_port.port_num)

	# 确认end_rack_down_wss的输入端口
	end_wss_in_port = osm_end_port.physic_port.wss_port
	# 确认end_rack_down_wss的输出端口
	end_wss_out_port = recv.recv_port
	# 确认recv连接的rack
	recv.to_rack = end_rack_num
	# end_rack_down_wss 建路
	end_rack_down_wss.set_connect(slot_plan, end_wss_in_port.port_num, end_wss_out_port.port_num)

	# 更新osm中wss_link --> 带宽确认
	if not osm_link.wss_link:
		osm_link.wss_link = {}
	# 记录相应的链路方便带宽查询
	osm_link.wss_link['{}_{}_{}_{}'.format(start_rack_num, end_rack_num, start_wss_in_port.port_num,
		start_wss_out_port.port_num)] = start_rack_up_wss.optical_link[str(start_wss_in_port.port_num)]

	# 记录该条物理链路的完整信息
	rack_link = RackLink()
	rack_link.start_rack = start_rack
	rack_link.end_rack = end_rack

	rack_link.osm_link = osm_link

	rack_link.start_wss_link = start_rack_up_wss.optical_link[str(start_wss_in_port.port_num)]
	rack_link.end_wss_link = end_rack_down_wss.optical_link[str(end_wss_out_port.port_num)]

	rack_link.trans = trans
	rack_link.recv = recv
	rack_link.slot_plan = slot_plan
	# rack_link.start_host = start_host
	# rack_link.end_host = end_host

	topology.rack_link['{}_{}_{}_{}'.format(start_rack_num,end_rack_num,
		start_wss_in_port.port_num,start_wss_out_port.port_num)] = rack_link
	return rack_link

def select_slot(start_rack_up_wss, end_rack_down_wss):
	"""
	确认新建链路的slot -- 波长
	没有slot有两种情况:
	1.接收端没有相应的波长
	2.发送端没有相应的波长
	"""

	# 得到wss内部可用的通道计划
	start_avaliable_slot = start_rack_up_wss.check_useable_slot()
	if not start_avaliable_slot:
		return 'notStartWave'
	end_avaliable_slot = end_rack_down_wss.check_useable_slot()
	if not start_avaliable_slot:
		return 'notEndWave'

	# 选取规则 -- 每次选择最前面的4个slice
	index = 4
	while index <= len(start_avaliable_slot):
		mid_slot = start_avaliable_slot[0:index]
		if not end_rack_down_wss.check_slot(mid_slot):
			return mid_slot
		index += 4
	return 'notSlot'

def renew_resources(topology, sub_path, vnode):
	"""
	更新选中链路的资源
	:param sub_path: 整个映射链路
	"""
	racks = topology.racks # 拓扑文件中的
	rack_links = topology.rack_link
	sub_path = sub_path.next # 取得第一条链路

	csub_path = sub_path
	while csub_path:
		mid_rack_link = csub_path.rack_link # 对应的物理链路
		start_vnf = csub_path.start_vnf
		start_rack_num = mid_rack_link[1].start_rack.rack_num
		wss_link_id = mid_rack_link[0]
		if not csub_path.next:
			# 检测是否是路径的结尾
			end_vnf = csub_path.end_vnf
			end_rack_num = mid_rack_link[1].end_rack.rack_num
			
			# 更新物理资源
			racks[str(start_rack_num)].avaliable_resource -= vnode[start_vnf].computer_require
			racks[str(end_rack_num)].avaliable_resource -= vnode[end_vnf].computer_require
			# mid_rack_link.end_rack.avaliable_resource -= vnode[end_vnf].computer_require
			# mid_rack_link.start_rack.avaliable_resource -= vnode[start_vnf].computer_require
			# 更新带宽资源
			rack_links[wss_link_id].start_wss_link.bandwidth_avaliable -= vnode[start_vnf].bandwidth_require
		else:
			# 更新物理资源
			racks[str(start_rack_num)].avaliable_resource -= vnode[start_vnf].computer_require
			# mid_rack_link.start_rack.avaliable_resource -= vnode[start_vnf].computer_require
			# 更新带宽资源
			rack_links[wss_link_id].start_wss_link.bandwidth_avaliable -= vnode[start_vnf].bandwidth_require
		csub_path = csub_path.next

def release_resources(sub_path, vnode, topology):
	"""
	释放物理网络资源
	"""
	# 当释放映射失败的链时
	if not sub_path:
		return
	racks = topology.racks # 拓扑文件中的
	rack_links = topology.rack_link
	sub_path = sub_path.next # 取得第一条链路

	csub_path = sub_path
	while csub_path:
		mid_rack_link = csub_path.rack_link # 对应的物理链路
		start_vnf = csub_path.start_vnf
		start_rack_num = mid_rack_link[1].start_rack.rack_num
		wss_link_id = mid_rack_link[0]
		if not csub_path.next:
			# 检测是否是路径的结尾
			end_vnf = csub_path.end_vnf
			end_rack_num = mid_rack_link[1].end_rack.rack_num
			# 更新物理资源
			racks[str(start_rack_num)].avaliable_resource += vnode[start_vnf].computer_require
			# mid_rack_link.start_rack.avaliable_resource += vnode[start_vnf].computer_require
			# 尾结点
			racks[str(end_rack_num)].avaliable_resource += vnode[end_vnf].computer_require
			# mid_rack_link.end_rack.avaliable_resource += vnode[end_vnf].computer_require
			# 更新带宽资源
			rack_links[wss_link_id].start_wss_link.bandwidth_avaliable += vnode[start_vnf].bandwidth_require
			# mid_rack_link.start_wss_link.bandwidth_avaliable += vnode[start_vnf].bandwidth_require
			
		else:
			# 更新物理资源
			racks[str(start_rack_num)].avaliable_resource += vnode[start_vnf].computer_require
			# mid_rack_link.start_rack.avaliable_resource += vnode[start_vnf].computer_require
			# 更新带宽资源
			rack_links[wss_link_id].start_wss_link.bandwidth_avaliable += vnode[start_vnf].bandwidth_require
			# mid_rack_link.start_wss_link.bandwidth_avaliable += vnode[start_vnf].bandwidth_require
		csub_path = csub_path.next

	csub_path = sub_path
	while csub_path:
		mid_rack_link = csub_path.rack_link
		start_rack_num = mid_rack_link[1].start_rack.rack_num
		end_rack_num = mid_rack_link[1].end_rack.rack_num
		wss_link_id = mid_rack_link[0]
		if rack_links[wss_link_id].start_wss_link.bandwidth_avaliable == rack_links[wss_link_id].start_wss_link.bandwidth and racks[str(start_rack_num)].avaliable_resource == racks[str(start_rack_num)].computer_resource and racks[str(end_rack_num)].avaliable_resource == racks[str(end_rack_num)].computer_resource:
			release_rack_osm_wss_link(topology, start_rack_num,end_rack_num, mid_rack_link[1].start_wss_link.in_port.port_num)
			pass
		csub_path = csub_path.next

def release_rack_osm_wss_link(topo_object, start_rack_num, end_rack_num, up_wss_inport):
	"""
	当检测到wss中的带宽完全空闲时 -- 可用资源等于初始资源
	释放到相应的wss中的链路
	释放掉相应的trans和recv
	释放掉相应的host的资源

	:param up_wss_inport: 具体光学链路的唯一标识,上行wss的inport端口号
	"""
	topology = topo_object
	# 确认操作rack对象
	start_rack = topo_object.racks[str(start_rack_num)]

	end_rack = topo_object.racks[str(end_rack_num)]

	# 确认操作wss对象
	start_rack_up_wss = start_rack.up_wss
	end_rack_down_wss = end_rack.down_wss

	# 通过rack的连接来确认
	# 确定相应的osm链
	osm_link = topology.link[str(start_rack_num)][end_rack_num-1]
	
	osm_start_port = osm_link.start_port # 确认osm输入端口
	osm_end_port = osm_link.end_port # 确认osm输出端口 -- osmPort object

	# 确认start_rack_up_wss的输出端口 -- WssPort object
	start_wss_out_port = osm_start_port.physic_port.wss_port

	rack_link = topology.rack_link['{}_{}_{}_{}'.format(start_rack_num,end_rack_num,
		up_wss_inport,start_wss_out_port.port_num)]

	# 确认相关的信息
	trans = rack_link.trans
	recv = rack_link.recv
	# start_host = rack_link.start_host
	# end_host = rack_link.end_host
	
	# 确认start_rack_up_wss的输出端口 -- WssPort object
	start_wss_out_port = osm_start_port.physic_port.wss_port
	# 确认start_rack_up_wss的输入端口 -- 根据trans
	start_wss_in_port = trans.trans_port
	# 确认trans连接的rack
	trans.to_rack = None
	

	# 确认end_rack_down_wss的输入端口
	end_wss_in_port = osm_end_port.physic_port.wss_port
	# 确认end_rack_down_wss的输出端口
	end_wss_out_port = recv.recv_port
	# 删除recv连接的rack
	recv.to_rack = None
	
	# 删除osm_link中wss_link的记录
	del osm_link.wss_link['{}_{}_{}_{}'.format(start_rack_num,end_rack_num,start_wss_in_port.port_num,
		start_wss_out_port.port_num)]

	# 改变osm_link的状态 -- 如果当wss_link为空字典时
	if not osm_link.wss_link:
		osm_link.link_use = False

	# 删除rack_link中的记录
	del topology.rack_link['{}_{}_{}_{}'.format(start_rack_num,end_rack_num,
		up_wss_inport,start_wss_out_port.port_num)]

	del start_rack.trans_using[str(trans.trans_num)]
	# recv
	del end_rack.recv_using[str(recv.recv_num)]
	# # start_host
	# del start_rack.host_using[str(start_host.host_num)]
	# # end_host
	# del end_rack.host_using[str(end_host.host_num)]

	# start_rack_up_wss 建路
	start_rack_up_wss.delete_connect(start_wss_in_port.port_num, start_wss_out_port.port_num)

	# 删除end_rack_down_wss 建路
	end_rack_down_wss.delete_connect(end_wss_in_port.port_num, end_wss_out_port.port_num)

