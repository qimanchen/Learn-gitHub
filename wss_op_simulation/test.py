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
	rack_switch_link = creat_rack_switch_link(topology, 1,9,6)
	print(topology.rack_link)
	print(topology.rack_link['1_9_6_1_21_1'].start_mid_osm_link)
	print(topology.racks['1'].up_wss.optical_link)
	print(topology.racks['9'].up_wss.optical_link)
	print(topology.racks['9'].down_wss.optical_link)
	print(topology.racks['6'].down_wss.optical_link)
	release_rack_switch_link(topology, '1_9_6_1_21_1')
	print(topology.rack_link)
	print(topology.racks['1'].up_wss.optical_link)
	print(topology.racks['9'].up_wss.optical_link)
	print(topology.racks['9'].down_wss.optical_link)
	print(topology.racks['6'].down_wss.optical_link)







