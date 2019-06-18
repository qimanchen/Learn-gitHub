#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from topology_wss_op import Topology,Rack
from topology_wss_op import WSS
from creat_link import creat_rack_osm_wss_link
from creat_link import release_rack_osm_wss_link
from creat_service_chain import create_fixed_request
from creat_service_chain import create_flex_request_seed
from creat_service_chain import create_vnf_fg_seed
	
if __name__ == "__main__":

	n = 5
	set_seed = 3
	n, mid = create_vnf_fg_seed(n, set_seed)
	print(mid)




def release_rack_osm_wss_link_resource(topo_object, start_rack, end_rack):
	"""
	当释放虚拟链路时,释放相应的物理层的资源
	"""