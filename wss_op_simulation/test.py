#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from topology_wss_op import WSS
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
	link = topology.link
	index_link = topology.index_link

	print(link['1'][8].start_port.physic_port.rack_num)
	print(link['1'][8].end_port.physic_port.rack_num)
	
	print(link['20'][1].start_port.physic_port.rack_num)
	print(link['20'][1].end_port.physic_port.rack_num)

	change_osm_link(topology, 1,9)

	print(link['1'][1].start_port.physic_port.rack_num)
	print(link['1'][1].end_port.physic_port.rack_num)

	print(link['20'][8].start_port.physic_port.rack_num)
	print(link['20'][8].end_port.physic_port.rack_num)






