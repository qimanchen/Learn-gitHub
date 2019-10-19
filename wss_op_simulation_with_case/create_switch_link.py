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
from log_decorator import log_wss_link_create,log_wss_link_release


def creat_switch_link(topo_object, rack_num, start_osm_port, end_osm_port):
	"""
	建立某个rack内部的中转链路
	"""
@log_wss_link_create
def creat_rack_switch_link(topo_object, start_rack_num, mid_rack_num, end_rack_num):
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
	# 确认对应的中间rack的wss
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
	# 确定mid rack的上行wss的输入端口和输入端口
	# down
	switch_link_start_port = switch_link.start_port
	# up
	switch_link_end_port = switch_link.end_port

	# 确定对应的osm链路
	start_mid_osm_link = topo_object.link[str(start_rack_num)][mid_rack_num-1]
	mid_end_osm_link = topo_object.link[str(mid_rack_num)][end_rack_num-1]

	# 确定对应的osm端口
	# 并确定相应的wss与osm连接的端口是否有相应的可用slot
	# start mid
	start_mid_osm_start_port = start_mid_osm_link.start_port
	start_mid_osm_end_port = start_mid_osm_link.end_port
	# 对应的wss的端口是否有可用的slot端口
	if not start_rack_up_wss.check_osm_wss_port(start_mid_osm_start_port.physic_port.wss_port.port_num):
		return "noStartOutPort"
	if not mid_rack_down_wss.check_osm_wss_port(start_mid_osm_end_port.physic_port.wss_port.port_num):
		return "noMidInPort"

	# mid end
	mid_end_osm_start_port = mid_end_osm_link.start_port
	mid_end_osm_end_port = mid_end_osm_link.end_port
	if not mid_rack_up_wss.check_osm_wss_port(mid_end_osm_start_port.physic_port.wss_port.port_num):
		return "noMidOutPort"
	if not end_rack_down_wss.check_osm_wss_port(mid_end_osm_end_port.physic_port.wss_port.port_num):
		return "noEndInPort"
	# 使用已经建立端口的输入和输出端口 -- Debug
	# start_up_wss_link = start_mid_osm_link.wss_link
	# start_up_wss_port_id = 0
	# if not start_up_wss_link:
	# 	start_up_wss_port_id = start_rack_up_wss.find_useable_port()
	# 	if not start_up_wss_port_id:
	# 		return "noStartInPort"
	# else:
	# 	for i in start_up_wss_link.values():
	# 		start_up_wss_port_id = i.in_port.port_num
	# 		break

	# end_down_wss_port_id = 0
	# end_down_wss_link = mid_end_osm_link.wss_link
	# if not end_down_wss_link:
	# 	end_down_wss_port_id = end_rack_down_wss.find_useable_port()
	# 	if not end_down_wss_port_id:
	# 		return "noStartInPort"
	# else:
	# 	for i in end_down_wss_link.values():
	# 		end_down_wss_port_id = i.out_port.port_num
	# 		break

	# 确定start rack的输入端口
	start_up_wss_port_id = start_rack_up_wss.find_useable_port()
	if not start_up_wss_port_id:
		return "noStartInPort"
	# 确定end rack的输出端口
	end_down_wss_port_id = end_rack_down_wss.find_useable_port()
	if not end_down_wss_port_id:
		return "noEndOutPort"

	# 确定slot
	# no_use_slot包括mid中没有已经使用的slot和end rack中使用的slot
	# mid rack的down wss的接入端口的slot字典
	mid_down_wss_use_slot = start_mid_osm_end_port.physic_port.wss_port.slot_use
	if not mid_down_wss_use_slot:
		mid_down_wss_use_slot=[]
	# mid rack的up wss的接入端口的slot字典
	mid_up_wss_use_slot = mid_end_osm_start_port.physic_port.wss_port.slot_use
	if not mid_up_wss_use_slot:
		mid_up_wss_use_slot = []
	# end rack的down wss的接入端口的slot字典
	end_down_wss_use_slot = mid_end_osm_end_port.physic_port.wss_port.slot_use
	if not end_down_wss_use_slot:
		end_down_wss_use_slot = []

	# 将三者的slot组合
	use_slot = set(mid_down_wss_use_slot)
	use_slot = use_slot.update(set(mid_up_wss_use_slot))
	if not use_slot:
		use_slot = set([])
	else:
		use_slot = use_slot.update(set(end_down_wss_use_slot))

	# 检查是否有相同的波长 -- start_rack with mid_rack
	# 检查是否有相同的波长 -- mid_rack with end_rack
	no_use_slot = dict(zip([i for i in range(len(use_slot))], use_slot)) # 组合成字典传入，字典的键值无特殊意义
	slot_plan = start_rack_up_wss.chose_slot(start_up_wss_port_id, start_mid_osm_start_port.physic_port.wss_port.port_num, no_use_slot)
	if not slot_plan:
		return "noSameSlot"
	
	# 改变对应链路的状态
	start_mid_osm_link.link_use = True
	mid_end_osm_link.link_use = True
	# 确认相应的操作设置
	start_rack.trans_using[str(trans.trans_num)] = trans
	end_rack.recv_using[str(recv.recv_num)] = recv

	# 操作对应的wss
	# strat up wss
	start_rack_up_wss.set_connect(slot_plan, start_up_wss_port_id, start_mid_osm_start_port.physic_port.wss_port.port_num)

	# mid down wss
	mid_rack_down_wss.set_connect(slot_plan, start_mid_osm_end_port.physic_port.wss_port.port_num, switch_link_start_port.port_num)

	# mid up wss
	mid_rack_up_wss.set_connect(slot_plan, switch_link_end_port.port_num, mid_end_osm_start_port.physic_port.wss_port.port_num)

	# 改变swich link的状态
	mid_rack.down_up_link_using[str(switch_link_start_port.port_num)] = switch_link

	# end down wss
	end_rack_down_wss.set_connect(slot_plan, mid_end_osm_end_port.physic_port.wss_port.port_num, end_down_wss_port_id)

	# 更新osm中wss_link -- 带宽确认
	# start_mid_osm_link
	if not start_mid_osm_link.wss_switch_link:
		start_mid_osm_link.wss_switch_link = {}
	start_mid_osm_link.wss_switch_link[f'{start_rack_num}_{mid_rack_num}_{end_rack_num}_{start_up_wss_port_id}_{start_mid_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}'] =\
	start_rack_up_wss.optical_link[f'{start_up_wss_port_id}_{start_mid_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}']
	# mid_end_osm_link
	if not mid_end_osm_link.mid_link:
		mid_end_osm_link.mid_link = {}
	mid_end_osm_link.mid_link[f'{start_rack_num}_{mid_rack_num}_{end_rack_num}_{start_up_wss_port_id}_{start_mid_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}'] =\
	start_rack_up_wss.optical_link[f'{start_up_wss_port_id}_{start_mid_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}']
	
	# 记录整条链路的信息
	rack_switch_link = RackSwitchLink()
	rack_switch_link.start_rack = start_rack
	rack_switch_link.mid_rack = mid_rack
	rack_switch_link.end_rack = end_rack

	rack_switch_link.start_mid_osm_link = start_mid_osm_link
	rack_switch_link.mid_end_osm_link = mid_end_osm_link

	# start mid
	rack_switch_link.start_wss_link = start_rack_up_wss.optical_link[f'{start_up_wss_port_id}_{start_mid_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}']
	rack_switch_link.mid_end_wss_link = mid_rack_down_wss.optical_link[f'{start_mid_osm_end_port.physic_port.wss_port.port_num}_{switch_link_start_port.port_num}_{slot_plan}']

	# mid end
	rack_switch_link.mid_start_wss_link = mid_rack_up_wss.optical_link[f'{switch_link_end_port.port_num}_{mid_end_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}']
	rack_switch_link.end_wss_link = end_rack_down_wss.optical_link[f'{mid_end_osm_end_port.physic_port.wss_port.port_num}_{end_down_wss_port_id}_{slot_plan}']

	rack_switch_link.trans = trans
	rack_switch_link.recv = recv
	rack_switch_link.slot_plan = slot_plan
	rack_link_id = f'{start_rack_num}_{mid_rack_num}_{end_rack_num}_{start_up_wss_port_id}_{start_mid_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}'
	topo_object.rack_link[f'{start_rack_num}_{mid_rack_num}_{end_rack_num}_{start_up_wss_port_id}_{start_mid_osm_start_port.physic_port.wss_port.port_num}_{slot_plan}'] = rack_switch_link
	return rack_switch_link

@log_wss_link_release
def release_rack_switch_link(topo_object, rack_link_id):
	"""
	释放中转链路
	rack_link_id: start_rack_num,mid_rack_num,end_rack_num, start_up_wss_port_num, start_up_wss_out_port_num
	"""
	# 确定对应的rack
	# 对应start rack的
	# if rack_link_id == "17_8_22_4_22_3":
	# 	print("release", topo_object.rack_link[rack_link_id])
	# 	print("release", topo_object.rack_link[rack_link_id].end_wss_link)
	# 	print("release", topo_object.rack_link[rack_link_id].end_wss_link.port[str(24)].slot_use)

	start_rack_num, mid_rack_num, end_rack_num, start_up_wss_in_port_id, start_up_wss_out_port_id, slot_plan = list(map(int, rack_link_id.split('_')))

	topology = topo_object

	# 确定相应的rack
	start_rack = topo_object.racks[str(start_rack_num)]
	mid_rack = topo_object.racks[str(mid_rack_num)]
	end_rack = topo_object.racks[str(end_rack_num)]

	# 确定对应的rack link
	rack_link = topo_object.rack_link[rack_link_id]

	# 确定对应的osm链路
	start_mid_osm_link = topo_object.link[str(start_rack_num)][mid_rack_num-1]
	mid_end_osm_link = topo_object.link[str(mid_rack_num)][end_rack_num-1]

	# 确定对应的操作的wss
	start_up_wss = start_rack.up_wss
	mid_down_wss = mid_rack.down_wss
	mid_up_wss = mid_rack.up_wss
	end_down_wss = end_rack.down_wss

	# 确定各个wss对应链路的端点
	# start_up_wss -- 参数中已经给出
	# mid_down_wss
	mid_down_wss_link = rack_link.mid_end_wss_link
	mid_down_wss_in_port_id = mid_down_wss_link.in_port.port_num
	mid_down_wss_out_port_id = mid_down_wss_link.out_port.port_num

	# mid_up_wss
	mid_up_wss_link = rack_link.mid_start_wss_link
	mid_up_wss_in_port_id = mid_up_wss_link.in_port.port_num
	mid_up_wss_out_port_id = mid_up_wss_link.out_port.port_num
	# end_down_wss
	end_down_wss_link = rack_link.end_wss_link
	end_down_wss_in_port_id = end_down_wss_link.in_port.port_num
	end_down_wss_out_port_id = end_down_wss_link.out_port.port_num

	# 确定收发机
	trans = rack_link.trans
	recv = rack_link.recv

	# 更新一些结点和链路的信息
	# 更新osm中记录的wss链路信息
	del start_mid_osm_link.wss_switch_link[rack_link_id]
	del mid_end_osm_link.mid_link[rack_link_id]
	# 确定osm链路中是否已空
	if not start_mid_osm_link.wss_link and not start_mid_osm_link.wss_switch_link and not start_mid_osm_link.mid_link:
		start_mid_osm_link.link_use = False
	if not mid_end_osm_link.wss_link and not mid_end_osm_link.wss_switch_link and not mid_end_osm_link.mid_link:
		mid_end_osm_link.link_use = False

	# 更新收发机
	del start_rack.trans_using[str(trans.trans_num)]
	del end_rack.recv_using[str(recv.recv_num)]

	# 删除各个wss 链路
	start_up_wss.delete_connect(slot_plan, start_up_wss_in_port_id, start_up_wss_out_port_id)
	mid_down_wss.delete_connect(slot_plan, mid_down_wss_in_port_id, mid_down_wss_out_port_id)
	mid_up_wss.delete_connect(slot_plan, mid_up_wss_in_port_id, mid_up_wss_out_port_id)
	
	end_down_wss.delete_connect(slot_plan, end_down_wss_in_port_id, end_down_wss_out_port_id)

	del topo_object.rack_link[rack_link_id]
