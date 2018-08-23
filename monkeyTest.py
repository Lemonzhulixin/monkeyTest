# -*- coding: utf-8 -*-
import shutil
from Base.BasePickle import writeInfo, writeSum, readInfo
from Base.BaseWriteReport import report
import datetime
import time
from Base.BaseFile import OperateFile
import os
from Base import AdbCommon
from Base.Config import Config
from Base import BasePhoneMsg
from Base import BaseMonitor
import threading


#PATH = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p)) #报错：name '__file__' is not defined，os.path.dirname(path) 返回文件路径
#修改为：
PATH = lambda p: os.path.abspath(os.path.join(os.path.dirname(os.path.realpath('__file__')), p)) #os.path.realpath(path)  返回path的真实路径

ba = AdbCommon.AndroidDebugBridge()
info = []

# 手机信息
def get_phone(dev):
    phone_info = BasePhoneMsg.get_phone_Kernel(dev)
    app = {}
    app["phone_name"] = phone_info[0]["phone_name"] + "_" + phone_info[0]["phone_model"] + "_" + phone_info[0]["release"]
    app["rom"] = phone_info[1]
    app["kel"] = phone_info[2]
    app["pix"] = phone_info[3]
    return app

def destroy(dev):
    shutil.rmtree((PATH("./info/")))
    OperateFile(PATH("./info/" + dev + "_cpu.pickle")).remove_file()
    OperateFile(PATH("./info/" + dev + "_men.pickle")).remove_file()
    OperateFile(PATH("./info/" + dev + "_flow.pickle")).remove_file()
    OperateFile(PATH("./info/" + dev + "_battery.pickle")).remove_file()
    OperateFile(PATH("./info/" + dev + "_fps.pickle")).remove_file()
    OperateFile(PATH("./info/info.pickle")).remove_file()
    OperateFile(PATH("./info/sumInfo.pickle")).remove_file()


def Create_pickle(dev, app, data):
    print("创建持久性文件...")
    cpu = PATH("./info/" + dev + "_cpu.pickle")
    men = PATH("./info/" + dev + "_men.pickle")
    flow = PATH("./info/" + dev + "_flow.pickle")
    battery = PATH("./info/" + dev + "_battery.pickle")
    fps = PATH("./info/" + dev + "_fps.pickle")
    time.sleep(2)
    app[dev] = {"cpu": cpu, "men": men, "flow": flow, "battery": battery, "fps": fps, "header": get_phone(dev)}
    OperateFile(cpu).mkdir_file()
    OperateFile(men).mkdir_file()
    OperateFile(flow).mkdir_file()
    OperateFile(battery).mkdir_file()
    OperateFile(fps).mkdir_file()
    OperateFile(PATH("./info/sumInfo.pickle")).mkdir_file() # 用于记录是否已经测试完毕，里面存的是一个整数
    OperateFile(PATH("./info/info.pickle")).mkdir_file() # 用于记录统计结果的信息，是[{}]的形式
    writeSum(0, data, PATH("./info/sumInfo.pickle")) # 初始化记录当前真实连接的设备数

def start(dev):
    rt = os.popen('adb devices').readlines()  # os.popen()执行系统命令并返回执行后的结果
    num = len(rt) - 2
    print(num)
    app = {}
    Create_pickle(dev, app, num)
    """os.popen("adb kill-server")
    os.popen("adb start-server")
    time.sleep(5)"""


    #手动测试部分（手动测试性能数据统计）,直接杀掉app进程即可结束测试统计（备注：操作过程中请不要杀掉app进程，否则测试终止）
    """signal = input("现在是手动测试部分，是否要开始你的测试，请输入(y or n): ")
    if signal == 'y':
        print("测试即将开始，请打开需要测试的app并准备执行您的操作....")
        time.sleep(5)
        path_log = Config.log_location + dev
        device_dir = os.path.exists(path_log)
        if device_dir:
            print("日志文件目录log已存在，继续执行测试!")
        else:
            os.mkdir(path_log)  # 按设备ID生成日志目录文件夹
        run_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

        # logcat日志
        logcat_log = path_log + "\\" + run_time + "logcat.log"
        cmd_logcat = "adb -s " + dev + " logcat > %s" % (logcat_log)
        os.popen(cmd_logcat)
        # print("logcat 命令:", cmd_logcat)

        # "导出traces文件"
        traces_log = path_log + "\\" + run_time + "traces.log"
        cmd_traces = "adb -s " + dev + " shell cat /data/anr/traces.txt > %s" % traces_log
        os.popen(cmd_traces)
        # print("traces 命令:", cmd_traces)

        time.sleep(2)
        start_time = datetime.datetime.now()
        pid = BaseMonitor.get_pid(Config.package_name, dev)
        cpu_kel = BaseMonitor.get_cpu_kel(dev)
        beforeBattery = BaseMonitor.get_battery(dev)
        print("测试前电量", beforeBattery)
        try:
            while True:
                time.sleep(1)  # 每1秒采集一次
                print("----------------数据采集-----------------")
                BaseMonitor.cpu_rate(pid, cpu_kel, dev)
                BaseMonitor.get_men(Config.package_name, dev)
                BaseMonitor.get_fps(Config.package_name, dev)
                BaseMonitor.get_flow(pid, Config.net, dev)
                BaseMonitor.get_battery(dev)
        except:
            end_time = datetime.datetime.now()
            print(str(dev) + ":测试完成!")
            afterBattery = BaseMonitor.get_battery(dev)
            writeSum(1, path=PATH("./info/sumInfo.pickle"))
            app[dev]["header"]["beforeBattery"] = beforeBattery
            app[dev]["header"]["afterBattery"] = afterBattery
            app[dev]["header"]["net"] = Config.net
            app[dev]["header"]["time"] = str((end_time - start_time).seconds) + "秒"
            writeInfo(app, PATH("./info/info.pickle"))
    if readInfo(PATH("./info/sumInfo.pickle")) <= 0:
        report(readInfo(PATH("./info/info.pickle")))
        print("Kill adb server,test finished！")
        os.popen("taskkill /f /t /im adb.exe")
        shutil.rmtree((PATH("./info/"))) # 删除持久化目录

    elif signal == 'n':
        print('用户主动放弃测试，测试结束！')
    else:
        print("测试结束，输入非法，请重新输入y or n！")"""

    #Monkey测试部分，如果是进行monkey测试，去除该部分注释（line134~line191）并注掉手动测试部分(line72~line131)；另外BaseReport.py中line85，line120~line132注释也要去除
    print("--------------开始执行Monkey----------------")
    path_log = Config.log_location + dev
    device_dir = os.path.exists(path_log)
    if device_dir:
        print("日志文件目录log已存在，继续执行测试!")
    else:
        os.mkdir(path_log)  # 按设备ID生成日志目录文件夹
    run_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    # Monkey测试结果日志:monkey_log
    adb_monkey = "shell monkey -p %s -s %s %s" % (Config.package_name, Config.monkey_seed, Config.monkey_parameters)
    monkey_log = path_log + "\\" + run_time + "monkey.log"
    cmd_monkey = "adb -s %s %s > %s" % (dev, adb_monkey, monkey_log)
    os.popen(cmd_monkey)
    print("monkey 命令:", cmd_monkey)

    # logcat日志
    logcat_log = path_log + "\\" + run_time + "logcat.log"
    cmd_logcat = "adb -s " + dev + " logcat > %s" % (logcat_log)
    os.popen(cmd_logcat)
    # print("logcat 命令:", cmd_logcat)

    # "导出traces文件"
    traces_log = path_log + "\\" + run_time + "traces.log"
    cmd_traces = "adb -s " + dev + " shell cat /data/anr/traces.txt > %s" % traces_log
    os.popen(cmd_traces)
    # print("traces 命令:", cmd_traces)
    time.sleep(2)
    start_time = datetime.datetime.now()
    pid = BaseMonitor.get_pid(Config.package_name, dev)
    cpu_kel = BaseMonitor.get_cpu_kel(dev)
    beforeBattery = BaseMonitor.get_battery(dev)
    print("测试前电量",beforeBattery)
    while True:
        try:
            with open(monkey_log,encoding='utf-8') as monkeylog:
                time.sleep(2)  # 每2秒采集一次
                print("----------------数据采集-----------------")
                BaseMonitor.cpu_rate(pid,cpu_kel, dev)
                BaseMonitor.get_men(Config.package_name, dev)
                BaseMonitor.get_fps(Config.package_name, dev)
                BaseMonitor.get_flow(pid, Config.net, dev)
                BaseMonitor.get_battery(dev)
                if monkeylog.read().count('Monkey finished') > 0:
                    end_time = datetime.datetime.now()
                    print(str(dev)+":测试完成!")
                    afterBattery = BaseMonitor.get_battery(dev)
                    writeSum(1, path=PATH("./info/sumInfo.pickle"))
                    app[dev] ["header"]["beforeBattery"] = beforeBattery
                    app[dev]["header"]["afterBattery"] = afterBattery
                    app[dev]["header"]["net"] = Config.net
                    app[dev]["header"]["monkey_log"] = monkey_log
                    app[dev]["header"]["time"] = str((end_time - start_time).seconds) + "秒"
                    writeInfo(app, PATH("./info/info.pickle"))
                    break
        except:
                end_time = datetime.datetime.now()
                print(str(dev) + ":测试完成!")
                afterBattery = BaseMonitor.get_battery(dev)
                writeSum(1, path=PATH("./info/sumInfo.pickle"))
                app[dev]["header"]["beforeBattery"] = beforeBattery
                app[dev]["header"]["afterBattery"] = afterBattery
                app[dev]["header"]["net"] = Config.net
                app[dev]["header"]["monkey_log"] = monkey_log
                app[dev]["header"]["time"] = str((end_time - start_time).seconds) + "秒"
                writeInfo(app, PATH("./info/info.pickle"))
                break
    if readInfo(PATH("./info/sumInfo.pickle")) <= 0:
        report(readInfo(PATH("./info/info.pickle")))
        print("Kill adb server,test finished！")
        os.popen("taskkill /f /t /im adb.exe")
        shutil.rmtree((PATH("./info/"))) # 删除持久化目录

#多线程启动
class MonkeyThread(threading.Thread):
    def __init__(self, dev):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.dev = dev
    def run(self):
        time.sleep(2)
        start(self.dev)

def create_threads_monkey(device_list):
    thread_instances = []
    if device_list != []:
        for id_device in device_list:
            dev = id_device
            instance = MonkeyThread(dev)
            thread_instances.append(instance)
        for instance in thread_instances:
            instance.start()

if __name__ == '__main__':
    device_dir = os.path.exists(Config.info_path)
    if device_dir:
        print("持久性目录info已存在，继续执行测试!")
    else:
        os.mkdir(Config.info_path)  # 创建持久性目录
    device_list = BaseMonitor.get_devices()
    if ba.attached_devices():
        create_threads_monkey(device_list)
    else:
        print("设备不存在")