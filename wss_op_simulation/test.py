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
from main import init_man_queue
from main import Point # 引入整个指针参考兑现
from request_set import create_all_request
from algorithm import create_max_array
from algorithm import read_rga_link
from create_request_with_new_model import create_chose_vnf_fg_seed, decide_vnf_forward_graph
from main import Point
class PP(object):
	"""
	主要用于传递整个仿真的测试参数
	"""
	pass
	
if __name__ == "__main__":
	
	topology = Topology()
	n, set_seed, vnode = create_chose_vnf_fg_seed(5,3)
	
	print(create_max_array(topology, vnode, n))
	print(topology.index_link)
	
	

	




