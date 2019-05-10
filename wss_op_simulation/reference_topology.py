#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参考拓扑生成文件
"""
import random

def topo(num_node, degree):
	"""
	拓扑生成程序
	"""
	# 生成初始拓扑矩阵
	start_degree = [[None for i in range(num_node)]for j in range(num_node)]
	
	for i in range(num_node):
		temp = list(range(num_node))
		for k in range(i+1, num_node):
			if start_degree[k].count(1) >= degree:
				# 寻找到等于1的节点的位置
				while k in temp:
					temp.remove(k)
		n = i
		
		while n > -1:
			temp.pop(0)
			n -= 1
		find_node = degree - start_degree[i].count(1)
		
		random.shuffle(temp)
		
		if len(temp) >= find_node:
			temp = [temp[i] for i in range(find_node)]
			for j in range(find_node):
				start_degree[i][temp[j]] = 1
				start_degree[temp[j]][i] = 1
				
	return start_degree
				
		
	
	

if __name__ == "__main__":
	print(topo(5,2))
	