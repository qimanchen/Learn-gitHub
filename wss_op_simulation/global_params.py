#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-05-21 20:31:45
# @Author  : Qiman Chen
# @Version : $Id$

"""
所有的公共参数
"""
# load
ERLANG = 180


# 虚拟网络功能链参数

# 1. 虚拟网络功能类型参数
VNF_TYPE_NUM_MAX = 20
VNF_TYPE_NUM_MIN = 1
# 虚拟网络功能的四级关系
FILEVEL = [1,2,3,4]
SELEVEL = [5,6,7,8]
THLEVEL = [9,10,11,12]
FOLEVEL = [13,14,15,16]
MIDLEVEL = [17,18,19,20]

# 资源需求随机范围
# 0.1 - 0.2
# 0.2 - 0.4
# 0.4 - 0.6
# 0 - 1.0
# 这里选定资源范围为 0.2 - 0.6
# 2. 虚拟网络功能需求计算资源的范围
VNF_NEED_MAX_CPU = 60
VNF_NEED_MIN_CPU = 20

# 3. 虚拟网络功能链需求资源的参数
MAX_REQUIRE_BANDWIDTH = 60
MIN_REQUIRE_BANDWIDTH = 20

# 4. 虚拟链路的长度
MAX_SC_LENGTH = 5
MIN_SC_LENGTH = 3

# 物理网络参数

# 网络链路带宽资源参数

# 物理网络计算资源参数
INIT_BANDWIDTH = 100 # 初始带宽资源
INIT_COMPUTER_RESOURCE = 100 # 初始计算资源


# 事件的四种状态
# 1. 初始化状态
START_SIM = 0
# 2. 生成事件，事件未部署，或开始部署状态
LIGHTPATH_REQ = 1
# 3. 事件待释放状态
LIGHTPATH_REQ_END = 10
# 仿真整个事件队列队尾 -- 检测整个仿真的末尾
END_SIM = 100


class RequestEvent(object):
	"""
	请求事件模块
	"""
	def __init__(self, request_id=0, event_type=None, request_array=None):
		self.request_id = request_id # 请求id

		# 事件类型
		# 1. 新生成的事件
		# 2. 运行中的事件
		# 3. 要释放的事件
		self.type = event_type # 事件类型
		self.request = request_array # 请求数组
		self.req_graph_ar = None # 请求的关系矩阵

		self.create_time = None # 事件请求生成时间
		self.service_time = None # 事件服务时间
		self.vnf_num = None # vnf的个数
		self.next = None # 下一条事件，RequestEvent
		self.sub_path = None # 对应的物理路径