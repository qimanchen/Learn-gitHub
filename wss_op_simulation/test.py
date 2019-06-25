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
from time_set import negexp

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
	
	a = Test()
	c = a
	c.value += 10
	print(test_test(c).value)

	

class ShortPath(object):
	"""
	记录最大带宽矩阵中元素
	"""

	def __init__(self, path_id):
	
		# 链路编号 -- 第几条链路
		self.id = path_id
		# 路径类型 -- 转接或正常类型
		self.path_type = None
		# 映射的vnf
		self.start_vnf = None
		self.end_vnf = None
		# 起始rack
		self.start_rack = None
		# 终止rack
		self.end_rack = None
		# 对应的物理路径
		self.rack_link = None
		# 连接的下一端口
		self.next = None


