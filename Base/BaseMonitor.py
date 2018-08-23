import subprocess
import os
import re
from wsgiref.validate import validator
import time
from Base.BasePickle import *
from Base.Config import Config

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

dev_model_list =[]
dev_list =[]
device_dict = {}

def get_devices():
    #返回 device model 和 device id
    rt = os.popen('adb devices').readlines()  # os.popen()执行系统命令并返回执行后的结果
    n = len(rt) - 2
    print("当前已连接待测手机数为：" + str(n))
    for i in range(n):
        nPos = rt[i + 1].index("\t")
        dev = rt[i + 1][:nPos]
        #phone_model = os.popen("adb -s " + dev + ' shell cat /system/build.prop | find "ro.product.model="').readlines()  # 获取手机型号
        #dev_model = phone_model[0][17:].strip('\r\n')
        #dev_model_list.append(dev_model)
        dev_list.append(dev)
        #device_dict.update({dev:dev_model})
    return dev_list

"""def get_men(pkg_name, devices):
    try:
        cmd = "adb -s " + devices + " shell dumpsys meminfo %s" % (pkg_name)
        print(cmd)
        output = subprocess.check_output(cmd).split()
        # print(output)
        s_men = ".".join([x.decode() for x in output])  # 转换为string
        men2 = int(re.findall("TOTAL.(\d+)*", s_men, re.S)[0])
    except:
        men2 = 0
    print("-----------memory1------------")
    print(men2)
    #writeInfo(men2, PATH("../info/" + devices + "_men.pickle"))
    return men2"""
def get_men(pkg_name,dev):
    men_list =[]
    cmd = "adb -s " + dev + " shell dumpsys meminfo " + pkg_name
    print(cmd)
    men_s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
    for info in men_s:
        if len(info.split()) and info.split()[0].decode() == "TOTAL":
            men_list.append(int(info.split()[1].decode()))
    men = men_list[0]
    print("----men----")
    print(men)
    writeInfo(men, PATH("../info/" + dev+ "_men.pickle"))
    return men

# 得到fps
def get_fps(pkg_name, dev):
    _adb = "adb -s " + dev + " shell dumpsys gfxinfo %s" % pkg_name
    print(_adb)
    results = os.popen(_adb).read().strip()
    frames = [x for x in results.split('\n') if validator(x)]
    frame_count = len(frames)
    jank_count = 0
    vsync_overtime = 0
    render_time = 0
    for frame in frames:
        time_block = re.split(r'\s+', frame.strip())
        if len(time_block) == 3:
            try:
                render_time = float(time_block[0]) + float(time_block[1]) + float(time_block[2])
            except Exception as e:
                render_time = 0

        '''
        当 大于16.67，按照垂直同步机制，该帧就已经渲染超时
        那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
        如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整

        最后的计算方法思路：
        执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
        需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）

        所以FPS的算法可以变为：
        m / （m + 额外的垂直同步脉冲） * 60
        '''
        if render_time > 16.67:
            jank_count += 1
            if render_time % 16.67 == 0:
                vsync_overtime += int(render_time / 16.67) - 1
            else:
                vsync_overtime += int(render_time / 16.67)

    _fps = int(frame_count * 60 / (frame_count + vsync_overtime))
    print("-----fps------")
    print(_fps)
    writeInfo(_fps, PATH("../info/" + dev + "_fps.pickle"))
    return _fps



"""def get_battery(devices):
    try:
        cmd = "adb -s " + devices + " shell dumpsys battery"
        print(cmd)
        output = subprocess.check_output(cmd).split()
        # _batter = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
        #                            stderr=subprocess.PIPE).stdout.readlines()
        st = ".".join([x.decode() for x in output])  # 转换为string
        # print(st)
        battery2 = int(re.findall("level:.(\d+)*", st, re.S)[0])
    except:
        battery2 = 0
    print("-----battery------")
    print(battery2)
    #writeInfo(battery2, PATH("../info/" + devices + "_battery.pickle"))
    return battery2"""

def get_battery(dev):
    battery = []
    adb_battery = "adb -s " + dev + " shell dumpsys battery"
    print(adb_battery)
    _battery = subprocess.Popen(adb_battery, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.readlines()
    for info in _battery:
        if info.split()[0].decode() == "level:":
            battery.append(int(info.split()[1].decode()))
    battery2 = battery[0]
    print("-----battery------")
    print(battery2)
    writeInfo(battery2, PATH("../info/" + dev + "_battery.pickle"))
    return battery2


def get_pid(pkg_name,dev):
    #print("----get_pid-------")
    pid = subprocess.Popen("adb -s " + dev + " shell ps | findstr " + pkg_name, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).stdout.readlines()
    for item in pid:
        if item.split()[8].decode() == pkg_name:
            return item.split()[1].decode()

def get_flow(pid, type, dev):
    # pid = get_pid(pkg_name)
    upflow = downflow = 0
    if pid is not None:
        cmd = "adb -s " + dev + " shell cat /proc/" + pid + "/net/dev"
        print(cmd)
        _flow = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).stdout.readlines()
        for item in _flow:
            if type == "wifi" and item.split()[0].decode() == "wlan0:":  # wifi
                # 0 上传流量，1 下载流量
                upflow = int(item.split()[9].decode())
                downflow = int(item.split()[1].decode())
            if type == "gprs" and item.split()[0].decode() == "rmnet0:":  # gprs
                upflow = int(item.split()[9].decode())
                downflow = int(item.split()[1].decode())
    print("------flow---------")
    print(upflow, downflow)
    writeFlowInfo(upflow, downflow, PATH("../info/" + dev + "_flow.pickle"))


def totalCpuTime(dev):
    user = nice = system = idle = iowait = irq = softirq = 0
    '''
    user:从系统启动开始累计到当前时刻，处于用户态的运行时间，不包含 nice值为负进程。
    nice:从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间
    system 从系统启动开始累计到当前时刻，处于核心态的运行时间
    idle 从系统启动开始累计到当前时刻，除IO等待时间以外的其它等待时间
    iowait 从系统启动开始累计到当前时刻，IO等待时间(since 2.5.41)
    irq 从系统启动开始累计到当前时刻，硬中断时间(since 2.6.0-test4)
    softirq 从系统启动开始累计到当前时刻，软中断时间(since 2.6.0-test4)
    stealstolen  这是时间花在其他的操作系统在虚拟环境中运行时（since 2.6.11）
    guest 这是运行时间guest 用户Linux内核的操作系统的控制下的一个虚拟CPU（since 2.6.24）
    '''

    cmd = "adb -s " + dev + " shell cat /proc/stat"
    #print(cmd)
    """p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()"""
    process = (os.popen(cmd))
    output = process.read()
    #print(output)
    res = output.split()
    #print(res)
    for info in res:
        if info == "cpu":
            user = res[1]
            nice = res[2]
            system = res[3]
            idle = res[4]
            iowait = res[5]
            irq = res[6]
            softirq = res[7]
            """print("user = %s"% user)
            print("nice = %s" % nice)
            print("system = %s" % system)
            print("idle = %s" % idle)
            print("iowait =%s" % iowait)
            print("irq = %s" % irq)
            print("softirq = %s" % softirq)"""
            result = int(user) + int(nice) + int(system) + int(idle) + int(iowait) + int(irq) + int(softirq)
            #print("totalCpuTime=" + str(result))
            return result


'''
每一个进程快照
'''


def processCpuTime(pid, dev):
    '''

    pid     进程号
    utime   该任务在用户态运行的时间，单位为jiffies
    stime   该任务在核心态运行的时间，单位为jiffies
    cutime  所有已死线程在用户态运行的时间，单位为jiffies
    cstime  所有已死在核心态运行的时间，单位为jiffies
    '''
    utime = stime = cutime = cstime = 0
    try:
        cmd = "adb -s " + dev + " shell cat /proc/" + pid + "/stat"
        #print(cmd)
        """p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()"""
        process = (os.popen(cmd))
        output = process.read()
        #print(output)
        #process.close()
        res = output.split()
        #print(res)
        utime = res[13]
        stime = res[14]
        cutime = res[15]
        cstime = res[16]
        """print("utime = %s" % utime)
        print("stime = %s" % stime)
        print("cutime = %s" % cutime)
        print("cstime = %s" % cstime)"""
        result = int(utime) + int(stime) + int(cutime) + int(cstime)
        #print("processCpuTime=" + str(result))
    except:
        result = 0
    return result


# 得到几核cpu
def get_cpu_kel(dev):
    cmd = "adb -s " + dev + " shell cat /proc/cpuinfo"
    #print("----cpu_kel-------")
    #print(cmd)
    process = (os.popen(cmd))
    output = process.read()
    res = output.split()
    num = re.findall("processor",str(res))
    #print(num)
    return len(num)

'''
计算某进程的cpu使用率
100*( processCpuTime2 – processCpuTime1) / (totalCpuTime2 – totalCpuTime1) (按100%计算，如果是多核情况下还需乘以cpu的个数);
cpukel cpu几核
pid 进程id
'''

def cpu_rate(pid, cpukel, dev):
    # pid = get_pid(pkg_name)
    processCpuTime1 = processCpuTime(pid, dev)
    time.sleep(1)
    processCpuTime2 = processCpuTime(pid, dev)
    processCpuTime3 = processCpuTime2 - processCpuTime1

    totalCpuTime1 = totalCpuTime(dev)
    time.sleep(1)
    totalCpuTime2 = totalCpuTime(dev)
    totalCpuTime3 = (totalCpuTime2 - totalCpuTime1) * cpukel
    #print("totalCpuTime3=" + str(totalCpuTime3))
    #print("processCpuTime3=" + str(processCpuTime3))

    cpu = 100 * (processCpuTime3) / (totalCpuTime3)
    print("--------cpu--------")
    print(cpu)
    writeInfo(cpu, PATH("../info/" + dev + "_cpu.pickle"))
    return cpu

if __name__ == '__main__':
    device_list = get_devices()
    print(device_list)

    """os.popen("adb kill-server adb")
    os.popen("adb start-server")
    time.sleep(2)
    dev = "7N2SSE158U004185"
    package_name = "com.quvideo.slideplus"
    pid = get_pid(package_name,dev)
    print(pid)
    cpu_kel = get_cpu_kel(dev)
    print(cpu_kel)
    get_battery(devices)
    get_men(package_name, devices)
    get_fps(package_name, devices)
    get_flow(pid, "wifi", devices)
    cpu_rate(pid,cpu_kel, devices)"""

