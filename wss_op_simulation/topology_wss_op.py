#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑生成及操作文件
"""
# 导入设备参数
from wss_osm_para import  OSMSIZE, DEGREE, BVTNUM , RACKNUM, UPWSS, DOWNWSS, WSSSLOT


class OSMPort(object):
	"""
	定义osm的每一个端口的数据结构
	"""
	
	def __init__(self):
		pass
		
class WSSPort(object):
	"""
	定义wss的每一个端口的数据结构
	"""
	
	def __init__(self):
		pass
		

class Bvt(object):
	"""
	定义每一个收发机的状态数据结构
	"""


class OSM(object):
	"""
	建立osm的连接，同时管理
	两个问题考虑：
	1、是否先建立一个连接
	2、还是直接不建立连接，每次请求到来时都新建立连接
	但这会导致一个问题，就是一个rack完全只与另一个rack相连
	还有是否考虑osm是双向还是单向（一进一出）
	
	"""
	def __init__(self):
		self._osm_size = OSMSIZE
		self._input_port = [i for i in range(1, self._osm_size+1)]
		self._output_port = [i for i in range(1, self._osm_size+1)]
	
	def creat_connect(self):
		"""
		建立一个光连接
		"""
	def delete_connect(self):
		"""
		删除一个连接
		"""
	def check_connect(self):
		"""
		检测某个连接是否存在
		"""


class WSS(object):
	"""
	建立一个wss对象，同时管理wss
	"""
	def __init__(self):
		pass
		
	def set_slot(self):
		"""
		选择通道
		"""
	def set_port(self):
		"""
		选择端口
		"""
	def check_slot(self):
		"""
		检测通道
		"""
	def check_port(self):
		"""
		检测端口
		"""
	
	
class Topology(object):
	"""
	该类主要是拓扑文件的生成，及拓扑的一个改变
	
	# 变换主要有两部分：
		1、光开关内部连接的变化
		2、wss内部的变化
	# bvt与wss的连接为硬连接
	# wss与光开关的连接为硬链接
	"""
	
	def __init__(self):
		pass
		
	
	# 光开关的连接
	def osm(self):
		"""
		建立并管理光开关的连接
		"""
		pass
	
	# 光开关与wss的连接
	def osm_wss(self):
		"""
		建立osm与wss的连接
		"""

	# wss的连接
	def wss(self):
		"""
		建立并管理wss的连接
		"""

	# bvt到wss的连接
	def bvt_wss(self):
		"""
		建立bvt与wss的连接
		"""
		pass
