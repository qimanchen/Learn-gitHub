#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑生成及操作文件
"""
# 导入设备参数
from wss_osm_para import  OSMSIZE, DEGREE, BVTNUM, RACKNUM, UPWSS, DOWNWSS, WSSSLOT


class OSMPort(object):
	"""
	定义osm的每一个端口的数据结构
	"""
	
	def __init__(self, port_num, port_type='input', port_status='ENABLE', port_use=None, physic_port=None, wave=None):
		self._port_num = port_num # 端口号
		self._port_type = port_type # 端口类型 - input， output
		self._port_status = port_status # 端口的可用状态 -- ENABLE, DISABLED
		self._port_use = port_use # 端口是否与光开关的另外的端口相连 -- 光开关内部的连接, None-未连接到其他结点，

		self._physic_port = physic_port # 物理连接端口
		self._wave = port_num # 端口中传输的波长

	@property
	def port_num(self):
		return self._port_num

	@property
	def port_type(self):
		return self._port_type

	@property
	def port_status(self):
		return self._port_status

	@port_status.setter
	def port_status(self, status):
		# 修改port的状态
		self._port_status = status

	@property
	def port_use(self):
		return self._port_use

	@port_use.setter
	def port_use(self, port_change):
		"""
		改变port的连接状态
		"""
		self._port_use = port_change

	@property
	def physic_port(self):
		return self._physic_port
	
	@property
	def wave(self):
		return self._wave
	@wave.setter
	def wave(self, wavelength):
		"""
		端口中的通信波长设置
		"""
		self._wave = wavelength


class OSMOpticalLink(object):
	"""
	定义osm内部的光连接链路
	"""

	def __init__(self, link_num, osm_port1=None, osm_port2=None, wave=None, bandwidth=None):

		self._link_num = link_num # osm链编号

		self.start_port = osm_port1 # 起始结点对象 -- port_type='input'
		self.end_port = osm_port2 # 终结点对象 -- port_type='output'
		self.wave = wave # 链路中通信使用的波长
		self.bandwidth = bandwidth # 设定链路中可用带宽

	@property
	def link_num(self):
		return self._link_num
	
	def has_link(self, osm_port1, osm_port2):
		"""
		检验两结点之间是否存在link
		"""


class OSM(object):
	"""
	建立osm的连接，同时管理
	两个问题考虑：
	1、是否先建立一个连接
	2、还是直接不建立连接，每次请求到来时都新建立连接
	但这会导致一个问题，就是一个rack完全只与另一个rack相连
	还有是否考虑osm是双向还是单向（一进一出）

	# 设计optical端口编号
	# input - 从1 - degree*rack_num
	# output - 从 degree*rack_num+1 -- degree*rack_num*2
	
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
	
		
class WSSPort(object):
	"""
	定义wss的每一个端口的数据结构
	wss的每个port都有相应的 channel plan
	"""
	
	def __init__(self, port_num, port_type='input', slot=None):
		self._port_num = port_num # wss的端口编号
		self._port_type = port_type # 端口类型 'input', 'output'
		self._slot = slot


class WSSOpticalLink(object):
	"""
	wss内部的光连接，主要需要统一设置slot模式
	连接的建立：默认设置的slot范围相同即为相连
	"""


class WSS(object):
	"""
	建立一个wss对象，同时管理wss
	wss编号设置:
	1. 上行wss
	input: 连接bvt 1-M,转接M+1 -- D+M
	output: D+M+1 -- D+D+M

	2.下行wss
	input: 1-D
	output: D+1 - D+M 连接bvt， D+M+1 -- D+M+D 连接上行wss
	"""
	def __init__(self, wss_type='up'):
		self._wss_type = wss_type # wss类型 - 'up'上行wss, 'down'下行wss
		
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
		

class Bvt(object):
	"""
	定义每一个收发机的状态数据结构
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
