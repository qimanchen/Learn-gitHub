#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from topology_wss_op import OSM
from topology_wss_op import OSMOpticalLink
    
if __name__ == "__main__":
    osm = OSM()
    osm.create_connect(1,13)
    osm.create_connect(2,14)
    print(osm.optical_link['1'].link_use)
    print(osm.check_connect(1))
    osm.delete_connect(1)
    print(osm.check_connect(1))
    print(osm.link_num)


    
    

            
            
