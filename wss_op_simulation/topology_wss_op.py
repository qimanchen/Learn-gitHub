#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑生成及操作文件
"""
# 导入设备参数
from wss_osm_para import  OSMSIZE, DEGREE, BVTNUM, RACKNUM, UPWSS, DOWNWSS, WSSSLOT
from reference_topology import read_topo


class OSMPort(object):
	"""
	定义osm的每一个端口的数据结构
	"""
	
	def __init__(self, port_num, port_type='input', port_status='ENABLE', port_use=False, physic_port=None, optical_port=None):
		self._port_num = port_num # 端口号
		self._port_type = port_type # 端口类型 - input， output
		self.port_status = port_status # 端口的可用状态 -- ENABLE, DISABLED
		self.port_use = port_use # 端口是否已经使用, 'None'表示未使用
		self.optical_port = optical_port # 端口的光连接，input -> output
		self._physic_port = physic_port # 物理连接端口

	@property
	def port_num(self):
		return self._port_num

	@property
	def port_type(self):
		return self._port_type

	@property
	def physic_port(self):
		return self._physic_port
	


class OSMOpticalLink(object):
	"""
	定义osm内部的光连接链路
	"""

	def __init__(self, link_num, osm_port1=None, osm_port2=None, link_use=False):

		self._link_num = link_num # osm链编号
		self.start_port = osm_port1 # 起始结点对象 -- port_type='input'
		self.end_port = osm_port2 # 终结点对象 -- port_type='output'
		self.link_use = link_use # 检测该光学连接是否在使用中
	
	@property
	def link_num(self):
		return self._link_num
	
	def has_link(self, osm_port1, osm_port2):
		"""
		检验两结点之间是否存在link
		"""
		pass


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
	def __init__(self, osm_size=OSMSIZE):
		# 初始化osm数据结构模型

		# osm的大小为osm_size*osm_size
		self._osm_size = osm_size
		# 初始化osm的input端口
		self._in_port = {'%s' % i : OSMPort(i, port_type='input') for i in range(1, osm_size+1)}
		# 初始化osm的output端口
		self._out_port = {'%s' % i: OSMPort(i, port_type='output') for i in range(osm_size+1, osm_size*2+1)}
		# 初始化光连接
		# 端口连接只允许'input' to 'output'
		self._optical_link = {} 
		# 光连接的数量
		self._link_num = 0

	@property
	def in_port(self):
		return self._in_port

	@property
	def out_port(self):
		return self._out_port

	@property
	def optical_link(self):
		return self._optical_link

	@property
	def link_num(self):
		return self._link_num
	

	def check_port(self, port_num):
		"""
		检测某个端口是否存在
		"""
		if str(port_num) not in self._in_port and str(port_num) not in self._out_port:
			raise ValueError('%s-端口不存在！' % str(port_num))
		return True

	def check_optical_port(self, port_object):
		"""
		检测一个端口是否已经建立了光连接
		"""
		return port_object.port_use

	def check_link_use(self, link_object):
		"""
		检测已经建立的光连接是否还在使用
		"""
		return link_object.link_use
	
	def create_connect(self, inport_num, outport_num):
		"""
		建立一个光连接
		"""
		if str(inport_num) not in self._in_port:
			raise ValueError('%s-输入端口不存在！' % str(inport_num))
		if str(outport_num) not in self._out_port:
			raise ValueError('%s-输出端口不存在！' % str(outport_num))

		# 检测当前端口是否已经被使用
		if self.check_optical_port(self._in_port[str(inport_num)]):
			# 当被使用时，检测是否在使用中
			if str(inport_num) in self._optical_link:
				if self.check_link_use(self._optical_link[str(inport_num)]):
					# 检测到在使用中
					raise ValueError('建立的光路还在使用，禁止修改连接！')
				else:
					# 删除已经存在的链路
					self.delete_connect(inport_num)

		# 链的计数加一
		self._link_num += 1

		# 建立新的光路
		self._optical_link[str(inport_num)] = OSMOpticalLink(self._link_num, self._in_port[str(inport_num)], self._out_port[str(outport_num)])

		# 该变端口的使用状态
		self._in_port[str(inport_num)].port_use = True
		self._out_port[str(outport_num)].port_use = True


	def delete_connect(self, inport_num):
		"""
		删除一个光连接
		"""
		if str(inport_num) not in self._optical_link:
			raise ValueError('该端口的连接不存在')

		if self.check_link_use(self._optical_link[str(inport_num)]):
			raise ValueError('建立的光路还在使用，禁止删除连接！')
		# 修改端口使用状态
		self._optical_link[str(inport_num)].start_port.port_use = False
		self._optical_link[str(inport_num)].end_port.port_use = False
		self._link_num -= 1
		# 删除该条连接
		del self._optical_link[str(inport_num)]


	def check_connect(self, inport_num):
		"""
		检测某个光连接是否存在
		"""
		if str(inport_num) in self._optical_link:
			return True
		return False
	
		
class WSSPort(object):
	"""
	定义wss的每一个端口的数据结构
	wss的每个port都有相应的 channel plan
	# 假设每隔
	"""
	
	def __init__(self, port_num, port_type='input', port_use=False, slot=None, wss_type='up'):
		self._port_num = port_num # wss的端口编号
		# 只有'output'端口可以分配波长
		self._port_type = port_type # 端口类型 'input', 'output'
		self.port_use = port_use # 端口是否已经使用
		self.slot = slot # 指定端口的波长范围
		self._wss_type = wss_type # 指定wss的类型, 'up', 'down'
		self.physic_port = physic_port # wss连接的物理端口

	@property
	def port_num(self):
		return self._port_num

	@property
	def port_type(self):
		return self._port_type

	@property
	def wss_type(self):
		return self._wss_type


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

	def __init__(self, bvt_num, in_port, out_port):
		self._bvt_num = bvt_num # 收发机的编号
		self._in_port = in_port # 收发机的输入端口
		self._out_port = out_port # 收发机的输出端口
	
	
class Topology(object):
	"""
	该类主要是拓扑文件的生成，及拓扑的一个改变
	
	# 变换主要有两部分：
		1、光开关内部连接的变化
		2、wss内部的变化
	# bvt与wss的连接为硬连接
	# wss与光开关的连接为硬链接
	"""
	
	def __init__(self, topo_file,):
		self.topo_file = topo_file

		# 建立物理连接

		# 初始化光路连接

		# 设置osm的光路连接
		rack_topo = read_topo(self.topo_file)
		
	
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
# 整体拓扑的读取

# 选择结点

# 选择路径
# 1. 确定osm通路
#    1. 确定rack的连接端口
#    2. 确定wss的连接端口
#    3. 确定rack的输出端口
#    4. 确定wss的输入端口
#    5. 确定wss的传输波长
# 2. 确定wss通路
