#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from topology_wss_op import WSS


class PP(object):
	"""
	主要用于传递整个仿真的测试参数
	"""
	pass

class Test(object):
	
	def __init__(self):
		self.value = 10

def test_test(a):
	d = a
	d.value += 10
	return d
	
if __name__ == "__main__":
	
	wss = WSS(1)

	port = wss.find_useable_port()
	slot = wss.chose_slot(port, 21)

	wss.set_connect(slot, port, 21)

	port = wss.find_useable_port()
	slot = wss.chose_slot(port, 21)
	wss.set_connect(slot, port, 21)
	
	print(wss.check_osm_wss_port(21))
	print(wss.optical_link)






