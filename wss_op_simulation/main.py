#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from logger import Logger
logger = Logger(__name__).Logger

# 事件队列初始化
from event_request import RequestEvent
# 导入初始请求状态
from global_params import START_SIM
# 导入请求生成库
from request_set import create_all_request
# 导入拓扑生成程序
from topology_wss_op import Topology
# 导入请求处理函数
from event_request import event_handler


class Point(object):
	"""
	模拟指针传递参数
	主要为全局参数使用
	如seed
	request的数量使用
	"""
	def __init__(self, value=None):
		self.value = value

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
	lambda_start = 1/180
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
	all_test = 1 # 整体测试的数量

	# 测试参数
	# notRecv -- 没有接收机
	# notTrans -- 没有发射机
	# notStartHost -- 发射rack没有host
	# notEndHost -- 接收rack没有host
	# notStartWave -- 发射端没有波长资源
	# notEndWave -- 接收端没有波长资源
	# notWave -- startRack和endrack没有相应的波长资源
	fail_num = Point(0) # 失败的请求
	process_request = Point(1) # 处理的请求的数量
	no_bandwidth_num = Point(0) # 由于没有带宽资源失败的请求的数量
	no_slot_num = Point(0) # 由于没有slot而请求失败的数量
	no_cpu = Point(0) # 由于没有计算资源而请求失败

	file_name = "data/test.txt"
	file = open(file_name, 'w')
	file.write('all blocking\t\tno bandwidth blocking\t\tno slot blocking\t\tno cpu blocking\n')
	# 整体测试的开始
	while True:
		if man_h.next.type == 1:
			# 加入新的请求
			create_all_request(man_h, lambda_start, set_seed_point, seed_point, new_request_time_point, req_sum, n_point)

			all_test += 1

			if (all_test % 10) == 0:
				blocking = fail_num.value/process_request.value # 整体阻塞率
				no_bandwidth_num_blocking = no_bandwidth_num.value/process_request.value # 没有波长资源而阻塞
				no_slot_num_blocking = no_slot_num.value/process_request.value # 没有slot资源而阻塞
				no_cpu_blocking = no_cpu.value/process_request.value # 没有计算资源而阻塞
				# 每 10000条请求输出一次结果
				print("all blocking: ", blocking)
				print("no bandwidth blocking: ", no_bandwidth_num_blocking)
				print("no slot blocking: ", no_slot_num_blocking)
				print('no cpu blocking: ', no_cpu_blocking)
				print("*"*50)
				print()
				# 将数据读入文件中
				file.write(str(blocking)+'\t\t'+str(no_bandwidth_num_blocking)+'\t\t'+
					str(no_slot_num_blocking)+'\t\t' + str(no_cpu_blocking)+'\n')

			if (all_test == 100):
				# 仿真数量的上限
				blocking = fail_num.value/process_request.value # 整体阻塞率
				no_bandwidth_num_blocking = no_bandwidth_num.value/process_request.value # 没有波长资源而阻塞
				no_slot_num_blocking = no_slot_num.value/process_request.value # 没有slot资源而阻塞
				no_cpu_blocking = no_cpu.value/process_request.value # 没有计算资源而阻塞
				# 输出最后一次的结果
				print("all blocking: ", blocking)
				print("no bandwidth blocking: ", no_bandwidth_num_blocking)
				print("no slot blocking: ", no_slot_num_blocking)
				print('no cpu blocking: ', no_cpu_blocking)
				# 将最后一次结果读入文件中
				file.write(str(blocking)+'\t\t'+str(no_bandwidth_num_blocking)+'\t\t'+
					str(no_slot_num_blocking)+'\t\t' + str(no_cpu_blocking)+'\n')
				break
		# 开始处理请求
		event_handler()

	file.close()
	print('*'*50, "测试完成", "*"*50)


if __name__ == "__main__":
	main()
