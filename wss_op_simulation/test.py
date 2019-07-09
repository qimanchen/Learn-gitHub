#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from topology_wss_op import WSS
from topology_wss_op import Topology
from creat_link import creat_rack_osm_wss_link
from creat_link import release_rack_osm_wss_link


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
	print(creat_rack_osm_wss_link(topology, 1,2))

	print(topology.rack_link)
	print(topology.racks['1'].up_wss.port['1'].slot_num)
	release_rack_osm_wss_link(topology, '1_2_1_13_1')
	print(topology.rack_link)
	print(topology.racks['1'].up_wss.port['1'].slot_num)







