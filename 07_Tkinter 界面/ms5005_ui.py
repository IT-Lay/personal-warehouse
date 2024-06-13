# -*- coding: utf-8 -*-
# Author: Lay.zhang
# Date: 2024/6/7

import threading
import logging
import base64,os
from datetime import datetime
from icon import img
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter.constants import END
from ms5005_control import Control
from queue import Queue, Empty

class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        """ 创建窗口, 调用消息队列 """
        self.setup_window()
        self.create_widgets()
        self.message_queue = Queue()
        self.control = Control(self.message_queue)
        self.background_processing()
        self.paused = False
        # 5005 连接端口号
        self.port = 6133

    def setIcon(self):
        tmp = open("tmp.ico", "wb+")
        tmp.write(base64.b64decode(img))  # 写入到临时文件中
        tmp.close()
        self.iconbitmap("tmp.ico")  # 设置图标
        os.remove("tmp.ico")

    def setup_window(self):
        """ 主窗口界面函数, 设置窗口大小以及样式 """
        self.title("MS-5005 自动化测试工具")
        width = 750
        height = 630
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.setIcon()
        self.geometry(geometry)
        self.resizable(width=False, height=False)

        # 初始化选项卡
        self.notebook = Notebook(self)
        self.notebook.pack(side="left", padx=(25, 0), pady=(180, 0))
        self.notebook.config(width=290, height=300)

        # 创建各个选项卡的内容
        self.create_resolution_tab()
        self.create_color_tab()
        self.create_audio_tab()
        self.create_tools_tab()
        # style = Style()
        # style.theme_use('vista')

    def create_widgets(self):
        self.run()
        self.creat_select_frame()
        self.create_parameters_frame()
        self.create_log_frame()

    def run(self):
        """ 创建 IP 输入框, 以及连接，运行，停止按钮 """
        label = Label(self, text="IP:", anchor="center")
        label.place(x=20, y=35, width=50, height=30)
        self.ip_var = StringVar()
        ipt = Entry(self, textvariable=self.ip_var, validate="key", validatecommand=(self.register(self.validate_number_input), "%P"), invalidcommand=self.on_invalid_input, justify='center')
        ipt.place(x=85, y=35, width=150, height=30)
        ipt.insert(0, "192.168.1.10")
        self.btn_connect = Button(self, text="连接", takefocus=False, command=self.connect_ip)
        self.btn_connect.place(x=300, y=35, width=50, height=30)
        self.btn_run = Button(self, text="运行", takefocus=False, state=DISABLED, command=self.run_instrument)
        self.btn_run.place(x=450, y=35, width=80, height=30)
        self.btn_stop = Button(self, text="停止", state=DISABLED, takefocus=False, command=self.stop_test)
        self.btn_stop.place(x=600, y=35, width=80, height=30)

    def create_parameters_frame(self):
        """ 创建 设置LabelFrame以及对应控件 """
        frame = LabelFrame(self, text="设置")
        frame.place(x=27, y=84, width=330, height=150)

        Label(frame, text="运行次数：").place(x=12, y=10, width=60, height=30)
        self.run_times_entry = Entry(frame, validate="key", validatecommand=(self.register(self.validate_number), "%P"), justify='center')
        self.run_times_entry.insert(0, "1")
        self.run_times_entry.place(x=86, y=10, width=100, height=30)

        Label(frame, text="间隔时间：").place(x=12, y=78, width=60, height=30)
        self.interval_entry = Entry(frame, validate="key", validatecommand=(self.register(self.validate_number), "%P"), justify='center')
        self.interval_entry.insert(0, "10")
        self.interval_entry.place(x=86, y=78, width=100, height=30)

        self.mode_var = StringVar(value="顺序")
        modes = ["顺序", "倒序", "随机"]
        for i, mode in enumerate(modes):
            Radiobutton(frame, text=mode + "切换", value=mode, variable=self.mode_var).place(x=220, y=5 + 40 * i, width=80, height=30)

    def creat_select_frame(self):
        self.iterate_checkbox_var = BooleanVar()
        self.iterate_checkbox = Checkbutton(self, text="遍历", variable=self.iterate_checkbox_var)
        self.iterate_checkbox.place(x=290, y=589)
        # 创建全选，取消按钮并绑定对应事件
        btn_all = Button(self, text="全选", takefocus=False, command=self.select_all)
        btn_all.place(x=60, y=585, width=50, height=30)
        btn_cancel = Button(self, text="取消", takefocus=False, command=self.cancel_all)
        btn_cancel.place(x=180, y=585, width=50, height=30)

    def create_log_frame(self):
        """ 创建 日志LabelFrame以及对应控件 """
        frame = LabelFrame(self, text="日志")
        frame.place(x=380, y=85, width=340, height=480)
        self.text_area = Text(frame, wrap=WORD, state='disabled', font=("Arial", 10))
        self.text_area.place(x=0, y=0, width=335, height=460)

        self.scrollbar = Scrollbar(frame, command=self.text_area.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text_area['yscrollcommand'] = self.scrollbar.set
        self.btn_paused = Button(self, text="暂停", takefocus=False, command=self.toggle_pause_continue)
        self.btn_paused.place(x=460, y=585, width=50, height=30)
        Button(self, text="清屏", takefocus=False, command=self.clear_log).place(x=600, y=585, width=50, height=30)
        style = Style()
        style.configure("Underline.TLabel", foreground="blue", font=("TkDefaultFont", 10, "underline"))
        label = Label(self, text='?', style="Underline.TLabel", cursor="hand2")
        label.place(x=690, y=585, width=50, height=30)
        label.bind("<Button-1>", self.show_help)

    def show_help(self, event):
        messagebox.showinfo("帮助", "① 打开MS-5005设备 →点击SYSTEM →点击Ethernet →选择Static IP →点击IP Address Edit → 设置与PC同一网段，示例:\nMS-5505:192.168.1.10, \nPC:192.168.1.15\n"
                                   "② 打开工具界面，点击连接按钮，显示 'Succesfully connected to the MS-5005 device.' 表示连接设备成功，如果连接失败，需检查网络连接，或重启5005设备；\n"
                                   "③ 若勾选遍历复选框，会根据选择的分辨率参数与其他参数排列组合，每次都会切换一遍所有参数，若不勾选遍历复选框，则只会第一次切换所有参数，后面只切换分辨率；\n"
                                   "④ 点击运行，开始遍历参数，若出现 'xxx is ok'表示参数切换成功，'xxx switch error'表示切换失败，'xxx not available for switch'则表示不支持此组合参数切换; \n"
                                   "⑤ 运行次数默认'1', 切换间隔时间默认'10s', 可根据实际需求自行设置，运行日志可在界面文本框查看，也可打开同目录下的log文件查看。\n"
                                    "\n                                     --- 工具使用过程中，有任何问题请及时反馈，谢谢！")

    def create_scrollable_checkbox(self, master, checkboxes):
        global checkbox_vars
        """创建一个可滚动的多选框列表框架"""
        frame = Frame(master, style='White.TFrame')

        # 使用Canvas来实现滚动功能
        canvas = Canvas(frame)
        scrollbar = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
        inner_frame = Frame(canvas, style='White.TFrame')

        # 配置Canvas的滚动和大小调整
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner_frame.bind("<Configure>", on_configure)

        # 将inner_frame放入Canvas并绑定滚动
        canvas.create_window((0, 0), window=inner_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        checkbox_vars = []

        # 添加多选框到inner_frame
        for index, checkbox_text in enumerate(checkboxes):
            var = IntVar()
            check_button = Checkbutton(inner_frame, text=checkbox_text, variable=var)
            # 动态切换列
            col_count = index % 2
            # 根据列数调整行布局
            check_button.grid(row=index // 2, column=col_count, sticky='w', padx=(18, 0))
            # 更新列宽度以适应内容
            inner_frame.columnconfigure(col_count, weight=1)
            checkbox_vars.append(var)
            inner_frame.update_idletasks()

        # 布局Canvas和Scrollbar
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        return frame

    def create_resolution_tab(self):
        tab1 = Frame(self.notebook)
        self.notebook.add(tab1, text="    Resolution    ")
        self.resolutions_list = ["640x480p@60", "640x480p@75", "720x480i@60", "720x480p@60", "720x576i@50", "720x576p@50", "800x600p@60", "800x600p@75",
                            "1024x768p@60", "1024x768p@75", "1280x1024p@60", "1280x1024p@75", "1280x720p@25", "1280x720p@29.97", "1280x720p@30", "1280x720p@50",
                            "1280x720p@59.94", "1280x720p@60", "1360x768p@60", "1366x768p@60", "1400x1050p@60", "1440x900p@60", "1440x900p@75", "1600x1200p@60",
                            "1680x1050p@60", "1680x1050pRB", "1920x1080i@50", "1920x1080i@59.94", "1920x1080i@60", "1920x1080p@23.976", "1920x1080p@24", "1920x1080p@25",
                            "1920x1080p@29.97", "1920x1080p@30", "1920x1080p@50", "1920x1080p@59.94", "1920x1080p@60", "1920x1080pRB", "1920x1200pRB", "3840x2160p@23.976",
                            "3840x2160p@24", "3840x2160p@25", "3840x2160p@29.97", "3840x2160p@30", "3840x2160p@50", "3840x2160p@59.94", "3840x2160p@60", "4096x2160p@23.976",
                            "4096x2160p@24", "4096x2160p@25", "4096x2160p@29.97", "4096x2160p@30","4096x2160p@50", "4096x2160p@59.94", "4096x2160p@60"]
        checkbox_frame1 = self.create_scrollable_checkbox(tab1, self.resolutions_list)
        checkbox_frame1.pack(fill=BOTH, expand=True)

    def create_color_tab(self):
        tab2 = Frame(self.notebook)
        self.notebook.add(tab2, text="    Color    ")
        """ 子窗口界面函数，自定义色彩空间，色度采样，色彩深度 """

        # 第一个LabelFrame: 色彩空间
        lf_color_space = LabelFrame(tab2, text="Color Space")
        lf_color_space.pack(padx=10, pady=20, fill=X)

        self.var_color_space = IntVar()
        self.color_spaces = ["RGB", "YCbCr 444", "YCbCr 422", "YCbCr 420", "DVI"]
        for i, space in enumerate(self.color_spaces):
            Radiobutton(lf_color_space, text=space, variable=self.var_color_space, value=i).pack(anchor=W)
        self.var_color_space.set(0)

        # 第二个LabelFrame: 色彩位深
        lf_bits = LabelFrame(tab2, text="Color Depth")
        lf_bits.pack(padx=10, pady=(40, 10), fill=X)

        self.var_bits = IntVar()
        self.bits_values = [8, 10, 12, 16]
        for i, bits in enumerate(self.bits_values):
            Radiobutton(lf_bits, text=bits, variable=self.var_bits, value=i).pack(side ='left')
        # 默认选择8
        self.var_bits.set(0)

    def create_audio_tab(self):
        tab3 = Frame(self.notebook)
        self.notebook.add(tab3, text="    Audio    ")

        # 第一个LabelFrame: Audio Mute
        lf_audio_length = LabelFrame(tab3, text="Audio Mute")
        lf_audio_length.pack(padx=10, pady=8, fill=X)

        self.var_audio_mute = IntVar()
        self.audio_mute_list = ["OFF", "ON"]
        for i, length in enumerate(self.audio_mute_list):
            Radiobutton(lf_audio_length, text=length, variable=self.var_audio_mute, value=i).pack(side=LEFT, padx=70 * i)

        # 第二个LabelFrame: Audio Length
        lf_audio_length = LabelFrame(tab3, text="Audio Length")
        lf_audio_length.pack(padx=10, pady=8, fill=X)

        self.var_audio_length = IntVar()
        self.audio_lengths_list = ["16bits", "20bits", "24bits"]
        for i, length in enumerate(self.audio_lengths_list):
            Radiobutton(lf_audio_length, text=length, variable=self.var_audio_length, value=i).pack(side=LEFT)

        # 第三个LabelFrame: Audio Level
        lf_audio_level = LabelFrame(tab3, text="Audio Level")
        lf_audio_level.pack(padx=10, pady=8, fill=X)

        self.var_audio_level = IntVar()
        self.audio_level_list = [0, 1, 2, 3, 4, 8, 6, 7]
        for i, level in enumerate(self.audio_level_list):
            Radiobutton(lf_audio_level, text=level, variable=self.var_audio_level, value=i).pack(side=LEFT)

        # 第四个LabelFrame: Audio Sample Rate
        lf_audio_sample_rate = LabelFrame(tab3, text="Audio Sample Rate")
        lf_audio_sample_rate.pack(padx=10, pady=8, fill=X)

        self.var_audio_sample = IntVar()
        self.audio_sample_list = ['32KHz', '44.1KHz', '48KHz', '96KHz', '192KHz']
        for i, sample in enumerate(self.audio_sample_list):
            Radiobutton(lf_audio_sample_rate, text=sample, variable=self.var_audio_sample, value=i).pack(side=LEFT)

        # 第五个LabelFrame: Audio Channel Number
        audio_channel_number = LabelFrame(tab3, text="Audio Channel Number")
        audio_channel_number.pack(padx=10, pady=8, fill=X)

        self.var_audio_channel = IntVar()
        self.audio_channel_list = ['2Ch', '2.1Ch', '5.1Ch', '6.1Ch', '7.1Ch']
        for i, channel in enumerate(self.audio_channel_list):
            Radiobutton(audio_channel_number, text=channel, variable=self.var_audio_channel, value=i).pack(side=LEFT)

    def create_tools_tab(self):
        tab4 = Frame(self.notebook)
        self.notebook.add(tab4, text="    HDCP   ")

        # 第一个LabelFrame: TX Hdcp
        lf_tx_hdcp = LabelFrame(tab4, text="TX HDCP")
        lf_tx_hdcp.pack(padx=10, pady=15, fill=X)

        self.var_tx_hdcp = IntVar()
        self.tx_hdcps = ["OFF", "HDCP 1.4", "HDCP 2.2 Type 0", "HDCP 2.2 Type 1"]
        for i, hdcp in enumerate(self.tx_hdcps):
            Radiobutton(lf_tx_hdcp, text=hdcp, variable=self.var_tx_hdcp, value=i).pack(anchor=W)

        # 第二个LabelFrame: RX Hdcp
        lf_rx_hdcp = LabelFrame(tab4, text="RX HDCP")
        lf_rx_hdcp.pack(padx=10, pady=15, fill=X)

        self.var_rx_hdcp = IntVar()
        self.rx_hdcps = ["OFF", "HDCP 1.4", "HDCP 2.2", "HDCP 1.4 & HDCP 2.2"]
        for i, hdcp in enumerate(self.rx_hdcps):
            Radiobutton(lf_rx_hdcp, text=hdcp, variable=self.var_rx_hdcp, value=i).pack(anchor=W)

    def validate_number_input(self, new_value):
        # 此函数检查输入值是否为数字或小数点
        if new_value == "" or new_value.replace(".", "").isdigit():
            return True
        else:
            return False

    def on_invalid_input(self):
        # messagebox.showwarning('警告', 'IP格式错误')
        return True

    def validate_number(self, value):
        return value.isdecimal() or value == ""

    def select_all(self):
        for var in checkbox_vars:
            var.set(1)  # 设置变量为1，选中状态

    def cancel_all(self):
        for var in checkbox_vars:
            var.set(0)  # 设置变量为0，未选中状态

    def get_resolution_checkboxes(self):
        """获取所有选中的复选框的文本和索引"""
        global checkbox_vars
        selected_items = []
        for idx, var in enumerate(checkbox_vars):
            if var.get() == 1:
                selected_items.append(idx)
        return selected_items

    def get_color_checkbox(self):
        # 获取色彩选择
        color_space_selected = self.var_color_space.get()
        color_depth_selected = self.var_bits.get()
        color_list = [color_space_selected, color_depth_selected]
        return color_list

    def get_audio_checkboxes(self):
        # 获取音频的选择
        audio_mute_selected = self.var_audio_mute.get()
        audio_length_selected = self.var_audio_length.get()
        audio_level_selected = self.var_audio_level.get()
        audio_sample_selected = self.var_audio_sample.get()
        audio_channel_selected = self.var_audio_channel.get()
        audio_list = [audio_mute_selected, audio_length_selected, audio_level_selected, audio_sample_selected, audio_channel_selected]
        return audio_list

    def get_hdcp_checkbox(self):
        # 获取TX RX HDCP的选择
        tx_hdcp_selected = self.var_tx_hdcp.get()
        rx_hdcp_selected = self.var_rx_hdcp.get()
        hdcp_list = [tx_hdcp_selected, rx_hdcp_selected]
        return hdcp_list

    def log_message(self, message):
        """ 打印日志消息，输出到控件"""
        logging.info(message)
        self.text_area.configure(state='normal')
        self.text_area.insert(END, message + '\n')
        self.text_area.configure(state='disabled')
        self.text_area.see(END)  # 自动滚动到底部

    def update_from_queue(self):
        """ 获取消息队列 """
        while True:
            try:
                msg = self.message_queue.get(timeout=1)
                if msg is None:  # 结束信号
                    break
                if 'Succesfully connected' in msg:
                    self.update_connection_button_status("connected")  # 更新按钮状态
                self.log_message(msg)
            except Empty:
                pass

    def update_connection_button_status(self, status):
        if status == "connected":
            self.btn_connect.config(text="断开")
            self.btn_connect.config(command=self.disconnect_ip)
            self.btn_run.config(state=NORMAL)
            self.btn_stop.config(state=NORMAL)

        elif status == "disconnected":
            self.btn_connect.config(text="连接")
            self.btn_connect.config(command=self.connect_ip)
            self.btn_run.config(state=DISABLED)
            self.btn_stop.config(state=DISABLED)

    def background_processing(self):
        # 后台运行获取消息队列
        self.processing_thread = threading.Thread(target=self.update_from_queue, daemon=True)
        self.processing_thread.start()

    def connect_ip(self):
        """ 尝试连接仪器的IP地址 """
        input_ip = self.ip_var.get()
        port = self.port
        self.log_message(f">>> Connecting to IP: {input_ip}...")
        threading.Thread(target=self.control.connect, args=(input_ip, port)).start()

    def disconnect_ip(self):
        """ 断开仪器连接 """
        self.control.disconnect()
        self.update_connection_button_status("disconnected")

    def run_instrument(self):
        self.control.running = True
        resolution_select = self.get_resolution_checkboxes()
        color_select = self.get_color_checkbox()
        audio_select = self.get_audio_checkboxes()
        hdcp_select = self.get_hdcp_checkbox()
        checkbox_state = self.iterate_checkbox_var.get()

        # 打印选则的切换参数
        resolution_show = [self.resolutions_list[res] for res in resolution_select]
        color_show = [self.color_spaces[color_select[0]], self.bits_values[color_select[1]]]
        audio_show = [self.audio_mute_list[audio_select[0]], self.audio_lengths_list[audio_select[1]], self.audio_level_list[audio_select[2]],
        self.audio_sample_list[audio_select[3]], self.audio_channel_list[audio_select[4]]]
        hdcp_show = [self.tx_hdcps[hdcp_select[0]], self.rx_hdcps[hdcp_select[1]]]

        self.log_message(f">>> Resolution: {resolution_show}")
        self.log_message(f">>> Color: {color_show}")
        self.log_message(f">>> Audio: {audio_show}")
        self.log_message(f">>> HDCP: {hdcp_show}")

        # 按钮映射指令
        resolution_map = [
        "0x15", "0x16", "0x0", "0x2", "0x1", "0x3", "0x17", "0x18", "0x19", "0x1a",
        "0x1b", "0x1c", "0x9", "0x8", "0x7", "0x6", "0x5", "0x4", "0x1d", "0x1e",
        "0x1f", "0x21", "0x22", "0x20", "0x23", "0x24", "0xc", "0xb", "0xa", "0x14",
        "0x13", "0x12", "0x11", "0x10", "0xf", "0xe", "0x2f", "0x25", "0x26", "0x2e",
        "0x2d", "0x2c", "0x2b", "0x2a", "0x29", "0x28", "0x27", "0x37", "0x36", "0x35",
        "0x34", "0x33", "0x32", "0x31", "0x30"]
        color_space_map = ["0x1", "0x2", "0x3", "0x4", "0x0"]
        color_depth_map = ["0x0", "0x1", "0x2", "0x3"]
        audio_mute_map = ["0x0", "0x1"]
        audio_length_map = ["0x2", "0x1", "0x0"]
        audio_level_map = ["0x0", "0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7"]
        audo_rate_map = ["0x3", "0x4", "0x0", "0x1", "0x2"]
        audio_channel_map = ["0x0", "0x1", "0x2", "0x3", "0x4"]
        tx_hdcp_map = ["0x0", "0x1", "0x2", "0x3"]
        rx_hdcp_map = ["0x0", "0x1", "0x2", "0x3"]

        resolution_list = [resolution_map[r] for r in resolution_select]
        color_list = [color_space_map[color_select[0]], color_depth_map[color_select[1]]]
        audio_list = [audio_mute_map[audio_select[0]], audio_length_map[audio_select[1]], audio_level_map[audio_select[2]], audo_rate_map[audio_select[3]], audio_channel_map[audio_select[4]]]
        hdcp_list = [tx_hdcp_map[hdcp_select[0]], rx_hdcp_map[hdcp_select[1]]]

        # 运行次数, 间隔时间, 运行方式
        run_times = self.run_times_entry.get()
        run_interval = self.interval_entry.get()
        run_mode = self.mode_var.get()
        self.log_message(f">>> Times: {run_times}")
        self.log_message(f">>> Waiting time: {run_interval}")
        self.log_message(f">>> Switching mode: {run_mode}切换")
        self.log_message(f">>> Running...")

        fun_parameters = (resolution_list, color_list, audio_list, hdcp_list, resolution_show, run_times, run_interval, run_mode, checkbox_state)
        # 子线程运行，发送对应指令
        threading.Thread(target=self.control.run_test, args=(fun_parameters)).start()

    def toggle_pause_continue(self):
        if self.paused:
            self.continue_test()
            self.btn_paused.config(text="暂停")
            self.paused = False
        else:
            self.pause_test()
            self.btn_paused.config(text="继续")
            self.paused = True

    def pause_test(self):
        # 添加暂停逻辑
        if not self.control.pause_event.is_set():
            self.log_message(">>> Pause testing...")
            self.control.pause_event.set()

    def continue_test(self):
        # 添加继续逻辑
        if self.control.pause_event.is_set():
            self.log_message(">>> Continue testing...")
            self.control.pause_event.clear()

    def stop_test(self):
        self.control.running = False
        self.log_message('Stop testing.')

    def clear_log(self):
        self.text_area.config(state=NORMAL)
        self.text_area.delete(1.0, END)
        self.text_area.config(state=DISABLED)

if __name__ == "__main__":
    nw = datetime.now().strftime("%Y%m%d%H%M%S")
    log_name = f'ms_5005_{nw}.log'
    # 配置日志格式
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s',  # 日志格式
                        datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.FileHandler(log_name)])
    win = WinGUI()
    win.mainloop()