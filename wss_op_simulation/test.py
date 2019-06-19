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
	
if __name__ == "__main__":

	n_point = Point(5)
	set_seed_point = Point(3)
	lambda_start = 1/180
	req_sum = Point(0)
	seed_point = Point(22)
	new_request_time_point = Point(0)
	man_h = init_man_queue()

	create_all_request(man_h, lambda_start, set_seed_point, seed_point, new_request_time_point, req_sum, n_point)
	create_all_request(man_h, lambda_start, set_seed_point, seed_point, new_request_time_point, req_sum, n_point)
	create_all_request(man_h, lambda_start, set_seed_point, seed_point, new_request_time_point, req_sum, n_point)

	print(req_sum.value)
	print(n_point.value)
	print(seed_point.value)
	print(new_request_time_point.value)
	while man_h:
		print(man_h.request)
		print(man_h.create_time)
		print(man_h.service_time)
		print(man_h.vnf_num)
		print(man_h.req_graph_ar)
		man_h = man_h.next
	





def release_rack_osm_wss_link_resource(topo_object, start_rack, end_rack):
	"""
	当释放虚拟链路时,释放相应的物理层的资源
	"""