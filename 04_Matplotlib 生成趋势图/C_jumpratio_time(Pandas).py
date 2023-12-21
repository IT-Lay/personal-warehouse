import matplotlib.pyplot as plt
import re
import matplotlib
import sys
import os
import traceback
import pandas as pd
import matplotlib.dates as mdates


def jump_ration():
    print('C_jumpratio_time script start')
    matplotlib.rc("font", family='Microsoft YaHei')
    try:
        # 读取数据文件
        path1_data = read_file(path1)
        path2_data = read_file(path2)
        # 生成趋势图
        drawing(path1_data, path2_data)
    except Exception:
        print(" -- Error -- {}".format(traceback.format_exc()))
    finally:
        print("Script end")

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 提取要素
        all_nums, utc_time, nums, utc = 0, 0, 0, 0
        period = []
        x_gp_l1, x_gp_l5, x_gl_l1, x_ga_l1, x_ga_l5, x_gb_l1, x_gb_l5 = [], [], [], [], [], [], []
        g_l1_ob, r_ob, e_l1_ob, c_l1_ob, g_l5_ob, e_l5_ob, c_l5_ob = [], [], [], [], [], [], []
        g_l1_data, r_data, e_l1_data, c_l1_data, g_l5_data, e_l5_data, c_l5_data = [], [], [], [], [], [], []
        gp_l1_datetime, gp_l5_datetime, gl_l1_datetime, ga_l1_datetime, ga_l5_datetime, gb_l1_datetime, gb_l5_datetime = [], [], [], [], [], [], []
        jump_data = []

        # 正则匹配非空数据, "G05  21163875.742   111216917.9221"
        regex = re.compile('\S+')
        # 正则匹配空数据, "C16               37684088.326   151738200.966       -1042.103          40.000  "
        regex_space = re.compile('\s+')

        # 遍历文件
        for line in lines:
            # 读取到UTC时间
            if line.strip().startswith('> '):
                reg_utc = regex.findall(line)
                period.append(line.strip()[2:29])
                all_nums = int(line.strip().split('.')[1][-2:])  # 获取总的卫星个数
                utc = 1
            elif utc == 1:
                jump_data.append(line)
                nums += 1
                # 读取UTC一整段数据， nums 数据行数
                if nums >= all_nums:
                    utc = 0
                    # 数据置0
                    g_l1_jump, r_jump, e_l1_jump, c_l1_jump = 0, 0, 0, 0
                    g_l5_jump, e_l5_jump, c_l5_jump = 0, 0, 0
                    g_l1_num, r_num, e_l1_num, c_l1_num = 0, 0, 0, 0
                    g_l5_num, e_l5_num, c_l5_num = 0, 0, 0
                    utc_string = reg_utc[4] + ':' + reg_utc[5] + ':' + reg_utc[6][0:4]
                    # 遍历数据
                    for i in range(len(jump_data)):
                        # 判断句首
                        re_all = regex.findall(jump_data[i])
                        re_space = regex_space.findall(jump_data[i])
                        if len(re_all) == 1:
                            continue
                        # GPS + QZSS
                        if re_all[0][0] == 'G':
                            # L1 频段周跳比计算，无值或者整数的数据忽略不计
                            if len(re_space[0]) < 5:
                                if len(re_all) > 4:
                                    if '.' in re_all[2]:
                                        g_l1_num += 1
                                        if len(re_all[2].split('.')[1]) == 4:
                                            g_l1_jump += 1
                                # L5 频段周跳比计算
                                if len(re_all) > 7:
                                    if '.' in re_all[6]:
                                        g_l5_num += 1
                                        if len(re_all[6].split('.')[1]) == 4:
                                            g_l5_jump += 1
                            # 'C16                       37680208.615   151722582.619       -1039.689          42.000' 记作L5
                            elif len(re_space[0]) > 50:
                                if '.' in re_all[2]:
                                    g_l5_num += 1
                                    if len(re_all[2].split('.')[1]) == 4:
                                        g_l5_jump += 1
                        # GLONASS
                        elif re_all[0][0] == 'R':
                            if len(re_all) > 4:
                                if '.' in re_all[2]:
                                    r_num += 1
                                    if len(re_all[2].split('.')[1]) == 4:
                                        r_jump += 1
                        # Galileo
                        elif re_all[0][0] == 'E':
                            if len(re_space[0]) < 5:
                                if len(re_all) > 4:
                                    if '.' in re_all[2]:
                                        e_l1_num += 1
                                        if len(re_all[2].split('.')[1]) == 4:
                                            e_l1_jump += 1
                                # L5 频段周跳比计算
                                if len(re_all) > 7:
                                    if '.' in re_all[6]:
                                        e_l5_num += 1
                                        if len(re_all[6].split('.')[1]) == 4:
                                            e_l5_jump += 1
                            elif len(re_space[0]) > 50:
                                if '.' in re_all[2]:
                                    e_l5_num += 1
                                    if len(re_all[2].split('.')[1]) == 4:
                                        e_l5_jump += 1
                        # BeiDou
                        elif re_all[0][0] == 'C':
                            if len(re_space[0]) < 5:
                                if len(re_all) > 4:
                                    if '.' in re_all[2]:
                                        c_l1_num += 1
                                        if len(re_all[2].split('.')[1]) == 4:
                                            c_l1_jump += 1
                                if len(re_all) > 7:
                                    if '.' in re_all[6]:
                                        c_l5_num += 1
                                        if len(re_all[6].split('.')[1]) == 4:
                                            c_l5_jump += 1
                            elif len(re_space[0]) > 50:
                                if '.' in re_all[2]:
                                    c_l5_num += 1
                                    if len(re_all[2].split('.')[1]) == 4:
                                        c_l5_jump += 1
                        # QZSS
                        elif re_all[0][0] == 'J' and g_l1_num > 0:
                            # L1 频段周跳比计算，无值或者整数的数据忽略不计
                            if len(re_space[0]) < 5:
                                if len(re_all) > 4:
                                    if '.' in re_all[2]:
                                        g_l1_num += 1
                                        if len(re_all[2].split('.')[1]) == 4:
                                            g_l1_jump += 1
                                if len(re_all) > 7:
                                        if '.' in re_all[6]:
                                            if re_all[0][0] == 'J' and g_l5_num > 0:
                                                g_l5_num += 1
                                                if len(re_all[6].split('.')[1]) == 4:
                                                    g_l5_jump += 1
                            elif len(re_space[0]) > 50:
                                if '.' in re_all[2]:
                                    if re_all[0][0] == 'J' and g_l5_num > 0:
                                        g_l5_num += 1
                                        if len(re_all[2].split('.')[1]) == 4:
                                            g_l5_jump += 1
                    if g_l1_num != 0:
                        x_gp_l1.append(utc_string)
                        g_l1_data.append(float(f'{(g_l1_jump / g_l1_num):.4f}'))
                        g_l1_ob.append(g_l1_num - g_l1_jump)
                    if g_l5_num != 0:
                        x_gp_l5.append(utc_string)
                        g_l5_data.append(float(f'{(g_l5_jump / g_l5_num):.4f}'))
                        g_l5_ob.append(g_l5_num - g_l5_jump)
                    if r_num != 0:
                        x_gl_l1.append(utc_string)
                        r_data.append(float(f'{(r_jump / r_num):.4f}'))
                        r_ob.append(r_num - r_jump)
                    if e_l1_num != 0:
                        x_ga_l1.append(utc_string)
                        e_l1_data.append(float(f'{(e_l1_jump / e_l1_num):.4f}'))
                        e_l1_ob.append(e_l1_num - e_l1_jump)
                    if e_l5_num != 0:
                        x_ga_l5.append(utc_string)
                        e_l5_data.append(float(f'{(e_l5_jump / e_l5_num):.4f}'))
                        e_l5_ob.append(e_l5_num - e_l5_jump)
                    if c_l1_num != 0:
                        x_gb_l1.append(utc_string)
                        c_l1_data.append(float(f'{(c_l1_jump / c_l1_num):.4f}'))
                        c_l1_ob.append(c_l1_num - c_l1_jump)
                    if c_l5_num != 0:
                        x_gb_l5.append(utc_string)
                        c_l5_data.append(float(f'{(c_l5_jump / c_l5_num):.4f}'))
                        c_l5_ob.append(c_l5_num - c_l5_jump)
                    nums = 0
                    jump_data.clear()
        if len(x_gp_l1) !=0:
            gp_l1_datetime = pd.to_datetime(x_gp_l1, format='%H:%M:%S.%f')
        if len(x_gp_l5) != 0:
            gp_l5_datetime = pd.to_datetime(x_gp_l5, format='%H:%M:%S.%f')
        if len(x_gl_l1) != 0:
            gl_l1_datetime = pd.to_datetime(x_gl_l1, format='%H:%M:%S.%f')
        if len(x_ga_l1) != 0:
            ga_l1_datetime = pd.to_datetime(x_ga_l1, format='%H:%M:%S.%f')
        if len(x_ga_l1) != 0:
            ga_l5_datetime = pd.to_datetime(x_ga_l5, format='%H:%M:%S.%f')
        if len(x_gb_l1) != 0:
            gb_l1_datetime = pd.to_datetime(x_gb_l1, format='%H:%M:%S.%f')
        if len(x_gb_l5) != 0:
            gb_l5_datetime = pd.to_datetime(x_gb_l5, format='%H:%M:%S.%f')
        return [gp_l1_datetime, gp_l5_datetime, gl_l1_datetime, ga_l1_datetime, ga_l5_datetime, gb_l1_datetime, gb_l5_datetime, g_l1_data, g_l5_data, r_data, e_l1_data, e_l5_data, c_l1_data, c_l5_data, g_l1_ob, g_l5_ob, r_ob, e_l1_ob, e_l5_ob, c_l1_ob, c_l5_ob]

def drawing(data1, data2):
    p_titles= ['GPS L1 周跳比', 'GPS L5 周跳比', 'GLO L1 周跳比', 'GAL L1 周跳比', 'GAL L5 周跳比', 'BDS L1 周跳比', 'BDS L5 周跳比']
    v_titles= ['GPS L1 可观测量', 'GPS L5 可观测量', 'GLO L1 可观测量', 'GAL L1 可观测量', 'GAL L5 可观测量', 'BDS L1 可观测量', 'BDS L5 可观测量']
    for d in range(7):
        # 生成图形代码
        fig, axs = plt.subplots(2, 1, figsize=(10, 8))

        # 记录周跳比数量
        print(f'{os.path.basename(path1)} {p_titles[d][0:6]} 全周跳数量：{data1[d+7].count(1.0)}\n{os.path.basename(path2)} {p_titles[d][0:6]} 全周跳数量：{data2[d+7].count(1.0)}')
        # 记录可观测量数量
        print(f'{os.path.basename(path1)} {p_titles[d][0:6]} 可见卫星数量：{sum(data1[d+14])}\n{os.path.basename(path2)} {p_titles[d][0:6]} 可见卫星数量：{sum(data2[d+14])}\n')

        # 创建图表,设置颜色
        axs[0].plot(data1[d], data1[d+7], "b-")
        axs[0].plot(data2[d], data2[d+7], "y-")
        axs[1].plot(data1[d], data1[d+14], "b-")
        axs[1].plot(data2[d], data2[d+14], "y-")

        # 设置X轴刻度格式
        # 自动选择日期时间刻度
        axs[0].xaxis.set_major_locator(mdates.AutoDateLocator())
        axs[1].xaxis.set_major_locator(mdates.AutoDateLocator())
        # 时间格式转换
        axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))

        # 添加标题和标签
        axs[0].set_title(p_titles[d])
        axs[1].set_title(v_titles[d])

        # Y轴显示的刻度点的位置和标签
        yticks_1 = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        axs[0].set_yticks(yticks_1)  # 设置Y轴刻度
        axs[0].set_yticklabels([str(y) for y in yticks_1])
        axs[0].set_ylim(0, 1)  # 设置Y轴范围
        axs[1].set_ylim(0, )

        # X轴显示的刻度点的位置和标签
        if len(data1[d]) != 0:
            axs[0].set_xlim(data1[d][0], data1[d][-1])
        if len(data2[d]) != 0:
            axs[1].set_xlim(data2[d][0], data2[d][-1])
        plt.legend([os.path.basename(path1), os.path.basename(path2)])

        # 添加平移,缩放
        fig.canvas.toolbar.pan()
        fig.canvas.toolbar.zoom()

        # 调整子图之间的距离
        fig.tight_layout()

        # 显示图表
        plt.show()

path1 = sys.argv[1]
path2 = sys.argv[2]
jump_ration()
