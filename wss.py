#!/usr/bin/evn python2
# -*- coding: utf-8 -*-
import logging
import re
import serial
import time


BAUDRATE = 115200	  # 与设备通信的波特率
WINDOWS_SERIALPORT = 'com3'		 # windows操作系统下串口
LINUX_SERIALPORT = '/dev/ttyUSB0'		# linux操作系统下串口

# 设置logging信息
logging.basicConfig(level=logging.INFO, format='*** %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger(__name__)


class WssControl(object):
	"""
		调用serial模块中的相应的功能，
		得到或设置WSS的相关配置
	"""
	def __init__(self, port='com3', baudrate=115200, timeout=None):
		"""初始化，连接到相应设备"""
		self._ser = self.open_connect(port, baudrate, timeout)
		self.use_channel = None
		self.use_channel_slice = None
		# [[port_num, out_port, attenuation],...]
	
	def __del__(self):
		"""
		防止设备程序关闭时，serial连接未关闭
		"""
		if hasattr(self._ser, 'isOpen') and self._ser.isOpen():
			Logger.info("检测到程序已关闭，连接未关闭")
			self._ser.close()

	@staticmethod
	def open_connect(port, baudrate, timeout):
		"""
			建立一个新的连接
			port: 设备通信串口
			baudrate：设备通信波特率
			timeout：读取response时间timeout
		"""
		try:
			ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
			if not ser.isOpen():
				raise ValueError("*** 设备连接错误 ***")
			else:
				Logger.info("通过串口-{},波特率-{},连接到设备".format(port, baudrate))
			return ser
		except Exception as e:
			Logger.info(e)

	def response_len(self):
		"""获取接收到的数据长度"""
		return self._ser.inWaiting()

	def check_connection_status(self):
		"""查询设备的连接状态"""
		return self._ser.isOpen()
	
	def clear_response(self):
		"""
		清除设备初始化返回信息
		"""
		start_info = self._ser.read(self._ser.inWaiting())
		return start_info

	def read_response(self, command_type):
		"""读取相应command的响应信息"""

		pattern = re.compile("[\r\n]+")		 # 定义分离模式
		data = ''
		data = data.encode('utf-8')
		time.sleep(0.1)
		n = self._ser.inWaiting()
		# time.sleep(0.1) # 等待设备设置完成
		while n:
			data = data + self._ser.read(n)
			n = self._ser.inWaiting()
		# 防止有数据未读取完全
		# n = self._ser.inWaiting()
		if len(data) > 0 and n == 0:
			# try:
			temp = data.decode("utf-8")
			# Logger.info(temp)
			temp = pattern.split(temp)
			# Logger.info(temp)
			# 去除最后的一个空白符
			temp.remove('')
			# 去除命令的回显
			temp = [temp[i] for i in range(len(temp)) if i != 0]
			# Logger.info(temp)
			
			# 特殊处理 RES 命令
			if command_type == "RES":
				set_check_status = temp[0]
				command_type = False
			else:
				set_check_status = temp[-1]

			# 检查命令设置状态
			if set_check_status == "OK":
				Logger.info("命令设置成功")
				# 返回响应信息
				if command_type:
					# 设备查询命令为True
					# 设备设置命令为False
					# 设备查询命令返回信息
					return temp[0:-1]	# 去除查询命令后面的OK
				# 返回设置命令的返回信息
				return temp

			# 命令设置出现错误
			elif set_check_status == "CER":
				Logger.info("命令行错误，请检查命令是否支持或书写正确")
			elif set_check_status == "AER":
				Logger.info("命令参数错误，请检查参数是否书写正确及参数个数是否正确")
			elif set_check_status == "RER":
				Logger.info("命令参数范围错误，请检查参数范围是否正确")
			elif set_check_status == "VER":
				Logger.info("限定错误，请检查认证mode是否正确")

	def send_data(self, command):
		"""
		发送指定指令到设备中
		:param command: 指定的指令
		:return:
		"""
		len_command = self._ser.write('{}\n'.format(command).encode("utf-8"))
		return len_command

	def close_connect(self):
		"""关闭串口的连接"""
		if self._ser.isOpen():
			self._ser.close()
			Logger.info("串口连接关闭")
		else:
			Logger.info("串口连接已关闭")

	# 相应操作指令
	def check_sus(self):
		"""
			查询设备当前状态
			设备指令 SUS?
			:return
			三种响应：
			SLS:  Start Last Saved
			SAB:  Start All Blocked
			SFD:  Start Factory Default
		"""
		command = 'SUS?'
		self.send_data(command)
		message = self.read_response(True)
		if message:
			Logger.info("SUS 查询到当前状态为{}".format(message[0]))
			return message[0]

	def set_mid(self, id_string):
		"""
		MID <IDstring>\n
			设置设备的唯一id
		:return: id_string
		"""
		command = 'MID {}'.format(id_string)
		# 发送指令
		self.send_data(command)
		message = self.read_response(False)
		if message:
			Logger.info("设置设备的唯一ID为: {}".format(id_string))
			return id_string
		else:
			Logger.info("MID 指令设置失败")

	def check_mid(self):
		"""
		MID?
			查询设备的唯一Id
		:return: 设备Id string
		"""
		command = 'MID?'
		self.send_data(command)
		message = self.read_response(True)
		if message:
			Logger.info("查询到设备的唯一ID为: {}".format(message[0]))
			return message[0]
		else:
			Logger.info("MID? 查询出错")

	def set_sfd(self):
		"""
		SFD
		设置以出厂设置为初始状态：恢复出厂设置
		:return: OK -- 设置成功
		None -- 设置出错
		"""
		command = 'SFD'
		self.send_data(command)
		time.sleep(0.5)
		# 注意设备在有过多通道时，这一设置需要更长的时间
		message = self.read_response(False)
		if message:
			Logger.info("SFD 设置成功")
			return message
		else:
			Logger.info("SFD 设置出错")

	def set_sab(self):
		"""
			SAB
			设置所有的Channels为Blocked状态
			:return: OK -- 设置成功
			None -- 设置出错
		"""
		command = 'SAB'
		self.send_data(command)
		time.sleep(1)
		message = self.read_response(False)
		if message:
			Logger.info("SAB 设置成功")
			return message
		else:
			Logger.info("SAB 设置出错")

	def set_sls(self):
		"""
			SLS
			设置上一次保存的状态作为开机状态
			:return: OK -- 设置成功
			None -- 设置出错
		"""
		command = 'SLS'
		self.send_data(command)
		time.sleep(1)
		message = self.read_response(False)
		if message:
			Logger.info("SLS 设置成功")
			return message
		else:
			Logger.info("SLS 设置出错")

	def check_oss(self):
		"""
		OSS?
		查询设备的运行状态
		:return: 十六进制数
		"""
		pass

	def check_hss(self):
		"""
		HSS?
		查询设备软件的运行状态
		"""
		pass

	def check_lss(self):
		"""
		LSS?
		查询设备软件锁存状态
		相应bit位对应HSS的bit位
		"""
		pass

	def check_css(self):
		"""
		CSS?
		查询设备的范围温度
		温度不可高于70摄氏度
		:return: 返回的[temperature]
		"""
		command = 'CSS?'
		self.send_data(command)
		message = self.read_response(True)
		if message:
			Logger.info("设备case温度为: {}".format(message[0]))
			if float(message[0]) > 50:
				Logger.info("设备温度过高，注意设备的休息")
			return message[0]
		else:
			Logger.info("CSS? 查询出错")

	def check_iss(self):
		"""
		ISS?
		查询设备的内部温度
		:return:
		"""
		command = 'ISS?'
		self.send_data(command)
		message = self.read_response(True)
		if message:
			Logger.info("设备case温度为: {}".format(message[0]))
			if float(message[0]) > 60:
				Logger.info("设备温度过高，注意设备的休息")
			return message[0]
		else:
			Logger.info("ISS? 查询出错")

	def check_rpa(self):
		"""
		RPA?
		查询设备所有通道的可读状态
		:return:
		"""
		pass

	def set_upa(self, out_port, port_attenuation):
		"""
		UPA out_port,port_attenuation
		out_port: [1-9]
		port_attenuation: [0-20]
		设置所有可用通道唯一的输出端口和衰减值
		:return:
		"""
		command = "UPA {},{}".format(out_port, port_attenuation)
		self.send_data(command)
		time.sleep(0.5)
		message = self.read_response(False)
		if message:
			Logger.info("设置当前所有有效channel: out_port-{}, port_attenuation-{}".format(out_port, port_attenuation))
			return message
		else:
			Logger.info("UPA 设置出错")

	def check_rcs_one_channel(self, channel_number):
		"""
		RCS? channel_numbe
		查询某一通道的状态 -- out_port, channel_attenuation
		:param channel_number:
		:return: [channel_number, port_number, channel_attenuation
		"""
		command = "RCS? {}".format(channel_number)
		self.send_data(command)
		message = self.read_response(True)
		if message:
			Logger.info(message)
			response = re.split(',+', message[0])
			Logger.info("channel-{}, out_port-{}, attenuation-{}".format(response[0], response[1], response[2]))
			# response = ['channel_number', 'out_port', 'attenuation']
			return response
		else:
			Logger.info("RCS? 查询出错")

	def check_rca_all_channel(self):
		"""
		RCA?
		查询所有可用通道的状态 -- out_port, channel_attenuation
		:return:
		"""
		command = "RCA?"
		self.send_data(command)
		message = self.read_response(True)
		if message:
			response = re.split(";+", message[0])
			channel_plan = []
			# 解析查询的信息
			for one_channel in response:
				mid_mes = re.split(",+", one_channel)
				channel_plan.append(mid_mes)
			# channel_plan = [['channel_num','out_port','channel_att'],....]
			Logger.info("查询到：[channel, out_port, attenuation] -- {}".format(channel_plan))
			return channel_plan
		else:
			Logger.info("RCA? 查询出错")
	
	def get_useing_channel(self):
		"""
		得到设备中已用端口
		"""
		channl_list = self.check_rca_all_channel()
		self.use_channel = []
		for channel in channel_list:
			if channel[1] != '99':
				self.use_channel.append(channel)

	def set_uca(self, channel_plan):
		"""
		UCA channel_number,port_number,channel_attenuation;...
		设置一个或多个通道的状态
		:param channel_plan:
		channel_plan = [[channel_num, out_port, channel_att],....]
		:return:
		"""
		# 处理传入参数
		mid_channel = []
		for channel_node in channel_plan:
			mid_channel.append(",".join(map(str, channel_node)))
		# 组合参数为一个字符串
		channel_string = ";".join(map(str, mid_channel))
		
		command = "UCA {}".format(channel_string)
		self.send_data(command)
		time.sleep(0.5)
		message = self.read_response(False)
		if message:
			Logger.info("设置channel plan为{}".format(channel_string))
			return message
		else:
			Logger.info("UCA 设置出错")

	def set_chw(self, mode):
		"""
		CHW mode[0|50|100]
		设置设备的通道模式
		:return:
		"""
		if mode in [0, 50, 100]:
			command = "CHW {}".format(mode)
			self.send_data(command)
			message = self.read_response(False)
			if message:
				Logger.info("设置设备的模式为: {}".format(mode))
				return message
			else:
				Logger.info("CHW 设置出错")
		else:
			Logger.info("CHW {}-模式不存在".format(mode))

	def check_chr(self):
		"""
		CHR?
		查询设备的通道模式
		:return:
		"""
		command = "CHR?"
		self.send_data(command)
		message = self.read_response(True)
		if message:
			Logger.info("设备模式为: {}".format(message[0]))
			return message
		else:
			Logger.info("CHR? 查询出错")

	def trans_custom_list(self, custom_list, command_type):
		"""
		转换DCC，DCR定制channel字典 to 字符串
		custome_list: {'channel_num':{'width':[start_slice,end_slice], 'range':[start_range,end_range]}}
		"""
		if command_type == "DCC":
			custom_channel_string = ""
			for channel_num in custom_list.keys():
				custom_channel_string += str(channel_num) +\
										 "=" \
										 + ":".join(map(str, custom_list[channel_num]['width'])) \
										 + ";"
				# "1=1:8;"
			return custom_channel_string
		elif command_type == "DCR":
			custom_channel_range = ""
			for channel_num in custom_list.keys():
				custom_channel_range += str(channel_num) \
										+ "=" \
										+ ":".join(map(str,custom_list[channel_num]['width'])) \
										+ ',' \
										+ ":".join(map(str, custom_list[channel_num]['range'])) \
										+ ";"
			return custom_channel_range

	def trans_string_custom_list(self, custom_string, command_type):
		"""
		将DCC或DCR的命令转换成相应的字符串
		custom_string:
		DCC? ==> channel_num=slice1:slice2;...
		DCR? ==>channel_num=slice1:slice2,range1:range2;...
		custome_list: {'channel_num':{'width':[start_slice,end_slice], 'range':[start_range,end_range]}}
		"""
		channel_list = re.split(';+', custom_string)
		channel_plan_dict = {}

		if command_type == "DCC":
			for mid_channel in channel_list:
				mid_list = re.split('=+', mid_channel)
				slice_list = re.split(':+', mid_list[1])
				# 注意：这里的slice_list内为string类型
				channel_plan_dict[str(mid_list[0])] = {'width': slice_list}
		elif command_type == "DCR":
			for mid_channel in channel_list:
				mid_list = re.split('=+', mid_channel)
				slice_range_list = re.split(',+', mid_list[1])

				slice_list = re.split(':+', slice_range_list[0])
				range_list = re.split(':+', slice_range_list[1])
				# 注意：这里的slice_list内为string类型
				channel_plan_dict[str(mid_list[0])] = {'width': slice_list, 'range': range_list}
		return channel_plan_dict

	def set_dcc(self, custom_channel):
		"""
		DCC channel_number=slice_range1:slice_range2;...
		注意slice范围不可超过40
		设置一个或多个自定义通道路由
		custom_channel = "channel_num=slice1:slice2;..."
		注意：sliece的范围受到设备当前设定的影响
		:return:
		"""
		# 将custom字典转换成对应的字符串
		custom_string = self.trans_custom_list(custom_channel, 'DCC')
		command = "DCC {}".format(custom_string)
		self.send_data(command)
		time.sleep(0.5)
		message = self.read_response(False)
		if message:
			Logger.info("定制的channel plane 为: {}".format(custom_channel))
			return message
		else:
			Logger.info("DCC 设置出错")

	def check_dcc(self):
		"""
		DCC?
		查询定制通道路由
		:return:
		"""
		command = "DCC?"
		self.send_data(command)
		message = self.read_response(True)
		if message:
			channel_list = self.trans_string_custom_list(message[0], 'DCC')
			Logger.info("定制的channel plane 为: {}".format(channel_list))
			return channel_list
		else:
			Logger.info("DCC? 查询出错")

	def set_dcr(self, custom_channel_range):
		"""
		DCR channel_number=slice1:slice2,slice_range1:slice_range2;...
		自定义通道路由的同时，自定义相依的变化范围
		:return:
		"""
		# 将custom字典转换成string
		custom_channel_range_string = self.trans_custom_list(custom_channel_range, "DCR")
		command = "DCR {}".format(custom_channel_range_string)
		self.send_data(command)
		time.sleep(0.5)
		message = self.read_response(False)
		if message:
			Logger.info("定制的channel plane 为: {}".format(custom_channel_range))
			return message
		else:
			Logger.info("DCR 设置出错")
	
	def get_useing_channel_slice(self):
		"""
		得到已使用channel的slice范围
		"""
		self.use_channel_slice = {}
		channel_range_list = self.check_dcr()
		for channel in self.use_channel:
			if channel[0] in channel_range_list.keys():
				self.use_channel_slice[channel[0]] = channel_range_list[channel[0]]

	def check_dcr(self):
		"""
		DCR?
		查询定义通道路由和通道slice变化范围
		:return:
		"""
		command = "DCR?"
		self.send_data(command)
		time.sleep(0.2)
		message = self.read_response(True)
		if message:
			channel_dic = self.trans_string_custom_list(message[0], 'DCR')
			Logger.info("定制的channel plane 为: {}".format(channel_dic))
			return channel_dic
		else:
			Logger.info("DCR? 查询出错")

	def set_ccc(self, channel_list):
		"""
		CCC channel_number=slice1:slice2;
		注意slice一定要在slice range范围内
		:return:
		"""
		# 将channel_list字典转换成string
		channel_string = self.trans_custom_list(channel_list, "DCC")
		command = "CCC {}".format(channel_string)
		self.send_data(command)
		time.sleep(0.5)
		message = self.read_response(False)
		if message:
			Logger.info("定制的channel plane 为: {}".format(channel_string))
			return message
		else:
			Logger.info("CCC 设置出错")

	def set_dcs(self, string):
		"""
		DCS channel_number=attenuations,attenuations;...
		设置通道内每个slice的shape -- 设置attenuation实现
		:param string:
		:return:
		"""
		pass

	def check_dcs(self, channel_number=None):
		"""
		DCS? {channel_number}
		查询所有或单个channel的shape
		:return:
		"""
		pass

	def set_reset(self):
		"""
		RES
		重新设置设备软件
		:return:
		"""
		command = "RES"
		self.send_data(command)
		time.sleep(0.5)
		message = self.read_response("RES")
		if message:
			Logger.info("存储当前设备重置成功")
			return message
		else:
			Logger.info("STR 设置出错")

	def set_str(self):
		"""
		STR
		存储当前设备的状态 -- 配合SLS使用
		:return:
		"""
		command = "STR"
		self.send_data(command)
		time.sleep(0.5)
		message = self.read_response(False)
		if message:
			Logger.info("存储当前设备状态成功")
			return message
		else:
			Logger.info("STR 设置出错")

	def set_cle(self):
		"""
		CLE
		清除设备中的错误 -- OSS？ 和 LSS？中查询到的
		:return:
		"""
		command = "CLE"
		self.send_data(command)
		
		message = self.read_response(False)
		if message:
			Logger.info("清除设备的软件错误 -- 通过OSS?和LSS?查询得到的")
			return message
		else:
			Logger.info("CLE 设置出错")


# 测试函数
def test():
	"""测试类中函数的功能"""
	pass


if __name__ == "__main__":
	ser = WssControl()
