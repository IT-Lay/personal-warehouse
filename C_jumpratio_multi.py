import matplotlib.pyplot as plt
from datetime import datetime
import re
import matplotlib
import sys
import os
import traceback

def jump_ration():
    print('C_jumpratio_multi script start')
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
    # 获取当前时间
    nt = datetime.now()
    nt_year = nt.year
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 提取要素
        all_nums, utc_time, nums, utc = 0, 0, 0, 0
        x_data, period, set_data = [], [], []
        g_l1_ob, r_ob, e_l1_ob, c_l1_ob, g_l5_ob, e_l5_ob, c_l5_ob = [], [], [], [], [], [], []
        g_l1_data, r_data, e_l1_data, c_l1_data, g_l5_data, e_l5_data, c_l5_data = [], [], [], [], [], [], []
        jump_data = []

        # 正则匹配非空数据, "G05  21163875.742   111216917.9221"
        regex = re.compile('\S+')
        # 正则匹配空数据, "C16                                                                  37684088.326   151738200.966       -1042.103          40.000  "
        regex_space = re.compile('\s+')

        # 遍历文件
        for line in lines:
            # 读取到UTC时间
            if line.strip().startswith('> ' + '%d' % nt_year):
                reg_utc = regex.findall(line)
                period.append(line.strip()[2:29])
                all_nums = int(line.strip().split('.')[1][-2:])  # 获取总的卫星个数
                x_data.append(float(reg_utc[4] + reg_utc[5] + reg_utc[6][0:5]))
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

                    # 遍历数据
                    for i in range(len(jump_data)):
                        # 判断句首
                        re_all = regex.findall(jump_data[i])
                        re_space = regex_space.findall(jump_data[i])
                        if len(re_all) == 1:
                            continue
                        # GPS
                        if re_all[0][0] == 'G':
                            # L1 频段周跳比计算，无值或者整数的数据忽略不计
                            if len(re_space[1]) < 5:
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
                            # 'C16                                                                  37680208.615   151722582.619       -1039.689          42.000' 记作L5
                            elif len(re_space[1]) > 50:
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
                            if len(re_space[1]) < 5:
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
                            elif len(re_space[1]) > 50:
                                if '.' in re_all[2]:
                                    e_l5_num += 1
                                    if len(re_all[2].split('.')[1]) == 4:
                                        e_l5_jump += 1
                        # BeiDou
                        elif re_all[0][0] == 'C':
                            if len(re_space[1]) < 5:
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
                            elif len(re_space[1]) > 50:
                                if '.' in re_all[2]:
                                    c_l5_num += 1
                                    if len(re_all[2].split('.')[1]) == 4:
                                        c_l5_jump += 1
                    if g_l1_num != 0:
                        g_l1_data.append(float(f'{(g_l1_jump / g_l1_num):.4f}'))
                        g_l1_ob.append(g_l1_num - g_l1_jump)
                    else:
                        g_l1_data.append(0)
                        g_l1_ob.append(0)
                    if g_l5_num != 0:
                        g_l5_data.append(float(f'{(g_l5_jump / g_l5_num):.4f}'))
                        g_l5_ob.append(g_l5_num - g_l5_jump)
                    else:
                        g_l5_data.append(0)
                        g_l5_ob.append(0)
                    if r_num != 0:
                        r_data.append(float(f'{(r_jump / r_num):.4f}'))
                        r_ob.append(r_num - r_jump)
                    else:
                        r_data.append(0)
                        r_ob.append(0)
                    if e_l1_num != 0:
                        e_l1_data.append(float(f'{(e_l1_jump / e_l1_num):.4f}'))
                        e_l1_ob.append(e_l1_num - e_l1_jump)
                    else:
                        e_l1_data.append(0)
                        e_l1_ob.append(0)
                    if e_l5_num != 0:
                        e_l5_data.append(float(f'{(e_l5_jump / e_l5_num):.4f}'))
                        e_l5_ob.append(e_l5_num - e_l5_jump)
                    else:
                        e_l5_data.append(0)
                        e_l5_ob.append(0)
                    if c_l1_num != 0:
                        c_l1_data.append(float(f'{(c_l1_jump / c_l1_num):.4f}'))
                        c_l1_ob.append(c_l1_num - c_l1_jump)
                    else:
                        c_l1_data.append(0)
                        c_l1_ob.append(0)
                    if c_l5_num != 0:
                        c_l5_data.append(float(f'{(c_l5_jump / c_l5_num):.4f}'))
                        c_l5_ob.append(c_l5_num - c_l5_jump)
                    else:
                        c_l5_data.append(0)
                        c_l5_ob.append(0)
                    nums = 0
                    jump_data.clear()
        return [x_data, g_l1_data, g_l5_data, r_data, e_l1_data, e_l5_data, c_l1_data, c_l5_data, g_l1_ob, g_l5_ob, r_ob, e_l1_ob, e_l5_ob, c_l1_ob, c_l5_ob]

def drawing(data1, data2):
    p_titles= ['GPS L1 周跳比数量', 'GPS L5 周跳比数量', 'GLO L1 周跳比数量', 'GAL L1 周跳比数量', 'GAL L5 周跳比数量', 'BDS L1 周跳比数量', 'BDS L5 周跳比数量']
    v_titles= ['GPS L1 可观测量', 'GPS L5 可观测量', 'GLO L1 可观测量', 'GAL L1 可观测量', 'GAL L5 可观测量', 'BDS L1 可观测量', 'BDS L5 可观测量']
    for d in range(7):
        # 生成图形代码GPS L1
        fig, axs = plt.subplots(2, 1, figsize=(10, 8))

        # 设置X轴的刻度范围和显示的刻度点
        num_ticks = 10  # 刻度点数量
        step = len(data1[0]) // (num_ticks - 1)  # 计算步长

        # 记录周跳比数量
        print(f'{path1} {p_titles[d]}：{data1[d+1].count(1.0)}\n{path2} {p_titles[d]}：{data2[d+1].count(1.0)}')

        # 创建图表
        axs[0].plot(data1[0], data1[d+1], "b-")
        axs[0].plot(data2[0], data2[d+1], "y-")
        axs[0].set_title(p_titles[d])
        axs[1].plot(data1[0], data1[d+8], "b-")
        axs[1].plot(data2[0], data2[d+8], "y-")
        axs[1].set_title(v_titles[d])

        # 添加标题和标签
        axs[0].set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])  # 设置Y轴刻度
        axs[0].set_ylim(0, 1)  # 设置Y轴范围
        axs[1].set_ylim(0, )
        # 生成要显示的刻度点的位置和标签
        axs[0].set_xticks([data1[0][i] for i in range(0, len(data1[0]), step)])
        axs[0].set_xlim(data1[0][0], data1[0][-1])
        axs[1].set_xticks([data1[0][i] for i in range(0, len(data1[0]), step)])
        plt.legend([os.path.basename(path1), os.path.basename(path2)])
        # 调整子图之间的距离
        fig.tight_layout()
        # 显示图表
        plt.show()

path1 = sys.argv[1]
path2 = sys.argv[2]
jump_ration()
