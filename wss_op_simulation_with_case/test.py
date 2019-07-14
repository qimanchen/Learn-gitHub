#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from topology_wss_op import WSS
from topology_wss_op import RackLink
from topology_wss_op import Topology
from creat_link import creat_rack_osm_wss_link
from creat_link import release_rack_osm_wss_link
from create_switch_link import creat_rack_switch_link, release_rack_switch_link
from modify_osm_link import change_osm_link


class PP(object):
	"""
	主要用于传递整个仿真的测试参数
	"""
	pass

class Test(object):
	
	def __init__(self):
		self.value = 10

def test_test(a):
	d = a
	d.value += 10
	return d
	
if __name__ == "__main__":
	
	topology = Topology()
	creat_rack_osm_wss_link(topology, 1, 9)
	print(topology.rack_link)
	release_rack_osm_wss_link(topology, '1_9_1_21_1')
	print(topology.rack_link)


def case1(topology, pre_rack, vnode, fm, rack_mapped, on):
	"""
	执行case1
	切换对应的wss的链接
	"""
	# 找到还没有映射的vnf
	# 清除之前未映射成功的vnf和相应的rack
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
	if not avaliable_racks:
		# 没有可用的rack
		return False, None

	# 最后一个vnf对象
	require_cpu = vnode[chose_vnf].computer_require
	# 测试
	for rack in avaliable_racks:
		if racks[str(rack)].avaliable_resource >= require_cpu:
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
				return True, (f'{startrack}_{endrack}_{upwssinport}_{upwssoutport}_{slotplan}', rack_link)
	else:
		return False, None
	# if isinstance(creat_state, type(RackLink)):
	# 	pass
		# 表示建路成功
	








