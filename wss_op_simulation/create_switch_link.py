#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-28 15:45:32
# @Author  : Qiman Chen
# @Version : $Id$

"""
针对转发链实现相应的建路和删路
"""
# 导入RacSwitchLink类对象
from topology_wss_op import RackSwitchLink


def creat_switch_link(topo_object, rack_num, start_osm_port, end_osm_port):
	"""
	建立某个rack内部的中转链路
	"""

def creat_rack_switch_link(topo_object, start_rack_num, end_rack_num, mid_rack_num):
	"""
	建立rack之间的转接链路
	"""
	topology = topo_object

	# 确认操作rack对象
	start_rack = topo_object.racks[str(start_rack_num)]

	mid_rack = topo_object.racks[str(mid_rack_num)]

	end_rack = topo_object.racks[str(end_rack_num)]

	# 确认操作wss对象
	start_rack_up_wss = start_rack.up_wss

	mid_rack_up_wss = mid_rack.up_wss
	mid_rack_down_wss = mid_rack.down_wss

	end_rack_down_wss = end_rack.down_wss

	# 检测是否有可用的发射机
	trans = start_rack.get_avaliable_trans()
	if not trans:
		return 'notTrans'
	# 检测是否有可用的接收机
	recv = end_rack.get_avaliable_recv()
	if not recv:
		return 'notRecv'
	# 检测是否有可用的switch链路
	switch_link = mid_rack.get_avaliable_switch_link()
	if not switch_link:
		return 'notSwitch'

	# 检查是否有相同的波长 -- start_rack with mid_rack
	# 检查是否有相同的波长 -- mid_rack with end_rack
	slot_plan = select_slot(strat_rack_up_wss, mid_rack_down_wss, mid_rack_up_wss, end_rack_down_wss)
	# 若没有相同的波长资源，返回相应的标记信息
	try:
		if isinstance(slot_plan, str):
			return slot_plan
	except:
		pass

	# 确认相应的操作设置
	start_rack.trans_using[str(trans.trans_num)] = trans

	end_rack.recv_using[str(recv.recv_num)] = recv

	# 确定对应的osm链路
	start_mid_osm_link = topo_object.link[str(start_rack_num)][mid_rack_num-1]
	mid_end_osm_link = topo_object.link[str(mid_rack_num)][end_rack_num-1]
	# 改变对应链路的状态
	start_mid_osm_link.link_use = True
	mid_end_osm_link.link_use = True

	# 确定对应的osm端口
	# start mid
	start_mid_osm_start_port = start_mid_osm_link.start_port
	start_mid_osm_end_port = start_mid_osm_link.end_port

	# mid end
	mid_end_osm_start_port = mid_end_osm_link.start_port
	mid_end_osm_end_port = mid_end_osm_link.end_port

	# 操作对应的wss
	# strat up wss
	start_wss_out_port = start_mid_osm_start_port.physic_port.wss_port
	start_wss_in_port = trans.trans_port
	trans.to_rack = end_rack_num
	start_rack_up_wss.set_connect(slot_plan, start_wss_in_port.port_num, start_wss_out_port.port_num)

	# mid down wss
	mid_down_wss_in_port = start_mid_osm_end_port.physic_port.wss_port
	mid_down_wss_out_port = switch_link.start_port
	mid_rack_down_wss.set_connect(slot_plan, mid_down_wss_in_prot.port_num, mid_down_wss_out_port.port_num)

	# mid up wss
	mid_up_wss_out_port = mid_end_osm_start_port.physic_port.wss_port
	mid_up_wss_in_port = switch_link.end_port
	mid_rack_up_wss.set_connect(slot_plan, mid_up_wss_in_port.port_num, mid_up_wss_out_port.port_num)

	# 改变swich link的状态
	mid_rack.down_up_link_using[str(mid_down_wss_out_port.port_num)] = switch_link

	# end down wss
	end_wss_in_port = mid_end_osm_end_port.physic_port.wss_port
	end_wss_out_port = recv.recv_port
	recv.to_rack = start_rack_num
	end_rack_down_wss.set_connect(slot_plan, end_wss_in_port.port_num, end_wss_out_port.port_num)

	# 更新osm中wss_link -- 带宽确认
	# start_mid_osm_link
	if not start_mid_osm_link.wss_link:
		start_mid_osm_link.wss_link = {}
	start_mid_osm_link.wss_link[f'{start_rack_num}_{mid_rack_num}_{end_rack_num}_{start_wss_in_port.port_num}_{start_wss_out_port.port_num}'] = 
	start_rack_up_wss.optical_link[str(start_wss_in_port).port_num]
	# mid_end_osm_link
	
	# 记录整条链路的信息
	rack_switch_link = RackSwitchLink()
	rack_switch_link.start_rack = start_rack
	rack_switch_link.mid_rack = mid_rack
	rack_switch_link.end_rack = end_rack

	rack_switch_link.start_mid_osm_link = start_mid_osm_link
	rack_switch_link.mid_end_osm_link = mid_end_osm_link

	rack_switch_link.start_wss_link = start_rack_up_wss.optical_link[str(start_wss_in_port.port_num)]
	rack_switch_link.mid_end_wss_link = mid_rack_down_wss.optical_link[str(mid_down_wss_out_port.port_num)]
	rack_switch_link.mid_start_wss_link = mid_rack_up_wss.optical_link[str(mid_up_wss_in_port.port_num)]
	rack_switch_link.end_wss_link = end_rack_down_wss.optical_link[str(end_wss_out_port.port_num)]

	rack_switch_link.trans = trans
	rack_switch_link.recv = recv
	rack_switch_link.slot_plan = slot_plan

	topo_object.rack_link[f'{start_rack_num}_{mid_rack_num}_{end_rack_num}_{start_wss_in_port.port_num}_{start_wss_out_port.port_num}'] = rack_switch_link
	return rack_switch_link


def select_slot(start_rack_up_wss, mid_rack_down_wss, mid_rack_up_wss, end_rack_down_wss):
	"""
	确认新建链路的slot -- 波长
	没有slot有两种情况:
	1.接收端没有相应的波长
	2.发送端没有相应的波长
	notSlot -- 没有共同可用的波长
	"""

	# 得到wss内部可用的通道计划
	start_avaliable_slot = start_rack_up_wss.check_useable_slot()
	if not start_avaliable_slot:
		return 'notStartWave'
	mid_up_avaliable_slot = mid_rack_up_wss.check_useable_slot()
	if not mid_up_avaliable_slot:
		return 'notMidStartWave'
	mid_down_avaliable_slot = mid_rack_down_wss.check_useable_slot()
	if not mid_down_avaliable_slot:
		return 'notMidEndWave'
	end_avaliable_slot = end_rack_down_wss.check_useable_slot()
	if not start_avaliable_slot:
		return 'notEndWave'

	# 选取规则 -- 每次选择最前面的4个slice
	index = 0
	while index <= len(start_avaliable_slot):
		mid_slot = start_avaliable_slot[index:index+4]
		if not mid_rack_down_wss.check_slot(mid_slot):
			if not mid_rack_up_wss.check_slot(mid_slot):
				if not end_rack_down_wss.check_slot(mid_slot):
					return mid_slot
		index += 4
	return 'notSameSlot'


def release_rack_switch_link(topo_object, start_rack_num, end_rack_num, up_wss_inport):
	"""
	释放中转链路
	"""