#!/usr/bin/env python
# -*- coding: utf-8 -*-


import scpi
import wss
import logging
import time


logging.basicConfig(level=logging.INFO, format='*** %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger(__name__)


def use_case1():
    """
    直接改变光开关的连接
    """
    Logger.info("usecase1 演示开始")
    # 连接光开关
    scpi_oms = scpi.SCPIOpticalSwitchControl()
    scpi_oms.open_connect()
    # 连接WSS
    ser = wss.WssControl()
    ser.clear_response()
    ser.set_sab()
    
    # 验证光开关中是否存在已有连接
    connect_state = scpi_oms.check_all_connect()
    if connect_state:
        in_ports, out_ports = connect_state
        Logger.info("当前设备的连接in_ports-{}, out_ports-{}".format(in_ports, out_ports))
        # 清除之前的连接
        scpi_oms.delete_all_connect()
        
    # 设置光开关的初始连接
    scpi_oms.add_new_optical_path([1],[25])
    # 设置wss的初始连接
    ser.set_uca([[1,1,0], [2,1,0]])
    
    Logger.info("系统运行中...")
    time.sleep(10)
    Logger.info("工作需求发生变化")
    scpi_oms.add_new_optical_path([1],[29])
    Logger.info("系统恢复运行")
    
    # 演示结束
    scpi_oms.close_connect()
    ser.close_connect()
    Logger.info("usecase1演示完毕")
    
def use_case2():
    """
    改变wss的北向接口
    """
    Logger.info("usecase2 演示开始")
    # 连接光开关
    scpi_oms = scpi.SCPIOpticalSwitchControl()
    scpi_oms.open_connect()
    # 连接WSS
    ser = wss.WssControl()
    # 清除之前的设置
    ser.set_sab()
    
    # 验证光开关中是否存在已有连接
    connect_state = scpi_oms.check_all_connect()
    if connect_state:
        in_ports, out_ports = connect_state
        Logger.info("当前设备的连接in_ports-{}, out_ports-{}".format(in_ports, out_ports))
        # 清除之前的连接
        scpi_oms.delete_all_connect()
        
    # 设置光开关的初始连接
    scpi_oms.add_new_optical_path([1,3],[25,33])
    # 设置wss的初始连接
    ser.set_uca([[1,1,0], [2,1,0]])
    
    Logger.info("系统运行中...")
    time.sleep(10)
    Logger.info("工作需求发生变化")
    try:
        ser.set_uca([[1,2,0],[2,2,0]])
    except:
        ser.clear_response()
        ser.set_uca([[1,2,0],[2,2,0]])
    Logger.info("系统恢复运行")
    
    # 演示结束
    scpi_oms.close_connect()
    ser.close_connect()
    Logger.info("usecase2演示完毕")
    

def use_case3():
    """
    改变wss的南向接口
    """
    

def main():
    """
    测试主实例
    """
    use_case2()
    print("*"*50)
    
    
    
    
if __name__ == "__main__":
    main()
