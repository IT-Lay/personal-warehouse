from datetime import datetime
import paramiko
import traceback
import time
import os

def ssh_command(ip, port, username, password, remote_filepath, local_filepath):
    # 创建 SSH 客户端实例
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 连接到树莓派
    client.connect(ip, port, username, password)

    # 执行命令
    shell = client.invoke_shell()
    command_list = ['su root', 'password', 'pip uninstall liteapi', 'y', 'pip install git+http://xxx.xxx.xx.134:8084/jking.wang/liteapi.git', 'name', 'passward', 'cd GNSS/tapp','pyinstaller -F tapp_v5_20230725.py']
    receipt_list = ['Password', 'root@ubuntu:/home/ubuntu#', 'Proceed (y/n)?', 'Successfully uninstalled liteapi', "Username for 'http://192.168.29.134:8084'", "Password for 'http://Jking.wang@xxx.xxx.xx.134:8084'",'Successfully installed liteapi', 'root@ubuntu:/home/ubuntu/GNSS/tapp#','Building EXE from EXE-00.toc completed successfully.']
    unintstall_status = False

    for n, command in enumerate(command_list):
        if unintstall_status:
            if command == 'y':
                continue
        shell.send(command + '\n')

        # 获取输出
        while True:
            output = shell.recv(1024).decode()
            print(output)
            if receipt_list[n] in output:
                time.sleep(0.1)
                break
            if 'WARNING: Skipping liteapi as it is not installed' in output:
                unintstall_status = True
                break

    # 使用 SFTP 下载文件
    sftp = client.open_sftp()
    sftp.get(remote_filepath, local_filepath)
    sftp.close()

    # 关闭连接
    client.close()

def main():
    try:
        # 树莓派的 IP 地址、端口、用户名和密码
        ip = 'xx.xx.xx.xx'
        port = 22  # SSH 端口通常是 22
        username = 'xxxxx'
        password = 'xxxxx'
        nt = datetime.now().strftime('%Y%m%d')

        # 要下载的文件路径
        remote_filepath = '/home/ubuntu/GNSS/tapp/dist/tapp_v5_20230725'
        local_filepath = 'D:/Personal Information/02-Tool Test/TWS/05-Testapp/tapp_v5_20230725'

        # 下载文件
        ssh_command(ip, port, username, password, remote_filepath, local_filepath)
        new_name = f'tapp_v1_{nt}.ubuntuserver'
        et = time.time() + 20
        while et >= time.time():
            if os.path.exists(local_filepath):
                os.rename(local_filepath, os.path.join(os.path.dirname(local_filepath), new_name))
                print('Testapp 导出完成。')
                break
        else:
            print('Testapp 导出异常。')
    except:
        print(f'-- Error {traceback.format_exc()}')

if __name__ == '__main__':
    main()

