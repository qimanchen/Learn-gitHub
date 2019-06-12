#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from topology_wss_op import Topology,Rack
from topology_wss_op import WSS
	
if __name__ == "__main__":
	# topology = Topology()

	# # 确定对应的链路
	# link_object = topology.link['1'][1]
	# # 链路一到二的
	# # 确定对应的rack node object
	# rack1_object = topology.link['1'][1].start_port.physic_port # start node
	# rack2_object = topology.link['1'][1].end_port.physic_port # end node

	# # 确定需要操作的wss端口
	# rack1_wss_port = topology.link['1'][1].start_port.physic_port.wss_port.port_num
	# rack2_wss_port = topology.link['1'][1].end_port.physic_port.wss_port.port_num

	# # 确定wss
	# rack1_wss = topology.racks['1'].up_wss
	# rack2_wss = topology.racks['2'].down_wss

	# # 目标rack对象
	# rack1 = topology.racks['1']
	# rack2 = topology.racks['2']
	# slot_plan = 0

	# # 需要提前检测目标rack的slot，防止slot冲突
	# # 检测

	# if rack1.get_goal_bvt('2'):
	# 	print('直接分配资源')
	# else:
	# 	# 需要分配收发机，并设置wss链路
	# 	# 每次取最后一台
	# 	rack1_bvt = rack1.bvt_avaliable[-1]
	# 	rack1.bvt_avaliable.remove(rack1_bvt)
	# 	rack1_bvt.rack_to = '2'

	# 	# 保证接收和发射波长一致
	# 	if not rack1_bvt.recv_wave:
	# 		slot_plan = rack1_wss.add_new_slot()
	# 	else:
	# 		slot_plan = rack1_wss.recv_wave
	# 	rack1_bvt.send_wave = slot_plan
	# 	# 更新资源
	# 	rack1_wss.set_connect(slot_plan, rack1_bvt.send_port.port_num, rack1_wss_port)
	# 	# bvt 连接wss的端口

	# if rack2.get_goal_bvt('1'):
	# 	print('直接分配资源')
	# else:
	# 	rack2_bvt = rack2.bvt_avaliable[-1]
	# 	rack2_bvt.rack_to = '1'
	# 	rack2_bvt.recv_wave = slot_plan
	# 	rack2_wss.set_connect(slot_plan, rack2_bvt.recv_port.port_num, rack2_wss_port)

	# print(rack2.down_wss.optical_link)
	# print(rack2.down)


	# # 设置wss中的slot plan
	# # 注意每个slot plan需要一致，即收发机的收发波长要一致
	# # 

	# # 确定是否需要开启新的发射机

	# print(topology.link['1'][1].start_port.physic_port.wss_port.port_num)
	# print(topology.link['1'][1].end_port.physic_port.wss_port.port_num)
	# print(topology.racks['1'].bvt_avaliable)
	# # 假设topo选到rack1和rack2

	# # 设置rack1中的wss光路 -- 上行wss
	# # 设置rack2中的wss光路 -- 下行wss

	rack = Rack(1)
	for i in rack.up_wss.port.values():
		print(i.physic_port)

	for i in rack.down_wss.port.values():
		print(i.physic_port)