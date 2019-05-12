#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
设置设备的主要参数：
osm大小
degree
bvt数量
rack数量
"""


# 上层的连接度
DEGREE = 5
# 每一台rack的收发机的数量
BVTNUM = 4
# 系统中rack的数量
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
