#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参考拓扑生成文件
"""
import random
from wss_osm_para import DEGREE, RACKNUM


def topo(num_node, degree):
	"""
	拓扑生成程序
	:params num_node: rack的数量
	:params degree: 每台rack的连接度
	:return: 拓扑数组 -- 一个二维数组
	"""
	# 生成初始拓扑矩阵
	start_degree = [[None]*num_node]*num_node
	
	for i in range(num_node):
		temp = list(range(num_node))
		for k in range(i+1, num_node):
			if start_degree[k].count(1) >= degree:
				# 寻找到等于1的节点的位置
				while k in temp:
					temp.remove(k)
		n = i
		
		while n > -1:
			# 删除前面已经对比过的结点
			temp.pop(0)
			n -= 1
		# 确定需要对比的结点
		find_node = degree - start_degree[i].count(1)
		
		# 将temp中的元素随机排列
		random.shuffle(temp)
		
		if len(temp) >= find_node:
			temp = [temp[i] for i in range(find_node)]
			for j in range(find_node):
				start_degree[i][temp[j]] = 1
				start_degree[temp[j]][i] = 1
				
	return start_degree


def write_topo(start_degree):
	"""
	写入拓扑文件
	:params start_degree: 拓扑的二维数组
	"""

	filename = "topo_file\\rack{}_degree{}.txt".format(RACKNUM, DEGREE)

	with open(filename, 'w') as f:
		for i in range(len(start_degree)):
			# 读入某个rack当前连接的rack
			f.write(str(i+1)+'\t')
			for j in range(len(start_degree[i])):
				# 读取Racki 连接的Rack
				if start_degree[i][j] != None:
					f.write(str(j+1)+'\t')
				else:
					f.write(str(start_degree[i][j]) + '\t')
			f.write('\n')

def read_topo(file_name):
	"""
	读取拓扑文件
	:params file_name: 指定的拓扑的文件名
	"""

				
		
if __name__ == "__main__":
	topo_list = topo(RACKNUM, DEGREE)
	print(topo_list)
	# write_topo(topo_list)



	