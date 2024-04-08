# -*- coding: utf-8 -*-
# Author: Lay.zhang
# Date: 2024/3/11

from time import sleep, time
import uiautomation as auto
import logging
import datetime
import traceback

def click_device_menu(qgnss_name, module_name, download_path):
    global success, failures
    # QGNSS 烧录点击
    window = auto.WindowControl(searchDepth=1, Name=qgnss_name)
    if window.Exists():
        window.SetActive()
        logging.info('-- 点击QGNSS菜单栏 - Device')
        device_menu = window.MenuItemControl(Name='Device')
        device_menu.Click(simulateMove=False)
        sleep(0.2)
        logging.info('-- 点击QGNSS菜单栏 - Connect')
        connect_menu = window.MenuItemControl(Name='Connect')
        connect_menu.Click(simulateMove=False)
        sleep(0.5)
        logging.info('-- 点击QGNSS状态栏 - RTS')
        rts_button = window.CheckBoxControl(Name='RTS')
        rts_button.Click(simulateMove=False)
        sleep(0.5)
        logging.info('-- 点击QGNSS状态栏 - DTR')
        dtr_button = window.CheckBoxControl(Name='DTR')
        dtr_button.Click(simulateMove=False)
        sleep(0.5)
        logging.info('-- 点击QGNSS菜单栏 - Tools')
        tool_menu = window.MenuItemControl(Name='Tools')
        tool_menu.Click(simulateMove=False)
        sleep(0.2)
        logging.info('-- 点击QGNSS菜单栏 - Firmware Download')
        download_menu = window.MenuItemControl(Name='Firmware Download')
        download_menu.Click(simulateMove=False)
        sleep(1)
        sub_window = auto.WindowControl(searchFromControl=window, Name=f"Module: {module_name}")
        if sub_window:
            sleep(0.2)
            logging.info('-- Ctrl + A 全选删除，已有文件路径')
            edit1_control = sub_window.EditControl(ClassName="QLineEdit", Name="")
            edit1_control.SetFocus()
            edit1_control.SendKeys('{Ctrl}a')
            sleep(0.2)
            # 删除已存在的路径
            edit1_control.SendKeys('{DEL}')
            sleep(0.2)
            logging.info(f'-- QLineEdit 填充路径:{download_path}')
            edit1_control.SendKeys(download_path)
            sleep(3)
            logging.info('-- 点击下载开始按钮')
            sub_window.SendKeys('{Ctrl}r')
            sleep(1)
            qtextedit = sub_window.EditControl(ClassName="QTextEdit")
            success_text = f"{module_name}:BOOT: Success"
            et_time = time() + 60
            while et_time > time():
                logging.info('qtextedit.GetValuePattern().Value')
                if success_text in qtextedit.GetValuePattern().Value:
                    break
                else:
                    sleep(2)
            else:
                logging.debug('-- 下载失败, 60s内未识别到模块烧录成功语句')
                print('-- 下载失败, 60s内未识别到模块烧录成功语句')
                failures += 1
                return False
            logging.info('-- 点击关闭下载窗口')
            close_button = sub_window.ButtonControl(Name='关闭')
            close_button.Click(simulateMove=False)
            sleep(0.5)
            logging.info('-- 双击RTS, 拉低拉高信号, 使模块正常输出')
            rts_button.DoubleClick(simulateMove=False)
            sleep(1)
            output_edit = window.EditControl(ClassName="QPlainTextEdit")
            et1_time = time() + 20
            while et1_time > time():
                nmea_text = output_edit.GetValuePattern().Value
                logging.info(nmea_text)
                if 'RMC' in nmea_text and 'GGA' in nmea_text and 'GSV' in nmea_text:
                    break
                else:
                    sleep(1)
            else:
                logging.debug('-- 20s内未识别到NMEA语句输出')
                print('-- 20s内未识别到NMEA语句输出')
                failures += 1
                return False
            sleep(0.5)
            logging.info('-- 点击RTS')
            rts_button.Click(simulateMove=False)
            sleep(0.2)
            logging.info('-- 点击DTR')
            dtr_button.Click(simulateMove=False)
            sleep(0.5)
            logging.info('-- 点击点击QGNSS菜单栏 - Device, 断开连接')
            device_menu.Click(simulateMove=False)
            sleep(0.2)
            connect_menu.Click(simulateMove=False)
            sleep(0.2)
            return True
        else:
            failures += 1
            logging.debug('-- 未找到版本烧录窗口')
            print("-- 未找到版本烧录窗口")
    else:
        logging.debug('-- 未找到主窗口 QGNSS V1.10')
        print("-- 未找到主窗口 QGNSS V1.10")

def main():
    global success, failures
    loop_nums = 2  # 循环次数
    gnss_name = 'QGNSS V1.10' # QGNSS 版本名称
    oc_name = 'LC760Z' # 模块名称
    download_path1 = r'D:/Personal Information/04-Flash File/HUADA/LC760ZAANR01A02V02/LC760ZAANR01A02V02.cyfm' # 下载路径1
    download_path2 = r'D:/Personal Information/04-Flash File/HUADA/LC760ZAANR01A02V08/LC760ZAANR01A02V08.cyfm' # 下载路径2
    nt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # log 日期
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s]:%(message)s', filename=f'log_{nt}.log')  # 记录Log
    try:
        print('脚本开始运行~')
        logging.info('脚本开始运行')
        for t in range(1, loop_nums+1):
            print(f'***************** 第{t}次循环 *****************')
            logging.info(f'***************** 第{t}次循环 *****************')
            download1_status = click_device_menu(gnss_name, oc_name, download_path1)
            if not download1_status:
                break
            download2_status = click_device_menu(gnss_name, oc_name, download_path2)
            if not download2_status:
                break
            if download1_status and download2_status:
                success +=1
            print(f'-- 循环次数：{t}，成功：{success}，失败：{failures}')
            logging.info(f'-- 循环次数：{t}，成功：{success}，失败：{failures}')
            sleep(2)
    except Exception:
        logging.debug(f'-- Error -{traceback.format_exc()}')
        print(f'-- Error -{traceback.format_exc()}')
    finally:
        logging.info('下载压力测试结束。')
        print('下载压力测试结束。')

success, failures = 0, 0
main()




