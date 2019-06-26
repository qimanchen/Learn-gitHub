#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-21 23:18:06
# @Author  : Qiman Chen
# @Version : $Id$

"""
通过新的模式生成服务功能链请求
"""
import random

# 虚拟结点类型 - 共10种
from global_params import VNF_TYPE_NUM_MAX, VNF_TYPE_NUM_MIN
# 虚拟结点需要资源 - 20-60
from global_params import VNF_NEED_MAX_CPU, VNF_NEED_MIN_CPU
# 虚拟网络功能链需求资源 - 20 - 60
from global_params import MAX_REQUIRE_BANDWIDTH, MIN_REQUIRE_BANDWIDTH
# 虚拟链路的长度 - 3 - 5
from global_params import MAX_SC_LENGTH, MIN_SC_LENGTH
# 引入四种不同级别的vnf
from global_params import FILEVEL, SELEVEL, THLEVEL, FOLEVEL, MIDLEVEL


class VNode(object):
	"""
	定义虚拟结点
	"""
	def __init__(self, virtual_node_type, computer_require, bandwidth_require):
		self.virtual_node_type = virtual_node_type
		self.computer_require = computer_require
		self.bandwidth_require = bandwidth_require

# TODO
def create_chose_vnf_fg_seed(n, set_seed):
	"""
	通过确定的vnf之间的关系，选择除相应的vnf构成vnf之间的关系图
	总共4级关系，其中4级前后，另外一级是与其他都无前后关系
	每一级有四个结点，总共20个结点
	"""
	random.seed(set_seed) # 随机种子的确定

	# 注意这个n值需要返回给上层函数
	n = random.randint(MIN_SC_LENGTH, MAX_SC_LENGTH)

	virtual_node_dict = {} # 虚拟链路表
	vnode_type_list = [] # 记录选中的type,防止选到重复的node类型

	for i in range(1, n+1):
		if i == 1:
			# 第一个结点不用去重
			# 第一个节点
			virtual_node_type = random.randint(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)
			virtual_node_cpu = random.randint(VNF_NEED_MIN_CPU, VNF_NEED_MAX_CPU)
			virtual_bandwidth = random.randint(MIN_REQUIRE_BANDWIDTH, MAX_REQUIRE_BANDWIDTH)
			virtual_node_dict[virtual_node_type] = VNode(virtual_node_type, virtual_node_cpu, virtual_bandwidth)
			vnode_type_list.append(virtual_node_type) # 加入去重列表
		else:
			# 防止选择到重复的type
			virtual_node_type = random.randint(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)
			while virtual_node_type in vnode_type_list:
				virtual_node_type = random.randint(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)

			virtual_node_cpu = random.randint(VNF_NEED_MIN_CPU, VNF_NEED_MAX_CPU)
			virtual_bandwidth = random.randint(MIN_REQUIRE_BANDWIDTH, MAX_REQUIRE_BANDWIDTH)
			virtual_node_dict[virtual_node_type] = VNode(virtual_node_type, virtual_node_cpu, virtual_bandwidth)
			vnode_type_list.append(virtual_node_type) # 加入去重列表
	# 更新随机种子
	set_seed += 1
	if 65530 == set_seed:
		set_seed = 0
	random.seed(set_seed)

	return n, set_seed, virtual_node_dict
	

def decide_vnf_forward_graph(virtual_node_dict, pp):
	"""
	确定vnf之间的关系，主要是确定vnf之间的逻辑关系
	:param virtual_node_dict: vnf结点hash表
	:param pp: 存储节点等级对象
	:return： vnf之间的关系表
	"""
	# pp = PP() # 存储节点等级对象
	
	pp.fi_level = []
	pp.se_level = []
	pp.th_level = []
	pp.fo_level = []
	pp.mid_level = []
	for vnode in virtual_node_dict.keys():
		# 在第一级
		if vnode in FILEVEL:
			pp.fi_level.append(vnode)
		elif vnode in SELEVEL:
			pp.se_level.append(vnode)
		elif vnode in THLEVEL:
			pp.th_level.append(vnode)
		elif vnode in FOLEVEL:
			pp.fo_level.append(vnode)
		elif vnode in MIDLEVEL:
			pp.mid_level.append(vnode)
		else:
			raise ValueError('不存在的结点类型！')
	# return pp


