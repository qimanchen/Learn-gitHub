#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-06-19 06:30:03
# @Author  : Qiman Chen
# @Version : $Id$

"""
处理请求
1. 请求的生成
2. 增加请求
3. 释放请求
"""
# 导入请求数组生成函数
# from creat_service_chain import create_flex_request_seed
from create_request_with_new_model import create_chose_vnf_fg_seed
# 导入服务功能关系链生成函数
# from creat_service_chain import create_vnf_fg_seed
from create_request_with_new_model import decide_vnf_forward_graph

# 导入泊松分布时间生成函数
from time_set import negexp
# 事件类型 -- 新建事件
from global_params import LIGHTPATH_REQ
# 导入事件数据结构
from global_params import RequestEvent


class PP(object):
	"""
	主要用于传递整个仿真的测试参数
	"""
	pass


def create_all_request(event_queue, lambda_start, set_seed, seed, sum_time, req_sum, n):
	"""
	生成请求
	请求时间
	请求
	:param event_queue: 事件队列 -- 整体仿真事件队列
	:param lambda_start: erlang设置
	:param set_seed: 请求生成的控制的种子
	:param seed: 事件队列的控制种子
	:param sum_time: 服务时间相关
	:param req_sum: 请求数量
	:param n: 请求中vnf的数量

	:return: None
	"""
	r_g_a = PP()

	inter_time = 0 # 请求生存时间
	service_time = 0 # 请求在系统中的生存时间

	# 服务时间
	mu = 1
	service_time, seed.value = negexp(mu, seed.value)
	# 请求数量
	req_sum.value += 1

	# 
	inter_time, seed.value = negexp(lambda_start, seed.value)
	sum_time.value += inter_time

	# 生成请求的各个结点
	n.value, set_seed.value, v_node = create_chose_vnf_fg_seed(n.value, set_seed.value)
	# 生成各个结点之间的关系矩阵
	decide_vnf_forward_graph(v_node, r_g_a)

	# 将请求加入到事件队列中
	add_request(event_queue, LIGHTPATH_REQ, r_g_a, v_node, sum_time.value, service_time, req_sum.value, n.value)

def add_request(event_queue, event_type, r_g_a, v_node, sum_time, service_time, req_sum, n,sub_path=None):
	"""
	将请求加入到事件队列中
	:param event_queue: 仿真事件队列
	:param event_type: 添加事件的类型 -- 3种
	:param r_g_a: SC中的vnf的关系拓扑
	:param v_node: 生成的请求 -- 各个vnf的结点的资源情况
	:param sum_time: 事件请求生成时间
	:param service_time: 请求生存时间
	:param req_sum: 请求的数量 -- 仿真的第几条请求
	:param n: 请求的vnf的数量 -- sc的长度
	:param sub_path: 请求映射到物理网络中的物理路径

	:return: None
	"""
	p = event_queue

	while p.next and p.next.create_time < sum_time:
		p = p.next

	tmp = RequestEvent()
	tmp.request_id = req_sum
	tmp.type = event_type
	tmp.request = v_node # 请求数组
	tmp.req_graph_ar = r_g_a # 请求的关系矩阵

	tmp.create_time = sum_time # 事件请求生成时间
	tmp.service_time = service_time # 事件服务时间
	tmp.vnf_num = n # vnf的个数
	tmp.sub_path = sub_path # 对应的物理路径

	# 事件队列入队
	tmp.next = p.next
	p.next = tmp

