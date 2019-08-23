#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-08-20 10:00:10
# @Author  : Qiman Chen
# @Version : $Id$

"""
测试输出文件格式化数据

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

if __name__ == "__main__":
	print_format_data()
