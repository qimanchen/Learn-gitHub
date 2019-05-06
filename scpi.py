#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置
通过scpi协议进行控制设备
主要使用pyserial模块
ser = serial.serial_for_url("socket://192.168.0.5:161")
建立串口连接
注：
要看设备的设置的ip和port
默认端口为5025
设备大部分命令是无返回信息的
"""
import serial
import logging
import re
import time


# 设备ip和port
IP = "192.168.3.105"
PORT = "5025"

# 设置logger信息 -- python2 与python3通用
logging.basicConfig(level=logging.INFO, format='*** %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger(__name__)


class SCPIOpticalSwitchControl(object):
    """
        光开关的控制
    """

    def __init__(self, url="192.168.1.120", port="5025"):

        self._url = url
        self._port = port
        self._ser = None
        # 存储设备中已建立连接的port
        self.exist_in_port = None
        self.exist_out_port = None
        # 存储设备中所有端口的状态
        self.port_states = {}

    def check_serial_link(self):
        """
            测试serial端口连接是否还存在
        """
        if hasattr(self._ser, "isOpen"):
            return self._ser.isOpen()
        else:
            Logger.info("当前设备还未建立过任何连接")

    def open_connect(self):
        """建立一个连接"""
        # format 会把花括号内的看成一个变量
        link_string = "socket://{host}:{port}".format(host=self._url, port=self._port)
        if hasattr(self._ser, 'isOpen') and self._ser.isOpen():
            Logger.info("连接已存在，请不要重复建立")
        else:
            self._ser = serial.serial_for_url(link_string)
            Logger.info("建立一个新的socket连接")

    def recv_message(self):
        """
        接收设备相应信息
        :return:
        """
        data = ''
        data = data.encode("utf-8")
        n = self._ser.inWaiting()
        # 这里与serial.Serial模块的inWaiting功能有些差别
        # 这里每次只返回一个，而不是直接返回
        time.sleep(0.1)
        while self._ser.inWaiting():
            # 组合设备信息
            data += self._ser.read(n)
            n = self._ser.inWaiting()

        if len(data) > 0 and n == 0:
            msg = data.decode("utf-8")
            # 去除换行符
            msg = re.sub('\s+', '', msg)
            return msg
        else:
            raise ValueError("recv_message 没有读取到信息")
            # Logger.info("请检查命令是否设置出错")

    def send_command(self, command):
        """
        发送指令到设备中去
        :return:
        """
        try:
            self._ser.write("{}\n".format(command).encode("utf-8"))
            message = self.recv_message()
            if message:
                Logger.info("指令-{}设置成功".format(command))
                return message
            else:
                Logger.info("指令-{}设置失败".format(command))
        except Exception as e:
            Logger.info("指令发送异常 -- {}".format(e))

    def decode_command(self, command):
        """
        将命令设置成设备可读形式，并发送出去
        :param command:
        :return:
        """
        len_command = self._ser.write("{}\n".format(command).encode("utf-8"))
        return len_command

    def close_connect(self):
        """
        关闭现有的连接
        :return:
        """
        if hasattr(self._ser, 'isOpen') and self._ser.isOpen():
            self._ser.close()
            Logger.info("serial 端口连接关闭")
        else:
            Logger.info("连接不存在 或 连接已关闭")

    def set_ip_port(self):
        """
        命令：:syst:comm:netw:addr <ip>[,<gateway>[,<mask>[,<broadcast>]]] -- 设置网卡1
        命令：:syst:comm:netw2:addr <ip>[,<gateway>[,<mask>[,<broadcast>]]] -- 设置网卡2
        命令返回：<none>
        更改设备的ip和port
        见设备文档第3页
        """
        pass

    def check_ip_port(self, net_interface):
        """
        命令：:syst:comm:netw:addr? -- 查询网卡1
        命令：:syst:comm:netw2:addr? -- 查询网卡2
        命令返回：IP="192.168.1.1" Gateway="0.0.0.0" Mask="255.255.255.0" Broadcast="192.168.1.255
        :param net_interface:
        :return:
        """
        pass

    def set_clear_register_error(self):
        """
        命令：*cls
        命令返回：<none>
        :return:
        """

    def check_connect_success(self):
        """
        命令：*idn?
        命令返回：Polatis,I-OST-24x24-LU1-DMHNS,002414,6.5.2.18
        测试设备是否已经正常的连接上仪器
        查看设备
        :return:
        """
        self._ser.write("*idn?\n".encode("utf-8"))
        time.sleep(0.1)
        if self._ser.inWaiting():
            Logger.info("与设备连接成功")
        else:
            Logger.info("与设备连接失败")
        pass

    def add_new_optical_path(self, in_port, out_port):
        """
        注：in_port -- [1,24], out_port -- [25, 48]
        命令：:oxc:swit:conn:add (@1,2,3),(@17,18.19)
        命令返回：<none>
        在设备已有连接的基础上，新建一个新的光连接
        :param in_port:[1,2,3]
        :param out_port:[4,5,6]
        :return:
        """
        in_ports = ",".join(map(str, in_port))
        out_ports = ",".join(map(str, out_port))
        command = ":oxc:swit:conn:add (@{in_port}),(@{out_port})".format(in_port=in_ports, out_port=out_ports)
        self.decode_command(command)
        # 检测是否设置成功
        port_list = self.check_all_connect()
        if port_list:
            exit_in_port, exit_out_port = port_list

            if set(exit_in_port) >= set(in_port) and set(exit_out_port) >= set(out_port):
                Logger.info("Add: in_port -- {}, out_port -- {}连接建立成功".format(in_port, out_port))
                return exit_in_port, exit_out_port
            else:
                Logger.info("连接建立失败，请检查端口设置和设备连接状态")
        else:
            Logger.info("连接建立失败，请检查端口设置和设备连接状态")

    def add_only_new_optical_path(self, in_port, out_port):
        """
        命令：:oxc:swit:conn:only (@1,2,3),(@17,18,19)
        命令返回：<none>
        清除所有之前的设备的连接，建立新增加的连接
        :param in_port: 参照 add_new_optical_path()
        :param out_port:
        :return:
        """
        in_ports = ",".join(map(str, in_port))
        out_ports = ",".join(map(str, out_port))
        command = ":oxc:swit:conn:only (@{in_port}),(@{out_port})".format(in_port=in_ports, out_port=out_ports)
        self.decode_command(command)
        # 检测是否设置成功
        port_list = self.check_all_connect()
        if port_list:
            exit_in_port, exit_out_port = port_list

            if set(exit_in_port) == set(in_port) and set(exit_out_port) == set(out_port):
                Logger.info("Only: in_port -- {}, out_port -- {}连接建立成功".format(in_port, out_port))
                return exit_in_port, exit_out_port
            else:
                Logger.info("连接建立失败，请检查端口设置和设备连接状态")
        else:
            Logger.info("连接建立失败，请检查端口设置和设备连接状态")

    def check_link_port(self, port_num):
        """
        命令：:oxc:swit:conn:port? 2
        命令返回："18"
        检查设备的某一端口的连接端口是?
        :param port_num:
        :return: 连接的目标端口
        """
        if self.exist_in_port is None:
            Logger.info("端口-{}未连接其他端口".format(port_num))
            return
        if port_num in self.exist_in_port or port_num in self.exist_out_port:
            command = "oxc:swit:conn:port? {}".format(port_num)
            self.decode_command(command)
            msg = self.recv_message()
            msg = str(msg)
            result = int(re.sub("\D","",msg))
            Logger.info("端口-{}连接端口{}".format(port_num, msg))
            return result
        else:
            Logger.info("端口-{}未连接其他端口")

    def check_all_connect(self):
        """
        命令：:oxc:swit:conn:stat?
        命令返回：(@1,2,3),(@19,18,22)
        查询设备中已建立的所有的连接
        :return:
        返回的是in_port和out_port列表
        其元素为字符串
        """
        command = ":oxc:swit:conn:stat?"
        self.decode_command(command)
        # 接收查询的结果
        msg = self.recv_message()
        if msg != "(@),(@)":
            # 去除括号
            msg = msg.replace('(', '').replace('),', '').replace(')', '')

            port_list = re.split('@', msg)
            in_port = port_list[1].split(',')   # ['1','2']
            out_port = port_list[2].split(',')  # ['2','3']

            # 将每一个字符串port转换为int方便比较
            in_ports = list(map(int, in_port))
            out_ports = list(map(int, out_port))

            self.exist_in_port = in_ports
            self.exist_out_port = out_ports
            return in_ports, out_ports
        else:
            self.exist_in_port = None
            self.exist_out_port = None
            Logger.info("当前设备不存在任何端口连接")

    def delete_one_connect(self, in_port, out_port=None):
        """
        命令：:oxc:swit:conn:sub (@1),(@17)
              :oxc:swit:conn:sub (@1,2,3),(@)
        命令返回：<none>
        删除设备中的某一连接
        注：
            可以只给出in_port，最好给出out_port
        :param in_port:
        :param out_port:
        :return:
        """
        in_ports = ",".join(map(str, in_port))
        if out_port is not None:
            out_ports = ",".join(map(str, out_port))
        else:
            out_ports = ''

        command = ":oxc:swit:conn:sub (@{}),(@{})".format(in_ports, out_ports)
        self.decode_command(command)

        # 验证是否删除成功，同时更新连接列表
        self.check_all_connect()
        if not set(self.exist_in_port) >= set(in_port):
            Logger.info("in_port-{}, out_port-{} 的连接删除成功".format(in_port, out_port))
        else:
            Logger.info("in_port-{}, out_port-{} 的连接删除失败，请检查连接和命令".format(in_port, out_port))

    def delete_all_connect(self):
        """
        命令：:oxc:swit:disc:all
        命令返回：<none>
        删除设备中所有的连接
        :return:
        """
        # in_ports = ",".join(map(str, self.exist_in_port))
        # out_ports = ""

        command = ":oxc:swit:disc:all"
        self.decode_command(command)

        # 验证是否删除成功，同时更新连接列表
        self.check_all_connect()
        if self.exist_in_port is None:
            Logger.info("设备的所有端口连接断开")
        else:
            Logger.info("in_port-{}, out_port-{} 的连接删除失败，请检查连接和命令".format(self.exist_in_port,
                                                                          self.exist_out_port))

    def disabled_port(self, port_num):
        """
        命令：:oxc:swit:port:dis (@2,4,6)
        命令返回：<none>
        使得某一端口down -- 关闭该端口
        :return:
        """
        port_nums = ":oxc:swit:port:dis (@{})".format(",".join(map(str, port_num)))
        self.decode_command(port_nums)

        # 检测port_state
        port_state = self.check_port_state(port_num)
        if port_state != self.port_states:
            Logger.info("ports-{} to disable".format(port_num))
        else:
            Logger.info("端口disabled失败，请检查连接和命令")

    def enabled_port(self, port_num):
        """
        命令：:oxc:swit:port:enab (@2,,4,6)
        命令返回：<none>
        重新开启某一端口
        :param port_num:
        :return:
        """
        port_nums = ":oxc:swit:port:enab (@{})".format(",".join(map(str, port_num)))
        self.decode_command(port_nums)

        # 检测port_state
        port_state = self.check_port_state(port_num)
        if port_state != self.port_states:
            Logger.info("ports-{} to enable".format(port_num))
        else:
            Logger.info("端口disabled失败，请检查连接和命令")

    def check_port_state(self, port_num=None):
        """
        命令：:oxc:swit:port:stat? (@2,4,6)
        命令返回：(D,E,F)
        D -- Disabled Channel
        E -- Enabled Channel
        F -- Failed Channel
        查询某一端口的状态
        :param port_num:
        :return:
        """
        port_state = {}
        # if port_num is not None:
        #     for port in port_num:
        #         if port in self.enable_port:
        #             port_state['port'] = 'enabled'
        #         elif port in self.disable_port:
        #             port_state['port'] = 'disabled'
        #         else:
        #             port_state['port'] = 'failed'

        # 更新port状态字典
        command = ":oxc:swit:port:stat?"
        self.decode_command(command)
        
        msg = self.recv_message()
        msg = msg.replace('(', '').replace(')', '')
        port_states = msg.split(',')
        for i in range(len(port_states)):
            if port_states[i] == 'D':
                self.port_states[str(i+1) ] = "disabled"
            elif port_states[i] == 'E':
                self.port_states[str(i+1)] = "enabled"
            else:
                self.port_states[str(i+1)] = "failed"

        if port_num is not None:
            for port in port_num:
                port_state[str(port)] = self.port_states[str(port)]
            return port_state
        else:
            return self.port_states

    def check_size(self):
        """
        命令：:oxc:swit:size?
        命令返回：16,16
        查询设备的大小
        :return:
        """


if __name__ == "__main__":
    scpi_wss = SCPIOpticalSwitchControl()
    scpi_wss.open_connect()
    scpi_wss.check_port_state()
    
