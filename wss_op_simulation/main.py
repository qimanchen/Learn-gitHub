#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from logger import Logger
logger = Logger(__name__).Logger

# 事件队列初始化
from event_request import RequestEvent
# 导入初始请求状态
from global_params import START_SIM
# 导入对应的load
from global_params import ERLANG
# 导入请求生成库
from request_set import create_all_request
# 导入拓扑生成程序
from topology_wss_op import Topology
# 导入请求处理函数
from event_request import event_handler
# 导入架构大小参数
from wss_osm_para import RACKNUM, BVTNUM, DEGREE, WSSSLOT


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

def main():

	# 物理网络初始化
	topology = Topology()
	# 请求初始化控制

	# 请求中的vnf的数量
	n_point = Point(5)
	# seed用于生成请求
	set_seed_point = Point(3)
	# erlang
	lambda_start = 1/ERLANG
	# 请求的数量
	req_sum = Point(0)
	# seed用于泊松到达控制
	seed_point = Point(22)
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

	# 对应数据文件文件名格式
	# rack_num,bvt_num,degree,slot,load
	file_name = "data/test.txt"
	# file_name = "data/{}_{}_{}_{}_{}.txt".format(RACKNUM, BVTNUM, DEGREE, WSSSLOT, ERLANG)
	file = open(file_name, 'w')
	file.write('all blocking\t\tno bandwidth blocking\t\tno slot blocking\t\tno cpu blocking\n')
	print("Load: ", ERLANG)
	# 整体测试的开始
	while True:
		if man_h.next.type == 1:
			# 加入新的请求
			create_all_request(man_h, lambda_start, set_seed_point, seed_point, new_request_time_point, req_sum, n_point)

			all_test += 1
			
			if (all_test % 10000) == 0:
				blocking = pp.fail_num/pp.process_request # 整体阻塞率
				no_bandwidth_num_blocking = pp.no_bandwidth_num/pp.process_request # 没有波长资源而阻塞

				no_slot_num_blocking = pp.no_slot_num/pp.process_request # 没有slot资源而阻塞
				no_start_slot_blocking = pp.no_start_slot/pp.process_request # 没有起始slot
				no_end_slot_blocking = pp.no_end_slot/pp.process_request # 没有截至slot
				no_trans_blocking = pp.no_trans/pp.process_request # 由于没有发射机而阻塞

				no_cpu_blocking = pp.no_cpu/pp.process_request # 没有计算资源而阻塞
				switch_wss = pp.switch_wss/pp.process_request # 通过切换wss映射链的比率
				# 每 10000条请求输出一次结果
				print("all blocking: ", blocking)
				print("no bandwidth blocking: ", no_bandwidth_num_blocking)
				print("no slot blocking: ", no_slot_num_blocking)
				print("no start slot blocking: ", no_start_slot_blocking)
				print("no end slot blocking: ", no_end_slot_blocking)
				print("no trans blocking: ", no_trans_blocking)
				print('no cpu blocking: ', no_cpu_blocking)
				print('switch wss request: ', switch_wss)
				print("*"*50)
				print()
				# 将数据读入文件中
				file.write(str(blocking)+'\t\t'+str(no_bandwidth_num_blocking)+'\t\t'+
					str(no_slot_num_blocking)+'\t\t'+ str(no_start_slot_blocking) + '\t\t' + str(no_end_slot_blocking) + '\t\t'+
					str(no_trans_blocking)+'\t\t' + str(no_cpu_blocking)+'\t\t' + str(switch_wss) + '\n')

			if (all_test == 100000):
				# 仿真数量的上限
				blocking = pp.fail_num/pp.process_request # 整体阻塞率
				no_bandwidth_num_blocking = pp.no_bandwidth_num/pp.process_request # 没有波长资源而阻塞
				no_slot_num_blocking = pp.no_slot_num/pp.process_request # 没有slot资源而阻塞
				no_cpu_blocking = pp.no_cpu/pp.process_request # 没有计算资源而阻塞
				switch_wss = pp.switch_wss/pp.process_request # 通过切换wss映射链的比率
				# 每 10000条请求输出一次结果
				print("all blocking: ", blocking)
				print("no bandwidth blocking: ", no_bandwidth_num_blocking)
				print("no slot blocking: ", no_slot_num_blocking)
				print('no cpu blocking: ', no_cpu_blocking)
				print('switch wss request: ', switch_wss)
				print("*"*50)
				print()
				# 将数据读入文件中
				file.write(str(blocking)+'\t\t'+str(no_bandwidth_num_blocking)+'\t\t'+
					str(no_slot_num_blocking)+'\t\t' + str(no_cpu_blocking)+'\t\t'+str(switch_wss) + '\n')
				break
		# 开始处理请求
		event_handler(topology, man_h, pp)

	file.close()
	print('*'*50, "测试完成", "*"*50)


if __name__ == "__main__":
	main()
