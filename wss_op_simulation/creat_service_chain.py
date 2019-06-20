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


def create_fixed_request_seed(n, set_seed):
	"""
	生成固定功能链, 伴随着随机数的种子
	:param n: 链中的结点个数
	:param set_seed: 随机数种子
	:return : 虚拟结点列表
	"""

	random.seed(set_seed)

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

	# 更新随机种子
	set_seed += 1
	if 65530 == set_seed:
		set_seed = 0
	random.seed(set_seed)

	return n, set_seed, virtual_node_dict


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


def create_vnf_fg_seed(n, set_seed):
	"""
	生成服务功能链转发topology图 - 伴随着随机种子的不同
	主要时vnf之间的随机关系矩阵的生成

	# :param vnf_fg - 二维数组: 转发图对象
	:param n - int: vnf的个数
	:传回整个vnf_fg
	"""
	# 更新随机种子
	random.seed(set_seed)

	mid = [[None for _ in range(n)] for _ in range(n)]

	# vnf_fg = mid

	# 随机关系矩阵的生成
	# 主要有三种关系类型
	# 1. 有关联 a 在 b之前 mid[a][b] 随机值 1 - 代表值 2
	# 2. 有关联 a 在 b之后 随机值 3 - 代表值 -2
	# 3. 无关联 并行 随机值 2 -- 代表值 32676
	# 4. 与自身的关系 -- 0
	# 5. 未操作过的结点 -- None

	for i in range(n):
		# forword graph 起点
		# 第一个结点与其他结点的关系
		if i == 0:
			for j in range(n):
				# 去除与自身的关系
				if i != j:
					mid_random = random.randint(1, 3)
					if mid_random == 1:
						mid[i][j] = 2
					elif mid_random == 2:
						mid[i][j] = 32676
					else:
						mid[i][j] = -2
				else:
					mid[i][j] = 0
		else:
			# 除第一结点外的其他结点
			# 关联前面已经设置的结点关系
			for in_i in range(i):
				for in_ii in range(n):
					if mid[in_i][in_ii] == 2:
						for in_iii in range(n):
							if mid[in_i][in_iii] == -2:
								mid[in_ii][in_iii] = -2

					elif mid[in_i][in_ii] == -2:
						for in_iii in range(n):
							if mid[in_i][in_iii] == 2:
								mid[in_ii][in_iii] = 2
			# 开始建立未建立关系的结点之间的关系
			for j in range(n):
				if j < i:
					if mid[j][i] == 2 or mid[j][i] == -2:
						mid[i][j] = -mid[j][i]
						continue
					else:
						mid[i][j] = mid[j][i]
						continue
				else:
					if mid[i-1][i] == 2:
						if (mid[i-1][j] == 2 or mid[i-1][j] == 32676) and mid[i][j] is None:
							if i != j:
								mid_random = random.randint(1,3)
								if mid_random == 1:
									mid[i][j] = 2
								elif mid_random == 2:
									mid[i][j] = 32676
								else:
									mid[i][j] = -2
							else:
								mid[i][j] = 0 # 表示已经操作过但i==j同一结点之间无任何关系可研
						else:
							if i != j and mid[i][j] == None:
								mid[i][j] = -2
							elif i == j:
								mid[i][j] = 0
					elif mid[i-1][i] == -2:
						if (mid[i-1][j] == -2 or mid[i-1][j] == 32676) and mid[i][j] is None:
							if i != j:
								mid_random = random.randint(1, 3)
								if mid_random == 1:
									mid[i][j] = 2
								elif mid_random == 2:
									mid[i][j] = 32676
								else:
									mid[i][j] = -2
							elif i == j:
								mid[i][j] = 0
						else:
							if i != j and mid[i][j] is None:
								mid[i][j] = 2
							elif i == j:
								mid[i][j] = 0
					elif mid[i-1][i] == 32676:
						counter_f = 0
						counter_end = 0
						if i == j and mid[i][j] is None:
							mid[i][j] = 0
						else:
							for m in range(j, n):
								if mid[i-1][m] == 2 and mid[i][m] is None:
									mid_random = random.randint(1,3)
									if mid_random == 1:
										mid[i][m] =2
									elif mid_random == 2:
										mid[i][m] = 32676
									else:
										mid[i][m] = -2
										counter_f += 1
						for m in range(j, n):
							if counter_f == 0:
								if mid[i-1][m] == -2 and mid[i][m] is None:
									mid_random = random.randint(1,3)
									if mid_random == 1:
										mid[i][m] = 2
										counter_end += 1
									elif mid_random == 2:
										mid[i][m] = 32676
									else:
										mid[i][m] = -2

						for m in range(j,n):
							if mid[i-1][m] == 32676 and mid[i][m] is None:
								mid_random = random.randint(1,3)
								if mid_random == 1:
									mid[i][m] = 2
								elif mid_random == 2:
									mid[i][m] = 32676
								else:
									mid[i][m] = -2
						counter_f = 0
						counter_end = 0

	set_seed += 1
	if 65530 == set_seed:
		set_seed = 0

	random.seed(set_seed)

	# 检测并排序好整vnf forwaring graph
	for i in range(n):
		for ii in range(n):
			if mid[i][ii] == 32676:
				for iii in range(n):
					if mid[i][iii] == -2 and mid[iii][ii] == -2:
						mid[i][ii] = -2
					if mid[i][iii] == 2 and mid[iii][ii] == 2:
						mid[i][ii] = 2

	return set_seed, mid
