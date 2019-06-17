#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-05-21 20:28:34
# @Author  : Qiman Chen
# @Version : $Id$

"""
生成灵活的请求链
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


class Seed(object):
	"""
	确定随机种子的传递
	"""
	def __init__(self, random_seed=1):
		self.seed = random_seed


def random_int(max_value, min_value):
	"""
	生成最大和最小之间的随机整数

	:param max_value: 最大值
	:param min_value: 最小值
	:return: 整数随机值
	"""
	return random.randint(max_value, min_value)

def random_float(max_value, min_value):
	"""
	生成最大和最小之间的随机浮点数

	:param max_value: 最大值
	:param min_value: 最小值
	:return: 整数随机值
	"""
	return random.random()


class VNode(object):
	"""
	定义虚拟结点
	"""
	def __init__(self, virtual_node_type, computer_require, bandwidth_require):
		self.virtual_node_type = virtual_node_type
		self.computer_require = computer_require
		self.bandwidth_require = bandwidth_require


def create_fixed_request(n):
	"""
	生成固定功能链
	:param n: 链中的结点个数
	:return : 虚拟结点列表
	"""
	virtual_node_dict = {} # 虚拟链路表
	vnode_type_list = [] # 记录选中的type,防止选到重复的node类型

	for i in range(1, n+1):
		# 链结点从 1 到 5
		if i == 1:
			# 第一个节点
			virtual_node_type = random_int(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)
			virtual_node_cpu = random_int(VNF_NEED_MIN_CPU, VNF_NEED_MAX_CPU)
			virtual_bandwidth = random_int(MIN_REQUIRE_BANDWIDTH, MAX_REQUIRE_BANDWIDTH)
			virtual_node_dict[i] = VNode(virtual_node_type, virtual_node_cpu, virtual_bandwidth)
			vnode_type_list.append(virtual_node_type) # 加入去重列表

		else:
			# 防止选择到重复的type
			virtual_node_type = random_int(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)
			while virtual_node_type in vnode_type_list:
				virtual_node_type = random_int(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)

			virtual_node_cpu = random_int(VNF_NEED_MIN_CPU, VNF_NEED_MAX_CPU)
			virtual_bandwidth = random_int(MIN_REQUIRE_BANDWIDTH, MAX_REQUIRE_BANDWIDTH)
			virtual_node_dict[i] = VNode(virtual_node_type, virtual_node_cpu, virtual_bandwidth)
			vnode_type_list.append(virtual_node_type) # 加入去重列表
	return virtual_node_dict


def create_flex_request_seed(n, set_seed):
	"""
	生成灵活功能链, 伴随着随机种子

	:param n: 随机链的结点个数
	:param set_seed: 随机种子 -- 使得每次随机都按照某种规律变化
	"""

	random.seed(set_seed) # 随机种子的确定

	# 注意这个n值需要返回给上层函数
	n = random_int(MIN_SC_LENGTH, MAX_SC_LENGTH)

	virtual_node_dict = {} # 虚拟链路表
	vnode_type_list = [] # 记录选中的type,防止选到重复的node类型

	for i in range(1, n+1):
		if i == 0:
			# 第一个结点不用去重
			# 第一个节点
			virtual_node_type = random_int(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)
			virtual_node_cpu = random_int(VNF_NEED_MIN_CPU, VNF_NEED_MAX_CPU)
			virtual_bandwidth = random_int(MIN_REQUIRE_BANDWIDTH, MAX_REQUIRE_BANDWIDTH)
			virtual_node_dict[i] = VNode(virtual_node_type, virtual_node_cpu, virtual_bandwidth)
			vnode_type_list.append(virtual_node_type) # 加入去重列表
		else:
			# 防止选择到重复的type
			virtual_node_type = random_int(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)
			while virtual_node_type in vnode_type_list:
				virtual_node_type = random_int(VNF_TYPE_NUM_MIN, VNF_TYPE_NUM_MAX)

			virtual_node_cpu = random_int(VNF_NEED_MIN_CPU, VNF_NEED_MAX_CPU)
			virtual_bandwidth = random_int(MIN_REQUIRE_BANDWIDTH, MAX_REQUIRE_BANDWIDTH)
			virtual_node_dict[i] = VNode(virtual_node_type, virtual_node_cpu, virtual_bandwidth)
			vnode_type_list.append(virtual_node_type) # 加入去重列表
	# 更新随机种子
	set_seed += 1
	if 65530 == set_seed:
		set_seed = 0
	random.seed(set_seed)

	return n, set_seed, virtual_node_dict
