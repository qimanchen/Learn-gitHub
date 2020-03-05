#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from logger import Logger
logger = Logger(__name__).Logger

# 事件队列初始化
from event_request import RequestEvent
# 导入初始请求状态
from global_params import START_SIM
# 导入对应的load
from global_params import ERLANG
# 导入总仿真数
from global_params import ALL_SIMULATION_NUM, GET_ONE_SIMULATION_RESULTS
from global_params import SET_SEED_POINT, SEED_POINT
# 导入请求生成库
from request_set import create_all_request
# 导入拓扑生成程序
from topology_wss_op import Topology
# 导入请求处理函数
from event_request import event_handler
# 导入架构大小参数
from wss_osm_para import RACKNUM, BVTNUM, DEGREE, WSSSLOT
from global_params import count_wss_oprator


class Point(object):
	"""
	模拟指针传递参数
	主要为全局参数使用
	如seed
	request的数量使用
	"""
	def __init__(self, value=None):
		self.value = value
class PP(object):
	"""
	主要用于传递整个仿真的测试参数
	"""
	pass


def init_man_queue():
	"""
	初始化事件队列
	:return: 事件初始化队列
	"""
	tmp = RequestEvent()
	tmp.type = START_SIM
	tmp.create_time = 0
	tmp.next = None
	return tmp

def count_resource_state(topology):
	"""
	统计资源的使用情况
	1. cup
	2. 发射机使用情况
	3. 接收机的情况
	4. 带宽资源 -- 当前已建链路的带宽
	5. up_wss 出端口+slot
	6. down_wss 入端口+slot

	# 统计两两连接的rack的对数
	"""
	rack_num = topology.rack_num
	racks = topology.racks
	rack_link = topology.rack_link
	rack_switch_link = topology.rack_switch_link
	link = topology.link
	index_link = topology.index_link

	# cpu
	# 计算资源占比
	sum_cpu = rack_num * racks['1'].computer_resource
	# used_sum_cpu = 0
	avaliable_sum_cpu = 0
	for rack in racks.values():
		# 计算所有剩余计算资源
		avaliable_sum_cpu += rack.avaliable_resource
	used_cpu_rate = (sum_cpu - avaliable_sum_cpu)/sum_cpu
	
	# trans
	sum_trans = rack_num * len(racks['1'].trans_list)
	used_sum_trans = 0
	for rack in racks.values():
		# 计算剩余的trans数量
		used_sum_trans += len(rack.trans_using)
	used_trans_rate = used_sum_trans/sum_trans

	# recv
	sum_recv = rack_num * len(racks['1'].recv_list)
	used_sum_recv = 0
	for rack in racks.values():
		# 计算使用的recv的数量
		used_sum_recv += len(rack.recv_using)
	used_recv_rate = used_sum_recv / sum_recv

	# 记录已经建立的链路的资源使用情况
	sum_exist_bd = 0
	last_bd = 0
	# 主要有两部分
	# 1. 正常链路
	# 2. bypass链路
	for rackLink in rack_link.values():
		sum_exist_bd += rackLink.start_wss_link.bandwidth
		last_bd += rackLink.start_wss_link.bandwidth_avaliable
	for rackLink in rack_switch_link.values():
		sum_exist_bd += rackLink.start_wss_link.bandwidth
		last_db += rackLink.start_wss_link.bandwidth_avaliable

	used_bd_rate = (sum_exist_bd - last_bd) / sum_exist_bd
	
	# 记录每一个rack的端口使用情况
	# 端口使用率
	sum_up_port = len(racks['1'].up_wss.slot_plan) * len(racks['1'].up_wss.out_port)*rack_num
	last_up_port = 0
	sum_down_port = len(racks['1'].down_wss.slot_plan) * len(racks['1'].down_wss.in_port)*rack_num
	last_down_port = 0
	for rack in racks.values():
		# 上行wss统计outprot
		# 下行wss统计inport
		up_wss = rack.up_wss
		down_wss = rack.down_wss
		last_up_port += sum(up_wss.out_port_usenum.values())
		last_down_port += sum(down_wss.in_port_usenum.values())
	used_up_rate = last_up_port / sum_up_port
	used_down_rate = last_down_port/sum_down_port

	return used_cpu_rate, used_trans_rate, used_recv_rate, used_bd_rate, used_up_rate, used_down_rate

def count_wss_port(topology):
	# 统计wss端口使用的情况
	# 分为两种wss
	# 1. 上行wss
	# 2. 下行wss
	# wss内也分为两种接口
	# bypass接口，非bypass接口
	# 特点，上行wss的中间几个端口为bypass端口
	# 下行wss的最后几个端口为bypass端口
	# 数据结构
	# rack_num: {up_wss:上行端口，下行端口，bypass端口,down_wss: 上行端口，下行端口，bypass端口}
	racks = topology.racks
	all_rack_count = RACKNUM
	# 通过遍历整个rack实现

	up_wss_inport_num = [i for i in range(1, BVTNUM+1)]
	up_wss_bypass_num = [i for i in range(BVTNUM+1, BVTNUM+DEGREE+1)]
	up_wss_outport_num = [i for i in range(BVTNUM+DEGREE+1, BVTNUM+DEGREE+DEGREE+1)]

	down_wss_inport_num = [i for i in range(1, DEGREE+1)]
	down_wss_outport_num = [i for i in range(DEGREE+1, BVTNUM+DEGREE+1)]
	down_wss_bypass_num = [i for i in range(BVTNUM+DEGREE+1, BVTNUM+DEGREE+DEGREE+1)]

	rack_upwss_inport = [None for i in range(RACKNUM)]
	rack_upwss_outport = [None for i in range(RACKNUM)]
	rack_upwss_bypass = [None for i in range(RACKNUM)]

	rack_downwss_inport = [None for i in range(RACKNUM)]
	rack_downwss_outport = [None for i in range(RACKNUM)]
	rack_downwss_bypass = [None for i in range(RACKNUM)]

	for rack_num, rack in racks.items():
		rack_num = int(rack_num)
		up_wss = rack.up_wss
		inport, bypass, outport = 0, 0, 0
		for port,count in up_wss.in_port_usenum.items():
			if count != 0 and (port in up_wss_inport_num):
				inport += 1
			elif count != 0 and (port in up_wss_bypass_num):
				bypass += 1
		for port,count in up_wss.out_port_usenum.items():
			if count != 0 and (port in up_wss_outport_num):
				outport += 1
		rack_upwss_inport[rack_num -1] = inport
		rack_upwss_outport[rack_num -1] = outport
		rack_upwss_bypass[rack_num -1] = bypass

		inport, bypass, outport = 0, 0, 0
		down_wss = rack.down_wss
		for port,count in down_wss.in_port_usenum.items():
			if count != 0 and (port in up_wss_inport_num):
				inport += 1
		for port,count in down_wss.out_port_usenum.items():
			if count != 0 and (port in down_wss_outport_num):
				outport += 1
			elif count != 0 and (port in down_wss_bypass_num):
				bypass += 1
		rack_downwss_inport[rack_num -1] = inport
		rack_downwss_outport[rack_num -1] = outport
		rack_downwss_bypass[rack_num -1] = bypass
	return rack_upwss_inport, rack_upwss_outport, rack_upwss_bypass, rack_downwss_inport, rack_downwss_outport,rack_downwss_bypass
				

def count_rack_matchs(topology):
	"""
	统计整个系统中的rack连接对数
	"""
	# 初始系统的rack连接对数
	init_rack_cap_list = [] # ['startRack_EndRack_slot']
	bypass_rack_cap_list = [] # ['startRackf_midRack_endRack_slot']
	# 每个端口可用的次数
	rack_link = topology.rack_link

	for link in rack_link.values():
		start_rack = link.start_rack.rack_num
		end_rack = link.end_rack.rack_num
		slot = link.slot_plan
		if link.link_type == "noSwitch":
			# 只统计rack之间的连接对
			rack_cap = f'{start_rack}_{end_rack}'
			if rack_cap not in init_rack_cap_list:
				init_rack_cap_list.append(rack_cap)
		elif link.link_type == "switch":
			mid_rack = link.mid_rack.rack_num
			rack_cap = f'{start_rack}_{mid_rack}_{end_rack}'
			if rack_cap not in bypass_rack_cap_list:
				bypass_rack_cap_list.append(rack_cap)
		else:
			raise ValueError("链路类型错误")
	# pp.one_rack_cap
	# pp.bypass_rack_cap
	return len(init_rack_cap_list), len(bypass_rack_cap_list)


def main():

	# 物理网络初始化
	topology = Topology()
	# 请求初始化控制

	# 请求中的vnf的数量
	n_point = Point(5)
	# seed用于生成请求
	# set_seed_point = Point(3)
	# set_seed_point = Point(5)
	set_seed_point = Point(SET_SEED_POINT)
	# set_seed_point = Point(3)
	# erlang
	lambda_start = 1/ERLANG
	# 请求的数量
	req_sum = Point(0)
	# seed用于泊松到达控制
	# seed_point = Point(22)
	# seed_point = Point(33)
	seed_point = Point(SEED_POINT)
	# seed_point = Point(44)
	# 控制服务时间的泊松分布
	new_request_time_point = Point(0)
	# 初始化队列
	man_h = init_man_queue()

	# 生成请求，并加入到整个事件队列中
	create_all_request(man_h, lambda_start, set_seed_point, seed_point, new_request_time_point, req_sum, n_point)
	all_test = 0 # 整体测试的数量

	# 测试参数
	# notRecv -- 没有接收机
	# notTrans -- 没有发射机
	# notStartHost -- 发射rack没有host
	# notEndHost -- 接收rack没有host
	# notStartWave -- 发射端没有波长资源
	# notEndWave -- 接收端没有波长资源
	# notWave -- startRack和endrack没有相应的波长资源

	# fail_num = Point(0) # 失败的请求
	# process_request = Point(1) # 处理的请求的数量
	# no_bandwidth_num = Point(0) # 由于没有带宽资源失败的请求的数量
	# no_slot_num = Point(0) # 由于没有slot而请求失败的数量
	# no_cpu = Point(0) # 由于没有计算资源而请求失败
	# 待测试参数

	pp = PP() # 仿真测试参数类
	pp.fail_num = 0 # 失败请求数
	pp.process_request = 0 # 处理的请求数
	pp.no_bandwidth_num = 0 # 由于没有带宽资源失败的请求数

	pp.no_slot_num = 0 # 由于没有slot而失败的请求数
	pp.no_start_slot = 0 # 由于起始端slot而失败
	pp.no_end_slot = 0 # 由于接收端的slot已经用完
	pp.no_trans = 0 # 由于没有发射机

	pp.no_cpu = 0 # 由于没有计算资源而失败的请求数
	pp.switch_wss = 0 # 通过wss转接而实现映射的请求

	# 链路映射成功的种类
	pp.normal = 0 # 不通过任何case的数量
	pp.case1 = 0
	pp.case2 = 0 # 通过case2完成的链路的映射
	pp.case3 = 0
	pp.case4 = 0
	pp.success = 0 # 请求映射成功
	# 通过复用之前的链路
	pp.case_repeat = 0

	# 统计链长
	pp.sc_len = {} # {‘链长’： ‘次数’}

	# 统计rack之间的对数
	# 对应的总的rack连接对数
	all_rack_cap = (DEGREE * RACKNUM)
	# 实时rack对数 -- 数据类型['startRack_EndRack_slot(以startrack的为准)']
	# 通过rack直接相连的对数
	one_rack_cap = 0
	# 通过bypass连接的rack对数
	bypass_rack_cap = 0

	# 统计wss操作次数
	# wss链路建立
	pp.wss_link_create = 0
	# wss链路删除
	pp.wss_link_delete = 0
	# wss同start and end建立的链路
	pp.wss_link_same_rack =0
	# wss上端端口的选择
	# wss同上端端口，slot的选择
	# 操作端口连接
	# 操作slot连接
	# 统计链路是否使用了新的链路
	# 使用了新的链路
	pp.use_new_link = 0
	# 未使用新链路
	pp.not_use_new_link = 0

	case_states = PP()
	case_states.test = [[0 for i in range(6)] for i in range(4)]

	# 对应数据文件文件名格式
	# rack_num,bvt_num,degree,slot,load
	# file_name = "data/test.txt"
	file_name = "data/{}_{}_{}_{}_{}.txt".format(RACKNUM, BVTNUM, DEGREE, WSSSLOT, ERLANG)
	# # 检测文件是否已经存在 -- 直接raise error
	# if os.path.exists(file_name):
	# 	raise FileNotFoundError("当前文件已经建立，禁止程序再次运行")

	file = open(file_name, 'w')
	# 存取相应的设置参数
	file.write(f'Load: {ERLANG}\tDgree: {DEGREE}\tBvtNum: {BVTNUM}\tRacknum: {RACKNUM}\tSlot: {WSSSLOT}')
	file.write('all blocking\tno bandwidth blocking\tno slot blocking\tno cpu blocking\n')
	# 输出测试基本参数
	print(f'Load: {ERLANG}\tDgree: {DEGREE}\tBvtNum: {BVTNUM}\tRacknum: {RACKNUM}\tSlot: {WSSSLOT}')
	rack_upwss_inport, rack_upwss_outport, rack_upwss_bypass, rack_downwss_inport, rack_downwss_outport,rack_downwss_bypass = [None for _ in range(6)]
	count_wss_port_counter = 0 # 统计计数
	# 整体测试的开始
	while True:
		if man_h.next.type == 1:
			# 加入新的请求
			create_all_request(man_h, lambda_start, set_seed_point, seed_point, new_request_time_point, req_sum, n_point)

			all_test += 1
			
			if (all_test % GET_ONE_SIMULATION_RESULTS) == 0:
				
				blocking = pp.fail_num/pp.process_request # 整体阻塞率
				no_bandwidth_num_blocking = pp.no_bandwidth_num/pp.process_request # 没有波长资源而阻塞

				no_slot_num_blocking = pp.no_slot_num/pp.process_request # 没有slot资源而阻塞
				no_start_slot_blocking = pp.no_start_slot/pp.process_request # 没有起始slot
				no_end_slot_blocking = pp.no_end_slot/pp.process_request # 没有截至slot
				no_trans_blocking = pp.no_trans/pp.process_request # 由于没有发射机而阻塞

				no_cpu_blocking = pp.no_cpu/pp.process_request # 没有计算资源而阻塞
				switch_wss = pp.switch_wss/pp.process_request # 通过切换wss映射链的比率

				# 请求处理成功占比
				normal_rate = pp.normal/pp.success
				case1_rate = pp.case1/pp.success
				case2_rate = pp.case2/pp.success
				case3_rate = pp.case3/pp.success
				case4_rate = pp.case4/pp.success
				case_repeat_rate = pp.case_repeat/pp.success
				# 统计系统资源情况
				# used_cpu_rate, used_trans_rate, used_recv_rate, used_bd_rate, used_up_rate, used_down_rate
				system_resource_state = count_resource_state(topology)
				# 统计rack对
				one_rack_cap, bypass_rack_cap = count_rack_matchs(topology)
				one_rack_cap_rate = one_rack_cap/all_rack_cap
				bypass_rack_cap_rate = bypass_rack_cap/all_rack_cap
				
				# 每 10000条请求输出一次结果
				print("all blocking: ", blocking)
				print("no bandwidth blocking: ", no_bandwidth_num_blocking)
				print("no slot blocking: ", no_slot_num_blocking)
				print("no start slot blocking: ", no_start_slot_blocking)
				print("no end slot blocking: ", no_end_slot_blocking)
				print("no trans blocking: ", no_trans_blocking)
				print('no cpu blocking: ', no_cpu_blocking)
				print('switch wss request: ', switch_wss)
				print("request mapping success: ", pp.success)
				print("not case normal: ", pp.normal)
				print("case1 num: ", pp.case1)
				print("case2 num: ", pp.case2)
				print("case3 num: ", pp.case3)
				print("case4 num: ", pp.case4)
				print("case_repeat num: ", pp.case_repeat)
				print(case_states.test)
				print("链长分布:", pp.sc_len)
				print('used_cpu_rate, used_trans_rate, used_recv_rate, used_bd_rate, used_up_rate, used_down_rate', system_resource_state)
				print("one_rack_cap_rate, bypass_rack_cap_rate", one_rack_cap_rate, "  ", bypass_rack_cap_rate)

				print("use_new_link_rack, not_use_new_link_racte", pp.use_new_link/pp.success, pp.not_use_new_link/pp.success)
				print("create_wss_link_num, release_wss_link_num", count_wss_oprator.CREATE_WSS_LINK,count_wss_oprator.RELEASE_WSS_LINK)
				print("*"*50)
				# 将数据读入文件中
				file.write(str(blocking)+'\t'+str(no_bandwidth_num_blocking)+'\t'+
					str(no_slot_num_blocking)+'\t'+ str(no_start_slot_blocking) + '\t' + str(no_end_slot_blocking) + '\t'+
					str(no_trans_blocking)+'\t' + str(no_cpu_blocking)+'\t' + str(switch_wss) + '\t' + str(normal_rate)+\
					'\t'+ str(case1_rate) +'\t' + str(case2_rate) + '\t' + str(case3_rate) + '\t' + str(case4_rate) +\
					'\t' + str(case_repeat_rate)+'\n')
				# 将对应case的统计情况写入
				file.write('noStartPort, noEndPort, noTrans, noRecv, noSameSlot, noRacks'+'\t')
				for caseNum in range(4):
					file.write('_'.join(map(str, case_states.test[caseNum])) + '\t')
				file.write('\n')
				# 将请求链长的分布输入到文件中
				file.write('service distribution:\t')
				for len_sc, value in pp.sc_len.items():
					file.write(str(len_sc)+'\t'+str(value)+'\t')
				file.write('\n')
				# 将资源使用情况写入到文件中
				file.write('used_cpu_rate, used_trans_rate, used_recv_rate, used_bd_rate, used_up_rate, used_down_rate'+'\t\n')
				file.write('\t'.join(map(str, system_resource_state)) + '\t'+'\n')

				#将rack对情况写入到文件中
				file.write("one_rack_cap_rate, bypass_rack_cap_rate"+"\t"+ str(one_rack_cap_rate)+"\t"+str(bypass_rack_cap_rate)+"\n")

				# 将请求是否使用了新建链路存入到文件
				file.write("use_new_link_rack, not_use_new_link_racte"+"\t"+ str(pp.use_new_link/pp.success)+"\t"+str(pp.not_use_new_link/pp.success)+"\n")

				file.write("create_wss_link_num, release_wss_link_num"+"\t"+str(count_wss_oprator.CREATE_WSS_LINK)+"\t"+str(count_wss_oprator.RELEASE_WSS_LINK)+"\n")
			if (all_test == 100):
				count_wss_port_counter += 1
				rack_upwss_inport, rack_upwss_outport, rack_upwss_bypass, rack_downwss_inport, rack_downwss_outport,rack_downwss_bypass = count_wss_port(topology)
			elif all_test != 100 and all_test % 100 == 0:
				count_wss_port_counter += 1
				crack_upwss_inport, crack_upwss_outport, crack_upwss_bypass, crack_downwss_inport, crack_downwss_outport,crack_downwss_bypass = count_wss_port(topology)
				rack_upwss_inport = list(map(sum,zip(rack_upwss_inport, crack_upwss_inport)))
				rack_upwss_outport = list(map(sum,zip(rack_upwss_outport,crack_upwss_outport)))
				rack_upwss_bypass = list(map(sum,zip(rack_upwss_bypass, crack_upwss_bypass)))
				rack_downwss_inport = list(map(sum,zip(rack_downwss_inport, crack_downwss_inport)))
				rack_downwss_outport = list(map(sum,zip(rack_downwss_outport, crack_downwss_outport)))
				rack_downwss_bypass = list(map(sum,zip(rack_downwss_bypass, crack_downwss_bypass)))
			if (all_test == ALL_SIMULATION_NUM):
				# 仿真数量的上限
				blocking = pp.fail_num/pp.process_request # 整体阻塞率
				no_bandwidth_num_blocking = pp.no_bandwidth_num/pp.process_request # 没有波长资源而阻塞
				no_slot_num_blocking = pp.no_slot_num/pp.process_request # 没有slot资源而阻塞
				no_cpu_blocking = pp.no_cpu/pp.process_request # 没有计算资源而阻塞
				switch_wss = pp.switch_wss/pp.process_request # 通过切换wss映射链的比率
				# wss端口统计求平均
				rack_upwss_inport = list(map(lambda x: x/count_wss_port_counter,rack_upwss_inport))
				rack_upwss_outport = list(map(lambda x: x/count_wss_port_counter,rack_upwss_outport))
				rack_upwss_bypass = list(map(lambda x: x/count_wss_port_counter,rack_upwss_bypass))
				rack_downwss_inport = list(map(lambda x: x/count_wss_port_counter,rack_downwss_inport))
				rack_downwss_outport = list(map(lambda x: x/count_wss_port_counter,rack_downwss_outport))
				rack_downwss_bypass = list(map(lambda x: x/count_wss_port_counter,rack_downwss_bypass))
				# 每 10000条请求输出一次结果
				print("all blocking: ", blocking)
				print("no bandwidth blocking: ", no_bandwidth_num_blocking)
				print("no slot blocking: ", no_slot_num_blocking)
				print('no cpu blocking: ', no_cpu_blocking)
				print('switch wss request: ', switch_wss)
				print('rack_upwss____inport: ', *rack_upwss_inport)
				print('rack_upwss___outport: ', *rack_upwss_outport)
				print('rack_upwss____bypass: ', *rack_upwss_bypass)
				print('rack_downwss__inport: ', *rack_downwss_inport)
				print('rack_downwss_outport: ', *rack_downwss_outport)
				print('rack_downwss__bypass: ', *rack_downwss_bypass)
				print("*"*50)
				print()
				# 将数据读入文件中
				file.write(str(blocking)+'\t\t'+str(no_bandwidth_num_blocking)+'\t\t'+
					str(no_slot_num_blocking)+'\t\t' + str(no_cpu_blocking)+'\t\t'+str(switch_wss) + '\n')
				file.write("\t".join(map(str, rack_upwss_inport)) + "\n")
				file.write("\t".join(map(str, rack_upwss_outport)) + "\n")
				file.write("\t".join(map(str, rack_upwss_bypass)) + "\n")
				file.write("\t".join(map(str, rack_downwss_inport)) + "\n")
				file.write("\t".join(map(str, rack_downwss_outport)) + "\n")
				file.write("\t".join(map(str, rack_downwss_bypass)) + "\n")
				break
		# 开始处理请求
		topology = event_handler(topology, man_h, pp, case_states)

	file.close()
	print('*'*50, "测试完成", "*"*50)


if __name__ == "__main__":
	main()
