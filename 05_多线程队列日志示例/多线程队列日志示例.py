import serial
import threading
import time
import logging
import datetime
from queue import Queue, Empty

# 配置日志
nt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # log 日期
logger = logging.getLogger('NMEA_Logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(f'nmea_{nt}.log')
formatter = logging.Formatter('[%(asctime)s]: %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger_script = logging.getLogger('Script_Logger')
logger_script.setLevel(logging.INFO)
script_handler = logging.FileHandler(f'script_{nt}.log')
script_handler.setFormatter(formatter)
logger_script.addHandler(script_handler)


# 创建一个队列来存储接收到的消息
message_queue = Queue()
# 全局变量用于控制线程的执行
keep_running, keep_reading = True, True

def read_from_port(ser):
    while keep_reading:
        reading = ser.readline().decode('utf-8', errors= 'ignore').strip()
        if reading:
            logger.info(reading)
            message_queue.put(reading)

def send_command(ser, command):
    ser.write(command.encode('utf-8'))
    logger_script.info(f"发送指令: {command[:-2]}")

def send_speed_command(ser, command, max_retries=5, delay=0.1):
    global keep_running
    if keep_running:
        retry_count = 0
        while retry_count < max_retries:
            try:
                ser.write(command)  # 发送指令
                time.sleep(delay)
                break  # 成功发送后跳出循环
            except serial.serialutil.SerialTimeoutException:
                retry_count += 1
                time.sleep(delay)
        if retry_count == max_retries:
            logger_script.info("发送速度指令，超过最大重试次数，发送失败")
            return False
    return True

def check_response(expected_response, timeout=3):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = message_queue.get(timeout=timeout - (time.time() - start_time))
            if expected_response in response:
                return True
        except Empty:
            break
    return False

def check1(ser):
    send_command(ser, "$PQTMCFGDRMODE,0*53\r\n")
    if not check_response("$PQTMDRMODE,0,0*0D"):
        print("check1 响应失败")
        logger_script.info("check1 响应失败")
        return False
    print("check1 响应成功")
    logger_script.info("check1 响应成功")
    return True

def check2(ser):
    send_command(ser, "$PSTMGETPAR,1227*25\r\n")
    if not check_response("$PSTMSETPAR,1227,0x040100cd*57"):
        print("check2 响应失败")
        logger_script.info("check2 响应失败")
        return False
    print("check2 响应成功")
    logger_script.info("check2 响应成功")
    return True

def check3(ser):
    send_command(ser, "$PSTMGETPAR,1201*21\r\n")
    if not check_response("$PSTMSETPAR,1201,0x00180056*5B"):
        print("check3 响应失败")
        logger_script.info("check3 响应失败")
        return False
    print("check3 响应成功")
    logger_script.info("check3 响应成功")
    return True

def check4(ser):
    send_command(ser, "$PQTMCFGDRMODE,0*53\r\n")
    if not check_response("$PQTMDRMODE,0,2*0F"):
        print("check4 响应失败")
        logger_script.info("check4 响应失败")
        return False
    print("check4 响应成功")
    logger_script.info("check4 响应成功")
    return True

def check5(ser):
    send_command(ser, "$PSTMGETPAR,1227*25\r\n")
    if not check_response("$PSTMSETPAR,1227,0x040103cd*54"):
        print("check5 响应失败")
        logger_script.info("check5 响应失败")
        return False
    print("check5 响应成功")
    logger_script.info("check5 响应成功")
    return True

def check6(ser):
    send_command(ser, "$PSTMGETPAR,1201*21\r\n")
    if not check_response("$PSTMSETPAR,1201,0x00180356*58"):
        print("check6 响应失败")
        logger_script.info("check6 响应失败")
        return False
    print("check6 响应成功")
    logger_script.info("check6 响应成功")
    return True


def main():
    global keep_running, keep_reading
    loop_nums = 3  # 循环次数
    port = 'COM4'  # 串口号
    baudrate = 115200  # 波特率
    check1_fails, check2_fails, check3_fails, check4_fails, check5_fails, check6_fails, reset1_fails, reset2_fails = 0, 0, 0, 0, 0, 0, 0, 0
    check1_succes, check2_succes, check3_succes, check4_succes, check5_succes, check6_succes, reset1_succes, reset2_succes = 0, 0, 0, 0, 0, 0, 0, 0

    with serial.Serial(port, baudrate, timeout=2, write_timeout=2) as ser:
        ser.flushInput()
        ser.setDTR(1)
        first_time = time.time()
        print('模块上电开机')
        logger_script.info('模块上电开机')
        time.sleep(3)
        print('脚本开始运行~')
        logger_script.info('脚本开始运行')
        # 创建并启动接收线程
        thread1 = threading.Thread(target=read_from_port, args=(ser,))
        thread1.start()
        for t in range(1, loop_nums):
            print(f'***************** 第{t}次循环 *****************')
            logger_script.info(f'***************** 第{t}次循环 *****************')
            # 进行循环测试
            if check1(ser):
                check1_succes +=1
            else:
                check1_fails +=1
            time.sleep(0.01)
            if check2(ser):
                check2_succes += 1
            else:
                check2_fails += 1
            time.sleep(0.01)
            if check3(ser):
                check3_succes += 1
            else:
                check3_fails += 1
            time.sleep(0.01)

            while True:
                end_time = time.time()
                # 判断循环次数，减去上电的时间
                if t==1:
                    time_out = end_time - first_time
                else:
                    time_out = end_time - third_time
                if time_out >=11:
                    break
            send_command(ser, "$PQTMCFGDRMODE,1,2*4C\r\n")
            time.sleep(0.01)
            send_command(ser, "$PSTMSAVEPAR*58\r\n")
            thread2 = threading.Thread(target=send_speed_command, args=(ser, b'$PQTMVEHMSG,1,0,10*36\r\n',))
            thread2.start()
            time.sleep(1)
            send_command(ser, "$PSTMSETCONSTMASK,143*13\r\n")
            time.sleep(15)
            send_command(ser, "$PSTMSETPAR,1201,300,1*37\r\n")
            time.sleep(0.01)
            send_command(ser, "$PSTMSAVEPAR*58\r\n")
            time.sleep(1)
            logger_script.info('模块断电重启')
            ser.setDTR(0)
            # 设置标志，指示线程停止发送
            keep_running = False
            thread2.join()
            logger_script.info('停止发送指令：$PQTMVEHMSG,1,0,10*36')
            time.sleep(0.5)
            ser.setDTR(1)
            ser.flushInput()
            second_time = time.time()
            if check_response("GGA"):
                reset1_succes +=1
                logger_script.info('①断电重启后，有GGA语句输出')
            else:
                reset1_fails += 1
                logger_script.info('①断电重启后，无GGA语句输出')
            while True:
                end_time = time.time()
                if end_time - second_time >= 3:
                    break
            if check4(ser):
                check4_succes += 1
            else:
                check4_fails += 1
            time.sleep(0.01)
            if check5(ser):
                check5_succes += 1
            else:
                check5_fails += 1
            time.sleep(0.01)
            if check6(ser):
                check6_succes += 1
            else:
                check6_fails += 1
            time.sleep(0.01)
            while True:
                end_time = time.time()
                if end_time - second_time >=11:
                    break
            send_command(ser, "$PQTMCFGDRMODE,1,0*4E\r\n")
            time.sleep(0.01)
            send_command(ser, "$PSTMSAVEPAR*58\r\n")
            time.sleep(1)
            send_command(ser, "$PSTMSETCONSTMASK,15*21\r\n")
            time.sleep(15)
            send_command(ser, "$PSTMSETPAR,1201,300,2*34\r\n")
            time.sleep(0.01)
            send_command(ser, "$PSTMSAVEPAR*58\r\n")
            time.sleep(1)
            logger_script.info('模块断电重启')
            ser.setDTR(0)
            time.sleep(0.5)
            ser.setDTR(1)
            third_time = time.time()
            ser.flushInput()
            if check_response("GGA"):
                reset2_succes += 1
                logger_script.info('②断电重启后，有GGA语句输出')
            else:
                reset2_fails += 1
                logger_script.info('②断电重启后，有GGA语句输出')
            print(f'循环次数：{t}, Reset1_成功：{reset1_succes}, Reset1_失败：{reset1_fails}, Reset2_成功：{reset2_succes}, Reset2_失败：{reset2_fails}')
            time.sleep(3)
        keep_reading = False
        thread1.join()

if __name__ == "__main__":
    main()
