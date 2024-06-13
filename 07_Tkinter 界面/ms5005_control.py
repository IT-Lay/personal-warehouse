# -*- coding: utf-8 -*-
# Author: Lay.zhang
# Date: 2024/6/5

import socket
import time
import random
import threading
import itertools

class Control:
    def __init__(self, message_queue):
        self.client_socket = None
        self.message_queue = message_queue
        # 添加控制循环暂停的事件
        self.pause_event = threading.Event()
        # self.pause_event.set()
        self.running = False

    def connect(self, ip, port):
        # 创建socket对象
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 连接到设备
            self.client_socket.connect((ip, port))
            time.sleep(1)
            self.message_queue.put("Succesfully connected to the MS-5005 device.")

        except Exception as e:
            self.message_queue.put(f"An error occurred: {e}")

    def disconnect(self):
        self.message_queue.put("Disconnected.")
        self.client_socket.close()

    def send_command(self, send_command, reply='aabbcc'):
        # 设置超时时间
        self.client_socket.settimeout(1)
        chunk = b''

        if self.running:
            # 将十六进制字符串列表转换为字节串
            command_bytes = bytes([int(x, 16) for x in send_command.split()])

            # 发送十六进制命令
            self.client_socket.sendall(command_bytes)

            # 接收响应
            et = time.time() + 3
            while et > time.time():
                try:
                    chunk = self.client_socket.recv(64)
                except socket.timeout:
                        break
            # print(f"Hex command receive: {response.hex()}")

            # 检查暂停事件状态，非阻塞式等待
            while self.pause_event.wait(timeout=0.1):
                if not self.running:  # 检查是否停止
                    break

            return chunk.hex()

    def output_matching(self, output, command, res):
        if self.running:
            if output:
                get_output = f'0x{output}'
                if int(get_output, 16) == int(command, 16):
                    self.message_queue.put(f'{res} is ok')
                else:
                    self.message_queue.put(f'{res} not available for switch')
            else:
                self.message_queue.put(f'{res} switch error')

    def run_test(self, *args):
        try:
            '''
            *args 参数
            0 - 分辨率指令参数列表
            1 - 色彩指令参数列表
            2 - 音频指令参数列表
            3 - HDCP指令参数列表
            4 - 分辨率参数列表
            5 - 色彩参数列表
            6 - 音频参数列表
            7 - HDCP参数列表
            8 - 运行次数
            9 - 间隔时间
            10 - 切换模式
            11 - 运行参数状态
            '''

            resolution_list = [
            "0x15", "0x16", "0x0", "0x2", "0x1", "0x3", "0x17", "0x18", "0x19", "0x1a",
            "0x1b", "0x1c", "0x9", "0x8", "0x7", "0x6", "0x5", "0x4", "0x1d", "0x1e",
            "0x1f", "0x21", "0x22", "0x20", "0x23", "0x24", "0xc", "0xb", "0xa", "0x14",
            "0x13", "0x12", "0x11", "0x10", "0xf", "0xe", "0x2f", "0x25", "0x26", "0x2e",
            "0x2d", "0x2c", "0x2b", "0x2a", "0x29", "0x28", "0x27", "0x37", "0x36", "0x35",
            "0x34", "0x33", "0x32", "0x31", "0x30"]
            color_space_list = ["0x1", "0x2", "0x3", "0x4", "0x0"]
            color_depth_list = ["0x0", "0x1", "0x2", "0x3"]
            audio_mute_list = ["0x0", "0x1"]
            audio_length_list = ["0x2", "0x1", "0x0"]
            audio_level_list = ["0x0", "0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7"]
            audo_rate_list = ["0x3", "0x4", "0x0", "0x1", "0x2"]
            audio_channel_list = ["0x0", "0x1", "0x2", "0x3", "0x4"]
            tx_hdcp_list = ["0x0", "0x1", "0x2", "0x3"]
            rx_hdcp_list = ["0x0", "0x1", "0x2", "0x3"]

            resolution_map = ["640x480p@60", "640x480p@75", "720x480i@60", "720x480p@60", "720x576i@50", "720x576p@50", "800x600p@60", "800x600p@75",
                              "1024x768p@60", "1024x768p@75", "1280x1024p@60", "1280x1024p@75", "1280x720p@25", "1280x720p@29.97", "1280x720p@30", "1280x720p@50",
                              "1280x720p@59.94", "1280x720p@60", "1360x768p@60", "1366x768p@60", "1400x1050p@60", "1440x900p@60", "1440x900p@75", "1600x1200p@60",
                              "1680x1050p@60", "1680x1050pRB", "1920x1080i@50", "1920x1080i@59.94", "1920x1080i@60", "1920x1080p@23.976", "1920x1080p@24", "1920x1080p@25",
                              "1920x1080p@29.97", "1920x1080p@30", "1920x1080p@50", "1920x1080p@59.94", "1920x1080p@60", "1920x1080pRB", "1920x1200pRB", "3840x2160p@23.976",
                              "3840x2160p@24", "3840x2160p@25", "3840x2160p@29.97", "3840x2160p@30", "3840x2160p@50", "3840x2160p@59.94", "3840x2160p@60", "4096x2160p@23.976",
                              "4096x2160p@24", "4096x2160p@25", "4096x2160p@29.97", "4096x2160p@30", "4096x2160p@50", "4096x2160p@59.94", "4096x2160p@60"]
            color_space_map = ["RGB", "YCbCr 444", "YCbCr 422", "YCbCr 420", "DVI"]
            color_depth_map = ["8", "10", "12", "16"]
            audio_length_map = ["16", "20", "24"]
            audio_mute_map = ["OFF", "ON"]
            audio_level_map = ["0", "1", "2", "3", "4", "5", "6", "7"]
            audo_rate_map = ["32KHz", "44.1KHz", "48KHz", "96KHz", "192KHz"]
            audio_channel_map = ['2Ch', '2.1Ch', '5.1Ch', '6.1Ch', '7.1Ch']
            tx_hdcp_map = ["TX OFF", "TX HDCP 1.4", "TX HDCP 2.2 Type 0", "TX HDCP 2.2 Type 1"]
            rx_hdcp_map = ["RX OFF", "RX HDCP 1.4", "RX HDCP 2.2", "RX HDCP 1.4 & HDCP 2.2"]

            # 建立映射关系
            map0_dict = {num: char for num, char in zip(resolution_list, resolution_map)}
            map1_dict = {num: char for num, char in zip(color_space_list, color_space_map)}
            map2_dict = {num: char for num, char in zip(color_depth_list, color_depth_map)}
            map3_dict = {num: char for num, char in zip(audio_mute_list, audio_mute_map)}
            map4_dict = {num: char for num, char in zip(audio_length_list, audio_length_map)}
            map5_dict = {num: char for num, char in zip(audio_level_list, audio_level_map)}
            map6_dict = {num: char for num, char in zip(audo_rate_list, audo_rate_map)}
            map7_dict = {num: char for num, char in zip(audio_channel_list, audio_channel_map)}
            map8_dict = {num: char for num, char in zip(tx_hdcp_list, tx_hdcp_map)}
            map9_dict = {num: char for num, char in zip(rx_hdcp_list, rx_hdcp_map)}

            resolution_list, color_list, audio_list, hdcp_list = args[0], args[1], args[2], args[3]
            res_show_list = args[4]
            run_times = args[5]
            run_interval = args[6]
            switch_sequences = args[7]
            checkbox_status = args[8]

            # 排列组合测试的项目
            if checkbox_status:
                command_list = list(itertools.product(resolution_list, color_space_list, color_depth_list, audio_mute_list, audio_length_list,
                                                      audio_level_list, audo_rate_list, audio_channel_list, tx_hdcp_list))
                self.message_queue.put(f'>>> 遍历共: {len(command_list)}种组合')
                for t in range(int(run_times)):
                    if self.running:
                        self.message_queue.put(f'***************** 第{t + 1}次循环 *****************')
                        # 切换分辨率参数
                        for n, command in enumerate(command_list):
                            self.message_queue.put(f'****** 第 {len(command_list)}\\{n+1} 组 ******')
                            if self.running:
                                res_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x1 {command[0]}'
                                self.message_queue.put(f'>>> Resolution switching to {map0_dict[command[0]]}')
                                self.send_command(res_command)
                                out_res_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x2'
                                get_res_output = self.send_command(out_res_command)
                                self.output_matching(get_res_output, command[0], map0_dict[command[0]])

                                if self.running:
                                    # 其他参数
                                    self.message_queue.put(f'>>> Color switching to\n'
                                                           f'Color Space: {map1_dict[command[1]]}\n'
                                                           f'Color Depth: {map2_dict[command[2]]}')
                                    mode_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x3 {command[1]}'
                                    self.send_command(mode_command)
                                    out_mode_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x4'
                                    get_mode_command = self.send_command(out_mode_command)
                                    self.output_matching(get_mode_command, command[1], map1_dict[command[1]])

                                    depth_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x5 {command[2]}'
                                    self.send_command(depth_command)
                                    out_depth_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x6'
                                    get_depth_command = self.send_command(out_depth_command)
                                    self.output_matching(get_depth_command, command[2], map2_dict[command[2]])
                                if self.running:
                                    self.message_queue.put(f'>>> Audio switching to\n'
                                                           f'Audio Mute: {map3_dict[command[3]]}\n'
                                                           f'Audio Length: {map4_dict[command[4]]}\n'
                                                           f'Audio Level: {map5_dict[command[5]]}\n'
                                                           f'Audio Sample Rate: {map6_dict[command[6]]}\n'
                                                           f'Audio Channel Number: {map7_dict[command[7]]}')
                                    mute_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x9 {command[3]}'
                                    self.send_command(mute_command)
                                    out_mute_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0xa'
                                    get_mute_command = self.send_command(out_mute_command)
                                    self.output_matching(get_mute_command, command[3], map3_dict[command[3]])

                                    if map3_dict[command[3]] == 'OFF':
                                        length_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0xb {command[4]}'
                                        self.send_command(length_command)
                                        out_length_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0xc'
                                        get_length_command = self.send_command(out_length_command)
                                        self.output_matching(get_length_command, command[4], map4_dict[command[4]])

                                        level_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0xd {command[5]}'
                                        out_level_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0xe'
                                        self.send_command(level_command)
                                        get_level_command = self.send_command(out_level_command)
                                        self.output_matching(get_level_command, command[5], map5_dict[command[5]])

                                        rate_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0xf {command[6]}'
                                        self.send_command(rate_command)
                                        out_rate_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x10'
                                        get_rate_command = self.send_command(out_rate_command)
                                        self.output_matching(get_rate_command, command[6], map6_dict[command[6]])

                                        number_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x11 {command[7]}'
                                        self.send_command(number_command)
                                        out_number_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x12'
                                        get_number_command = self.send_command(out_number_command)
                                        self.output_matching(get_number_command, command[7], map7_dict[command[7]])
                                if self.running:
                                    self.message_queue.put(f'>>> HDCP switching to {map8_dict[command[8]]}')
                                    tx_hdcp_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x13 {command[8]}'
                                    self.send_command(tx_hdcp_command)
                                    out_tx_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x14'
                                    get_tx_command = self.send_command(out_tx_command)
                                    self.output_matching(get_tx_command, command[8], map8_dict[command[8]])

                                    # rx_hdcp_commad = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x15 {command[9]}'
                                    # self.send_command(rx_hdcp_commad)
                                    # out_rx_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x16'
                                    # get_rx_command = self.send_command(out_rx_command)
                                    # self.output_matching(get_rx_command, command[9], map9_dict[command[9]])

                                while self.pause_event.wait(timeout=0.1):  # 检查暂停事件状态，非阻塞式等待
                                    if not self.running:  # 检查是否停止
                                        break
                                if self.running:
                                    time.sleep(float(run_interval))
                                else:
                                    break
                            else:
                                break
                    else:
                        break
                if self.running:
                    self.message_queue.put('End of run.')
            else:
                if '顺序' in switch_sequences:
                   pass
                elif '倒序' in switch_sequences:
                    resolution_list = resolution_list[::-1]
                    res_show_list = [map0_dict[num] for num in resolution_list]
                elif '随机'  in switch_sequences:
                    map_dict = {str(num): char for num, char in zip(resolution_list, res_show_list)}
                    random.shuffle(resolution_list)
                    res_show_list = [map_dict[str(num)] for num in resolution_list]

                for t in range(int(run_times)):
                    if self.running:
                        self.message_queue.put(f'***************** 第{t + 1}次循环 *****************')
                        # 切换分辨率参数
                        for n, command in enumerate(resolution_list):
                            if self.running:
                                # 发送分辨率切换指令
                                res_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x1 {command}'
                                self.message_queue.put(f'>>> Resolution switching to {res_show_list[n]}')
                                self.send_command(res_command)
                                get_res_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x2'
                                get_output = self.send_command(get_res_command)
                                self.output_matching(get_output, command, res_show_list[n])

                                if n == 0:
                                    # 其他参数
                                    if self.running:
                                        self.message_queue.put(f'>>> Color switching to\n'
                                                               f'Color Space: {map1_dict[color_list[0]]}\n'
                                                               f'Color Depth: {map2_dict[color_list[1]]}')
                                        mode_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x3 {color_list[0]}'
                                        self.send_command(mode_command)
                                        out_mode_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x4'
                                        get_mode_command = self.send_command(out_mode_command)
                                        self.output_matching(get_mode_command, color_list[0], map1_dict[color_list[0]])

                                        depth_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x5 {color_list[1]}'
                                        self.send_command(depth_command)
                                        out_depth_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x6'
                                        get_depth_command = self.send_command(out_depth_command)
                                        self.output_matching(get_depth_command, color_list[1], map2_dict[color_list[1]])
                                    if self.running:
                                        self.message_queue.put(f'>>> Audio switching to\n'
                                                               f'Audio Mute: {map3_dict[audio_list[0]]}\n'
                                                               f'Audio Length: {map4_dict[audio_list[1]]}\n'
                                                               f'Audio Level: {map5_dict[audio_list[2]]}\n'
                                                               f'Audio Sample Rate: {map6_dict[audio_list[3]]}\n'
                                                               f'Audio Channel Number: {map7_dict[audio_list[4]]}')
                                        mute_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x9 {audio_list[0]}'
                                        self.send_command(mute_command)
                                        out_mute_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0xa'
                                        get_mute_command = self.send_command(out_mute_command)
                                        self.output_matching(get_mute_command, audio_list[0], map3_dict[audio_list[0]])

                                        # Mute on 不需要切换音频其他选项
                                        if map3_dict[audio_list[0]] == 'OFF':
                                            length_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0xb {audio_list[1]}'
                                            self.send_command(length_command)
                                            out_length_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0xc'
                                            get_length_command = self.send_command(out_length_command)
                                            self.output_matching(get_length_command, audio_list[1], map4_dict[audio_list[1]])

                                            level_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0xd {audio_list[2]}'
                                            out_level_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0xe'
                                            self.send_command(level_command)
                                            get_level_command = self.send_command(out_level_command)
                                            self.output_matching(get_level_command, audio_list[2], map5_dict[audio_list[2]])

                                            rate_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0xf {audio_list[3]}'
                                            self.send_command(rate_command)
                                            out_rate_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x10'
                                            get_rate_command = self.send_command(out_rate_command)
                                            self.output_matching(get_rate_command, audio_list[3], map6_dict[audio_list[3]])

                                            number_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x11 {audio_list[4]}'
                                            self.send_command(number_command)
                                            out_number_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x12'
                                            get_number_command = self.send_command(out_number_command)
                                            self.output_matching(get_number_command, audio_list[4], map7_dict[audio_list[4]])
                                    if self.running:
                                        self.message_queue.put(f'>>> HDCP switching to\n'
                                                               f'TX: {map8_dict[hdcp_list[0]]}\n'
                                                               f'RX: {map9_dict[hdcp_list[1]]}')
                                        tx_hdcp_command = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x13 {hdcp_list[0]}'
                                        self.send_command(tx_hdcp_command)
                                        out_tx_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x14'
                                        get_tx_command = self.send_command(out_tx_command)
                                        self.output_matching(get_tx_command, hdcp_list[0], map8_dict[hdcp_list[0]])

                                        rx_hdcp_commad = f'0x4d 0x53 0x5 0x0 0x0 0x5 0x15 {hdcp_list[1]}'
                                        self.send_command(rx_hdcp_commad)
                                        out_rx_command = '0x4d 0x53 0x5 0x0 0x0 0x5 0x16'
                                        get_rx_command = self.send_command(out_rx_command)
                                        self.output_matching(get_rx_command, hdcp_list[1], map9_dict[hdcp_list[1]])
                                while self.pause_event.wait(timeout=0.1):  # 检查暂停事件状态，非阻塞式等待
                                    if not self.running:  # 检查是否停止
                                        break
                                if self.running:
                                    time.sleep(float(run_interval))
                                else:
                                    break
                            else:
                                break
                    else:
                        break
                if self.running:
                    self.message_queue.put('End of run.')
        except Exception as e:
            self.message_queue.put(f"An error occurred: {e}")
