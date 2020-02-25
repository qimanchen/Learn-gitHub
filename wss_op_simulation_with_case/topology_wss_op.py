#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑生成及操作文件
"""

import os
# 导入设备参数
from wss_osm_para import  OSMSIZE, DEGREE, BVTNUM, RACKNUM, UPWSS, DOWNWSS, WSSSLOT
# 生成参考拓扑文件
from reference_topology import read_topo
from reference_topology import topo
from reference_topology import write_topo
# 初始带宽
from global_params import INIT_BANDWIDTH
# 初始计算资源
from global_params import INIT_COMPUTER_RESOURCE

# 日志记录
from logger import Logger
logger = Logger(__name__).Logger


def create_topology(num_node=RACKNUM, degree=DEGREE):
	"""
	生成osm的拓扑文件
	生成后不在进行更改
	除非在程序运行时动态改变
	"""
	filename = "topo_file/rack{}_degree{}.txt".format(num_node, degree)

	if os.path.exists(filename):
		logger.info("%s 文件已存在，请不要重复建立！" % (filename))
	else:
		# 生成topolist
		topo_list = topo(num_node, degree)
		# 写入文件
		write_topo(topo_list)
	return filename


class OSMPort(object):
	"""
	定义osm的每一个端口的数据结构
	"""
	
	def __init__(self, port_num, port_type='inport', port_status='ENABLE', port_use=False, physic_port=None, optical_port=None):
		self._port_num = port_num # 端口号
		self._port_type = port_type # 端口类型 - input， output
		self.port_status = port_status # 端口的可用状态 -- ENABLE, DISABLED
		self.port_use = port_use # 端口是否已经使用, 'None'表示未使用
		self.optical_port = optical_port # 端口的光连接，input -> output
		self.physic_port = physic_port # 物理连接端口 指定wss的端口号 -- RackPort对象

	@property
	def port_num(self):
		return self._port_num

	@property
	def port_type(self):
		return self._port_type


class OSMOpticalLink(object):
	"""
	定义osm内部的光连接链路
	"""

	def __init__(self, link_num, osm_port1=None, osm_port2=None, link_use=False):

		self._link_num = link_num # osm链编号
		self.start_port = osm_port1 # 起始结点对象 -- port_type='input'
		self.end_port = osm_port2 # 终结点对象 -- port_type='output'
		self.link_use = link_use # 检测该光学连接是否在使用中

		# 当osm光路中仅存在一条链路时使用
		self._bandwidth = INIT_BANDWIDTH # 初始化拥有的带宽资源
		self.bandwidth_use = 0 # 已经使用后的带宽资源

		self.bandwidth_list = None
		self.bandwidth_use_list = None

		# 一条osm的光路可能包含多条wss的光路  -- WSSOpticalLink
		# 带宽以这里面为准
		# 当它为None时，表示该osm两端还没有建立任何通信链路
		# 即表示当link_use = None
		# 只记录对应的start rack 的 up_wss的链路
		# {'start_wss_in_port'_'start_wss_out_port'_slotplan: up_wss WssOpticalLink}
		self.wss_link = None
		# {start_rack_num,mid_rack_num, end_rack_num, start_wss_in_port_num, start_wss_out_port_num, slot_plan: up_wss port}
		self.wss_switch_link = None # 存储相应的多条的链路
		self.mid_link = None # mid rack 到 end rack的中转rack
	
	@property
	def bandwidth(self):
		return self._bandwidth
	
	@property
	def link_num(self):
		return self._link_num


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
		self.in_port_list = {'%s' % i : OSMPort(i, port_type='inport') for i in range(1, osm_size+1)}
		# 初始化osm的output端口
		self.out_port_list = {'%s' % i: OSMPort(i, port_type='outport') for i in range(osm_size+1, osm_size*2+1)}

		# 整体端口的状态
		self._port = {}
		self._port.update(self.in_port_list)
		self._port.update(self.out_port_list)
		# 初始化光连接
		# 端口连接只允许'input' to 'output'
		self._optical_link = {} 
		# 光连接的数量
		self._link_num = 0

	@property
	def in_port(self):
		return self.in_port_list

	@property
	def out_port(self):
		return self.out_port_list

	@property
	def port(self):
		return self._port
	
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
		if str(port_num) not in self.in_port_list and str(port_num) not in self.out_port_list:
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
		建立或修改一个光连接
		建立光连接时需要确认对应的端口是否已经被使用
		"""
		if str(inport_num) not in self.in_port_list:
			raise ValueError('%s-输入端口不存在！' % str(inport_num))
		if str(outport_num) not in self.out_port_list:
			raise ValueError('%s-输出端口不存在！' % str(outport_num))

		# 检测当前端口是否已经被使用
		if self.check_optical_port(self.in_port_list[str(inport_num)]):
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
		self._optical_link[str(inport_num)] = OSMOpticalLink(self._link_num, self.in_port_list[str(inport_num)], self.out_port_list[str(outport_num)])

		# 该变端口的使用状态
		self.in_port_list[str(inport_num)].port_use = True
		# 指定输入端口的连接端口
		self.in_port_list[str(inport_num)].optical_port = self.out_port_list[str(outport_num)]
		self.out_port_list[str(outport_num)].port_use = True
		# 指定输出端口的连接端口
		self.out_port_list[str(outport_num)].optical_port = self.in_port_list[str(inport_num)]

		# 表示链路创建成功
		return True

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
		# 删除端口连接的端口
		self._optical_link[str(inport_num)].start_port.optical_port = None
		self._optical_link[str(inport_num)].end_port.port_use = False
		self._optical_link[str(inport_num)].end_port.optical_port = None
		self._link_num -= 1
		# 删除该条连接
		del self._optical_link[str(inport_num)]

		# 表示链路删除成功
		return True

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
	
	def __init__(self, port_num, rack_num, port_status='ENABLE', port_type='inport', 
		port_use=False, slot=None, wss_type='up', optical_port=None, physic_port=None):

		self._port_num = port_num # wss的端口编号
		self.rack_num = rack_num
		self.port_status = port_status # 端口的状态
		self._port_type = port_type # 端口类型 'inport', 'outport'
		self.port_use = port_use # 端口是否已经使用
		# 当端口中的slot没有被使用时，表示port未被使用

		# 只有'output'端口需要指定分配波长
		# 每个output有一组波长
		# 只要满足相应的端口没有同一个波长即可
		# 主要有两个关键点：
		# 1. 输入端口是否有对应发射机
		# 2. 输出端口是否已经存在相应的波长（slot）
		self.slot_plan = [i for i in range(1, WSSSLOT//4+1)] # 指定端口可用波长范围
		self.slot_num = 0 # 记录当前端口已经使用的次数，对于输入端口(连接发射机和接收机的位置)最多只能使用三次
		# 记录端口已经连接的其他端口以及对应的slot
		self.slot_use = None # {"inport_outport_slotplan": slot_plan}
		self._wss_type = wss_type # 指定wss的类型, 'up', 'down'

		# self.optical_port = optical_port # wss内部的连接，可能存在多个端口连接
		self.physic_port = physic_port # wss连接的物理端口指定osm的端口号

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

	def __init__(self, slot_plan, in_port, out_port, link_use=False):
		# 链路通信使用的slot
		# 链路的端口号可能相同，但slot plan一定是不同的
		# 记录端口的编号
		self.link_id = None # inportnum_outportnum_slotplan: string
		self.slot_plan = slot_plan # slot分配
		# wss内部连接
		# 输入端口
		self.in_port = in_port # port对象
		# 输出端口列表
		self.out_port = out_port # port对象
		# 链路是否在使用
		self.link_use = link_use

		# 当前链路使用的recv or trans
		# 上行wss -- Recv object
		# 下行wss -- Trans object
		self.bvt = None

		# 确定内部可用的带宽
		self._bandwidth = INIT_BANDWIDTH
		self.bandwidth_avaliable = self._bandwidth

	@property
	def bandwidth(self):
		return self._bandwidth


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
	def __init__(self, rack_num, wss_type='up', osm_link_port_size=UPWSS, bvt_link_port_size=DOWNWSS, slot_plan_size=WSSSLOT):

		self._rack_num = rack_num # wss属于的rack编号

		self._wss_type = wss_type # wss类型 - 'up'上行wss, 'down'下行wss

		if self._wss_type == 'down':

			# wss 连接osm端的端口数量
			self.in_port_list_num = osm_link_port_size
			# wss 连接bvt端的端口数量
			self.out_port_list_num = bvt_link_port_size
		else:
			# wss 连接osm端的端口数量
			self.in_port_list_num = bvt_link_port_size
			# wss 连接bvt端的端口数量
			self.out_port_list_num = osm_link_port_size

		# wss支持的整个slot范围
		self._slot_plan = [i for i in range(1, slot_plan_size//4+1)]

		# wss中已经使用的slot，只针对outport
		# N*N的wss考虑的时候
		# 每个输入端口可以输入不同的波长（每个输入有一组波长）
		# 每个输出有一组波长
		# self.slot_plan_use = []

		# wss内部的路由记录
		# up_wss的链路是记录输入端口 {inport_outport_slotplan:link_object}
		# down wss 记录输出端口（大数字输入端口）{outport_inport_slotplan:link_object}
		self.optical_link = {}
		self.in_port_usenum = {} # 输入端口的使用次数 - {port_num: 使用次数}
		self.out_port_usenum = {} # 输出端口使用的次数 - 
		# 端口选用规则，每次选用使用次数最小或没有使用过的端口（负载均衡）

		# 初始化wss的端口
		self.in_port, self.out_port = self.__init_wss_port(self.in_port_list_num, self.out_port_list_num, self._wss_type, self._rack_num)

		# 初始化对应端口的使用次数
		for p in self.in_port.values():
			if p.slot_use is None:
				self.in_port_usenum[p.port_num] = 0
		for p in self.out_port.values():
			if p.slot_use is None:
				self.out_port_usenum[p.port_num] = 0
		# 整体端口的状态
		self._port = {}
		self._port.update(self.in_port)
		self._port.update(self.out_port)

	def check_avaliable_link(self):
		"""
		检测已经建立的链路中可用链路的带宽
		"""
		return [bw.avaliable_resource for bw in self.optical_link.values()]

	@property
	def port(self):
		return self._port
	
	@property
	def rack_num(self):
		return self._rack_num

	@property
	def wss_type(self):
		return self._wss_type

	@property
	def in_port_num(self):
		return self.in_port_list_num

	@property
	def out_port_num(self):
		return self.out_port_list_num
	
	@property
	def slot_plan(self):
		return self._slot_plan
	
	@staticmethod
	def __init_wss_port(in_port_size, out_port_size, wss_type, rack_num):
		"""
		初始化设置wss的端口
		端口号设置：
		inport的端口号小
		outport的端口号大
		"""
		# inport 初始化，上行和下行是不同的
		in_port = {str(i): WSSPort(i, rack_num=rack_num, port_type='inport', wss_type=wss_type) for i in range(1, in_port_size+1)}
		# ouport 初始化
		out_port = {str(i): WSSPort(i, rack_num=rack_num, port_type='outport', wss_type=wss_type) 
		for i in range(in_port_size+1, in_port_size+out_port_size+1)}

		return in_port, out_port

	def check_osm_wss_port(self, port_num):
		"""
		检查osm与wss连接的端口是否还有可用波长
		"""
		if self._port[str(port_num)].slot_num != (WSSSLOT//4):
			# 该端口还可用
			return True
		else:
			# 该端口不可用
			return False

	def find_useable_port(self):
		"""
		找到对应的可用port
		up: 输入端口
		down: 输出端口
		"""
		if self._wss_type == "down":
			# 确定输出端口
			min_num = min(self.out_port_usenum.values())
			if min_num == WSSSLOT//4:
				return False
			for port, num in self.out_port_usenum.items():
				if num == min_num:
					return port
		elif self._wss_type == "up":
			# 确定输入端口
			min_num = min(self.in_port_usenum.values())
			if min_num == WSSSLOT//4:
				return False
			for port, num in self.in_port_usenum.items():
				if num == min_num:
					return port
		else:
			raise ValueError("端口类型错误")

	def chose_slot(self, in_port_num, out_port_num, same_slot=None):
		"""
		same_slot: 已经被使用的slot列表

		确定对应：
		up wss： 输出端口的slot
		down wss： 输入端口的slot
		"""
		in_port = self.in_port[str(in_port_num)]
		out_port = self.out_port[str(out_port_num)]

		# 确定端口已经使用
		in_port_slot_use = None
		if in_port.slot_use:
			in_port_slot_use = in_port.slot_use.values() # 输入端口使用的slot
		out_port_slot_use = None
		if out_port.slot_use:
			out_port_slot_use = out_port.slot_use.values() # 输出端口使用了的slot
		
		for slot in self._slot_plan:
			if same_slot and slot in same_slot.values():
				# 当slot被已经被使用的列表中时，直接跳过
				continue
			if not in_port_slot_use and not out_port_slot_use:
				# 当输入端口和输出端口都没有使用时
				return slot
			if in_port_slot_use and not out_port_slot_use and (slot not in in_port_slot_use):
				# 输入端口已经使用，而输出端口未使用
				return slot
			elif not in_port_slot_use and out_port_slot_use and (slot not in out_port_slot_use):
				# 输入端口未使用，而输出端口已经使用
				return slot
			elif in_port_slot_use and out_port_slot_use and (slot not in in_port_slot_use) and (slot not in out_port_slot_use):
				# 两边的端口都已经使用了
				return slot
		else:
			# 没有可用slot -- 由于没有公共可用的slot
			return False

	def set_connect(self, slot_plan, in_port, out_port):
		"""
		设置上行wss的链路
		上行wss，输入端大于输出端
		输入：
		有M个端口是向下连接bvt
		D个端口向右连接下行wss
		输出：
		D个端口连接上层osm
		:param slot_plan: 使用的slot plan
		"""
		# 确定输入输出端口对象
		inport = self._port[str(in_port)]
		outport = self._port[str(out_port)]

		# 更新端口slot信息
		if not inport.slot_use:
			inport.slot_use = {}
		inport.slot_use[f'{in_port}_{out_port}_{slot_plan}'] = slot_plan
		inport.slot_num += 1
		self.in_port_usenum[in_port] += 1

		if not outport.slot_use:
			outport.slot_use = {}
		outport.slot_use[f'{in_port}_{out_port}_{slot_plan}'] = slot_plan
		outport.slot_num += 1
		self.out_port_usenum[out_port] += 1

		self.optical_link[f'{in_port}_{out_port}_{slot_plan}'] = WSSOpticalLink(slot_plan, inport, outport, link_use=True)

	def delete_connect(self, slot_plan, in_port, out_port):
		"""
		删除wss的链路
		"""
		inport = self._port[str(in_port)]
		if not inport.slot_use:
			raise ValueError("没有建立相应的链路")
		outport = self._port[str(out_port)]
		if not outport.slot_use:
			raise ValueError("没有建立相应的链路")

		# 更新各个结点的slot
		# 输入端口
		del_inport = None
		for port, slot in inport.slot_use.items():
			if f'{in_port}_{out_port}_{slot_plan}' == port:
				del_inport = port
				break
		else:
			raise ValueError("前面建路错误")
		del inport.slot_use[del_inport]
		inport.slot_num -= 1
		self.in_port_usenum[in_port] -= 1

		# 输出端口
		del_outport = None
		for port, slot in outport.slot_use.items():
			if f'{in_port}_{out_port}_{slot_plan}' == port:
				del_outport = port
				break
		else:
			raise ValueError("前面建路错误")
		del outport.slot_use[del_outport]
		outport.slot_num -= 1
		self.out_port_usenum[out_port] -= 1

		# 删除对应的连接
		del self.optical_link[f'{in_port}_{out_port}_{slot_plan}']


class Recv(object):
	"""
	接收机
	"""
	def __init__(self, recv_num, rack= None, recv_wave=None, recv_use=False):
		self._recv_num = recv_num # 接收机编号
		self.recv_wave = recv_wave # 接收机接收波长 # slot_plan
		self.recv_use = recv_use # 接收机使用状态
		self.recv_port = None # 接收机连接下行wss的端口
		self.to_rack =None # 接收机接收信号来源的rack
		self._rack = rack # 接收机所在的rack
		self.host = None # 接收机连接的host

	@property
	def recv_num(self):
		return self._recv_num

	@property
	def rack(self):
		return self._rack
	

class Trans(object):
	"""
	发射机
	"""
	def __init__(self, trans_num, rack=None, trans_wave=None, trans_use=False):
		self._trans_num = trans_num # 发射机的编号
		self._rack = rack # 发射机所在rack
		self.trans_wave = trans_wave # 发射机发射的波长 # slot_plan
		self.trans_use = trans_use # 发射机使用的状态
		self.trans_port = None # 发射机连接的上行wss的port
		self.to_rack = None # 发射机发射波长的目标rack
		self.host = None # 发射机连接的host

	@property
	def trans_num(self):
		return self._trans_num

	@property
	def rack(self):
		return self._rack
	
	
class Host(object):
	"""
	rack 内的host主机
	"""
	def __init__(self, host_num, rack=None, host_use=False):
		self._host_num = host_num # 主机编号
		self._rack = rack # 主机所所属rack
		self.host_use = host_use # 检测主机是否在使用
		self.recv = None # 主机包含的接收机 - 哈希表{recv_num:recv_object}
		self.trans = None # 主机包含的发射机 - 哈希表{trans_num:trans_object}
		# 主机拥有的初始资源
		self._computer_resource = INIT_COMPUTER_RESOURCE
		self.avaliable_resource = self._computer_resource # 主机中的可用资源
		# 通过列表来记录对应的映射的链路
		self.maping_sc = None # 主机中映射的链, 记录vnode表 {vnf:physical_node(rackNum_hostNum)}
		self.maping_vnf = None # 主机中映射的VNF - 哈希表{'start_vnf':end_vnf}
		
	@property
	def computer_resource(self):
		return self._computer_resource
	
	@property
	def host_num(self):
		return self._host_num

	@property
	def rack(self):
		return self._rack
	
	
class Bvt(object):
	"""
	定义每一个收发机的状态数据结构
	每台bvt发射的波长是确定的
	slot的范围是确定的
	"""
	def __init__(self, bvt_num, send_wave=None, recv_wave=None, bvt_use=False):
		self._bvt_num = bvt_num # 收发机的编号
		self.bvt_use = bvt_use # 检测bvt是否已经使用了
		self.send_wave = send_wave # 发射的波长，slot 范围 ex. [1,2,3,4]
		self.recv_wave = recv_wave # 接收的波长，slot 范围 ex. [1,2,3,4]
		self.send_port = None # 发送端连接的wss物理端口
		self.recv_port = None # 接收端连接的wss物理端口

		# 指定收发机的连接的rack
		self.send_to_rack = None # 指定发送到的racki
		self.recv_from_rack = None # 确定接收来自racki的信号
		# self.rack_to = None # 指定连接的rack
		# 初始计算资源
		self._computer_resource = INIT_COMPUTER_RESOURCE
		# # 更新带宽资源
		# self._bandwidth = INIT_BANDWIDTH
		# # 已经使用的带宽
		# self.bandwidth_use = 0
		# 使用了的计算资源
		self.computer_avaliable = self._computer_resource
		# 映射到此的服务链的一个vnf -- 此处记录相应的链表
		self.mapping_sc = None

	@property
	def bvt_num(self):
		return self._bvt_num
	

class RackPort(object):
	"""
	定义rack的结点属性
	"""
	def __init__(self, rack_num, port_type="inport", osm_port=None, wss_port=None, port_use=False):
		# 指定所属rack
		self.rack_num = rack_num
		# 指定端口类型
		self.port_type = port_type
		# 指定连接osm的编号
		self.osm_port = osm_port
		# 指定连接wss的端口
		self.wss_port = wss_port
		# 指定端口是否已经连接到osm，topo初始化时检测使用
		self.port_use = port_use

class RackLink(object):
	"""
	两个rack之间的相连
	"""
	def __init__(self):
		self.link_type = 'noSwitch' # 显示非交换链路
		self.start_rack = None # start_rack # 发射信号的rack
		self.end_rack = None # end_rack # 接收信号的rack
		self.osm_link = None # osm_link # osm中的连接链路
		self.start_wss_link = None # start_up_wss 的连接链路
		self.end_wss_link = None # end_down_wss 的连接链路
		self.trans = None # trans # 发射信号的发射机
		self.recv = None # recv # 接收信号的接收机
		self.slot_plan = None # 链路中的波长

		# self.start_host = None # start rack中的host
		# self.end_host = None # end rack中的host

class RackSwitchLink(object):
	"""
	当rack跨wss对应的链路变化
	rack1 - rack2(只经过wss, 不进入到rack内部) - rack3
	"""
	def __init__(self):
		self.link_type = 'switch' # 交换链路
		self.start_rack = None # start_rack 发射信号的rack
		self.mid_rack = None # 中转的rack（只消耗slot）
		self.end_rack = None # 目标rack

		self.start_mid_osm_link = None # start to mid的osm链接
		self.mid_end_osm_link = None # mid to end的链接

		self.start_wss_link = None # start rack内的wss链接
		self.mid_end_wss_link = None # 进入中转wss链接
		self.mid_start_wss_link = None # 出中转rack wss的链接
		self.end_wss_link = None # 目标rack的wss链接

		self.trans = None # 发射信号的发射机
		self.recv = None # 接收信号的接收机
		self.slot_plan = None # 链路中的波长

class DownUpWssLink(object):
	"""
	下行wss连接上行wss的转接链路
	"""
	def __init__(self, start_port, end_port, link_use=False):
		self.start_port = start_port # 下行wss的端口
		self.end_port = end_port # 上行wss的端口
		self.link_use = link_use # 链路是否已经使用


class Rack(object):
	"""
	初始化每一台Rack，主要设置和管理rack上层wss和bvt的参数
	"""

	def __init__(self, rack_num, bvts=BVTNUM, degrees=DEGREE, osm_size=OSMSIZE):
		# rack编号
		self._rack_num = rack_num
		self.bvt_num = bvts # recv和trans的数量

		# 上行wss
		self.up_wss = WSS(rack_num, wss_type='up')
		# 下行wss
		self.down_wss = WSS(rack_num, wss_type='down')

		# recv 列表
		self.recv_list = {str(i): Recv(i, rack_num) for i in range(1, bvts+1)}
		self.recv_using = {} # 正在使用中的recv
		# trans 列表
		self.trans_list = {str(i): Trans(i, rack_num) for i in range(1, bvts+1)}
		self.trans_using = {} # 正在使用中trans
		
		# host 列表
		self.host_list = {str(i): Host(i, rack_num) for i in range(1, bvts+1)}
		self.host_using = {} # 正在使用中的trans

		# host集合列表
		self._computer_resource = INIT_COMPUTER_RESOURCE * bvts
		self.avaliable_resource = self._computer_resource
		self.mapping_sc = None # {req_id:vnodes列表}

		# # 上行输出端口，osm的输入端口
		self.in_port_list = [i for i in range(degrees*(rack_num-1)+1, degrees*(rack_num)+1)]
		# 下行输入端口，osm的输出端口
		self.out_port_list = [i for i in range(degrees*(rack_num-1)+1+osm_size, degrees*(rack_num)+1+osm_size)]

		# 上行wss的输出端口，rack的输出端口，osm的输入端口
		self._out_port = {str(i): RackPort(self._rack_num, port_type='inport', osm_port=i) 
		for i in self.in_port_list}

		# 上行wss的输入端口，rack的输入端口，osm的输出端口
		self._in_port = {str(i): RackPort(self._rack_num, port_type='outport', osm_port=i) 
		for i in self.out_port_list}

		# 记录转接链路 -- 下行wss转接到上行wss上去
		# 测试链路转接使用
		self.down_up_link = {}
		# {end_wss_port: DownUpWssLink}
		self.down_up_link_using = {} # 记录使用了的链

		# rack的输入输出端口记录，主要是对wss端口的一个索引
		# self._in_port = {}
		# self._out_port = {}

		self.set_link_osm() # 设置wss与osm的物理连接
		# 对应的recv任意使用，同一端口可以使用多个端口
		# self.set_link_bvt() # 设置wss与recv和trans的物理连接
		self.set_up_down() # 设置上行wss与下行wss的连接

	@property
	def computer_resource(self):
		return self._computer_resource
	
	def get_avaliable_host(self):
		"""
		检测没有使用过的host
		"""
		for i in self.host_list:
			if i not in self.host_using:
				return self.host_list[i]
		else:
			# 没有可用host
			return None

	def get_avaliable_switch_link(self):
		"""
		获取对应的wss切换的链路
		"""
		for i in self.down_up_link:
			if i not in self.down_up_link_using:
				return self.down_up_link[i]
		else:
			# 没有可以切换的链路
			return None

	def get_avaliable_trans(self):
		"""
		获取可用发射机 -- 未使用的
		"""
		for i in self.trans_list:
			if i not in self.trans_using:
				return self.trans_list[i]
		else:
			# 没有可用发射机
			return None

	def get_avaliable_recv(self):
		"""
		获取可用接收机 -- 未使用的
		"""
		for i in self.recv_list:
			if i not in self.recv_using:
				return self.recv_list[i]
		else:
			# 没有可用接收机
			return None

	@property
	def rack_num(self):
		return self._rack_num

	@property
	def in_port(self):
		return self._in_port
	
	@property
	def out_port(self):
		return self._out_port

	# 建立相应的物理连接
	def set_link_osm(self):
		"""
		设置连接到osm的端口
		上行wss的输出端口连接的是osm
		下行wss的输入端口连接的是osm
		连接的是osm对应的端口号
		"""
		count = 0
		# 连接上行wss
		for i in self.up_wss.out_port:
			# 上行wss的输出连接着osm的输入
			# osm的端口号
			self.up_wss.out_port[i].physic_port = self.in_port_list[count]
			# rack输出端对应着上行wss的输出
			self._out_port[str(self.in_port_list[count])].wss_port = self.up_wss.out_port[i]
			count += 1

		# 连接下行wss
		count = 0
		for i in self.down_wss.in_port:
			self.down_wss.in_port[i].physic_port = self.out_port_list[count]
			# rack输入端对应着下行wss的输入
			self._in_port[str(self.out_port_list[count])].wss_port = self.down_wss.in_port[i]
			count += 1

	def set_link_bvt(self):
		"""
		设置连接到bvt
		上行wss的输入端口连接的是recv
		下行wss的输出端口连接的是trans
		连接的是对应的recv
		"""
		count = 0
		bvt_num_list = [str(i) for i in range(1, self.bvt_num+1)]
		# 连接上行wss
		for i in self.up_wss.in_port:
			
			self.up_wss.in_port[i].physic_port = self.trans_list[bvt_num_list[count]]
			# 收发机的发送端对应着上行wss的输入
			self.trans_list[bvt_num_list[count]].trans_port = self.up_wss.in_port[i]
			# 若达到bvt数则退出，其余接口为wss之间的连接
			count += 1
			if count == self.bvt_num:
				break
		# 连接下行wss
		count = 0
		for i in self.down_wss.out_port:
			self.down_wss.out_port[i].physic_port = self.recv_list[bvt_num_list[count]]
			# 收发机的接收端对应着wss的输出
			self.recv_list[bvt_num_list[count]].recv_port = self.down_wss.out_port[i]
			count += 1
			if count == self.bvt_num:
				break

	def set_up_down(self):
		"""
		设置上行wss与下行wss的物理连接
		"""
		up_wssin_port_list = [i for i in self.up_wss.in_port] # 上行wss的输入端口的编号
		down_wssout_port_list = [i for i in self.down_wss.out_port] # 下行wss的输出端口的编号

		for i in self.up_wss.in_port:
			if int(i) > self.bvt_num:
				self.up_wss.in_port[i].physic_port = self.down_wss.out_port[down_wssout_port_list[int(i)-1]]
				self.down_wss.out_port[down_wssout_port_list[int(i)-1]].physic_port = self.up_wss.in_port[i]
				self.down_up_link[str(self.down_wss.out_port[down_wssout_port_list[int(i)-1]].port_num)] = DownUpWssLink(
					self.down_wss.out_port[down_wssout_port_list[int(i)-1]],self.up_wss.in_port[i])

	
class Topology(object):
	"""
	该类主要是拓扑文件的生成，及拓扑的一个改变
	
	# 变换主要有两部分：
		1、光开关内部连接的变化
		2、wss内部的变化
	# bvt与wss的连接为硬连接
	# wss与光开关的连接为硬链接
	"""
	
	def __init__(self, topo_file=None, rack_num=RACKNUM):
		# 初始参数
		self.rack_num = rack_num
		# 初始化osm
		self.osm = OSM()
		# 初始化rack，多个rack初始化
		self.racks = {str(i): Rack(i) for i in range(1, self.rack_num+1)}

		# 记录rack之间完整链路的信息
		# {'start_rack_num'_'end_rack_num'_'osm_in_put'_'out_put': RackLink}
		# 注意之里面存在着link type
		self.rack_link = {} # 结构建RackLink
		self.rack_switch_link = {} # 交换链路

		# 拓扑文件名
		self.topo_file = topo_file
		# 记录rack之间的链（osm之间的链）
		self.link = {} #{'rack_num':[osm.optical_link object, 'None']}
		# 注意修改链路后对应的[[同一个rack对应着多条链路]]
		# 提供链路的索引 -- 与拓扑文件一致 但只记录连接的结点
		self.index_link = [] #[[] -- rack1 连接的结点]
		# osm内部的光链路初始化，以及取得整个链路表
		self.topo_list = self.read_topo_file()

	def set_wss_link():
		"""
		提前设置wss链路
		"""

	def get_link_rack_bandwidth_count(self, rack_num):
		"""
		获取某个rack与其他rack相连的带宽和
		"""
		# 防止keyerror
		if isinstance(rack_num, int):
			rack_num = str(rack_num)

		bandwidth_sum = 0 # 带宽和

		for rack_link in self.link[rack_num]:
			if rack_link != "None":
				# 注意减去已经使用了的带宽
				bandwidth_sum += (rack_link.bandwidth-rack_link.bandwidth_use)
		return bandwidth_sum

	def get_rack_osm_port(self, rack_num, port_type):
		"""
		取得rack连接osm的端口
		"""
		if port_type == 'inport':
			for i in self.racks[str(rack_num)].in_port:
				if not self.racks[str(rack_num)].in_port[i].port_use:
					return i
		elif port_type == 'outport':
			for i in self.racks[str(rack_num)].out_port:
				if not self.racks[str(rack_num)].out_port[i].port_use:
					return i
		else:
			raise ValueError('端口类型错误！')

	def read_topo_file(self):
		"""
		读取topology文件，初始化osm内部的光连接

		topology.link[str(rack_i)][rack_j] --> rack_i 与rack_j的连接光路 -- OSMOpticalLink
		topology.link[str(rack_i)][rack_j].strat_port --> OSMPort
		topology.link[str(rack_i)][rack_j].strat_port.physical_port --> RackPort
		topology.link[str(rack_i)][rack_j].start_port.physical_port.wss_port --> WSSPort
		topology.link[str(rack_i)][rack_j].start_port.physical_port.wss_port.physical_port --> BvtPort num/ osm port_num
		"""
		# 读取osm topology文件
		if self.topo_file is None:
			# 当拓扑文件不存在时
			self.topo_file = create_topology()

		rack_topo = read_topo(self.topo_file)
		for i in rack_topo:
			self.link.setdefault(i,[])
		# rack_topo -- {'rack_num':['None'--为连接该rack, '2'-- 连接到rack 2]}
		for i in rack_topo:
			# 添加每个rack连接的rack num，方便查询
			self.index_link.append([])
			for rack_num in rack_topo[i]:
				# 两rack之间存在连接
				if rack_num != 'None':
					# 记录与rack i 连接的rack的编号
					self.index_link[-1].append(int(rack_num))
					# osm输入端口 - str
					osm_rack_in_port = self.get_rack_osm_port(i, 'outport')
					# osm输出端口 - str
					osm_rack_out_port = self.get_rack_osm_port(rack_num, 'inport')
					# 建立连接
					# 连接端口
					# 设置osm连接到rack
					# osm的输入端口
					self.osm.port[osm_rack_in_port].physic_port = self.racks[i].out_port[str(osm_rack_in_port)]
					# 更新rack连接osm的端口
					self.racks[i].out_port[str(osm_rack_in_port)].osm_port = self.osm.port[osm_rack_in_port]
					self.racks[i].out_port[str(osm_rack_in_port)].port_use = True

					# osm的输出端口
					self.osm.port[osm_rack_out_port].physic_port = self.racks[rack_num].in_port[str(osm_rack_out_port)]
					self.racks[rack_num].in_port[str(osm_rack_out_port)].osm_port = self.osm.port[osm_rack_out_port]
					self.racks[rack_num].in_port[str(osm_rack_out_port)].port_use = True
					# osm内部的光连接
					self.osm.create_connect(osm_rack_in_port, osm_rack_out_port)

					# 表示rack i 与rack_num 有连接
					self.link[i].append(self.osm.optical_link[osm_rack_in_port])
				else:
					# 表示rack i 与 rack_num 无连接
					self.link[i].append('None')
		return rack_topo
		
