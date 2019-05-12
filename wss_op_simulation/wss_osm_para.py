#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
设置设备的主要参数：
osm大小
degree
bvt数量
rack数量
"""
"""
两种参考参数：
N = 64, D=6, M=16, S=48

M and S:
M=16, S=128
M=20, S=48

对于通过多个wss的设备需要考虑：
调制格式4QAM，4dB
40G -- 3,4,4 -- one slot 6.25GHZ
100G -- 8,8,10 
分别对应 one-, two-, three-hop
"""


# 上层的连接度
# 参考范围 4 to 8
DEGREE = 5

# 每一台rack的收发机的数量
# 参考范围 16 to 48
BVTNUM = 4

# 系统中rack的数量
# 参考范围32 to 96
RACKNUM = 6

# Wss的大小
# 上行端口数
UPWSS = DEGREE
# 下行端口数
DOWNWSS = DEGREE + BVTNUM
# 光开关的大小
OSMSIZE = DEGREE * RACKNUM
# wss中slot的数量
WSSSLOT = 48
