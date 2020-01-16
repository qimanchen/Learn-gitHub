#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-08-20 10:00:10
# @Author  : Qiman Chen
# @Version : $Id$

"""
测试输出文件格式化数据
主要用来对多

"""

def print_format_data():
	outfile = open("data/test_file_out.txt", 'w')
	with open("data/test_file.txt", 'r') as f:
		data = f.readline()
		while data != "":
			data.strip('\r\n')
			print(*data.split('_'), sep="\t", file=outfile, end="\n")
			data = f.readline()
	outfile.close()

def caculate_data():
	"""
	计算平均数
	"""
	outfile = open("data/cacu_file.txt", "w")

	with open("data/cacu.txt", "r") as f:
		count = 0
		while True:
			line1 = []
			line2 = []
			line3 = []

			for _ in range(6):
				data = f.readline()
				dataList = list(map(float,data.split()))
				line1.append(dataList)
			f.readline()
			for _ in range(6):
				data = f.readline()
				dataList = list(map(float,data.split()))
				line2.append(dataList)
			f.readline()
			for _ in range(6):
				data = f.readline()
				dataList = list(map(float,data.split()))
				line3.append(dataList)

			line = list(zip(line1,line2, line3))
			lines = [list(zip(*mid)) for mid in line]

			results = []
			for mid in lines:
				results.append([])
				for mid_in in mid:
					results[-1].append(sum(mid_in)/3)
			for mid in results:
				outfile.write("\t".join(map(str,mid)) + "\n")
			outfile.write("\n\n")
			f.readline()
			data = f.readline()
			print(data)
			if data != "a\n":
				break

		outfile.write("\n *************************\n")
	outfile.close()


def get_port_average_port():
	"""
	计算平均端口数
	"""
	outfile = open('data/ave_port.txt', 'w')

	with open('data/ports.txt', 'r') as f:

		count = 0
		while True:
			data = f.readline()
			if data == "":
				return
			datas = sum(map(float, data.split()))
			aveData = datas / 32
			outfile.write(f'{datas}\t{aveData}\n' )
			for _ in range(5):
				data = f.readline()
				datas = sum(map(float, data.split()))
				aveData = datas / 32
				outfile.write(f'{datas}\t{aveData}\n' )
			data = f.readline()
			outfile.write("\n")
			count += 1
			if count == 6:
				outfile.write("\n***********************\n")
				count = 0
	print("Success!")


if __name__ == "__main__":
	caculate_data()
