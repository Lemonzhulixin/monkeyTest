import re
import subprocess
import os
import time



def getModel(dev):
    result = {}
    cmd = "adb -s " + dev + " shell cat /system/build.prop"
    output = subprocess.check_output(cmd).decode()
    result["release"] = re.findall("version.release=(\d\.\d)*", output, re.S)[0] #  Android 系统，如anroid 4.0
    result["phone_name"] = re.findall("ro.product.model=(\S+)*", output, re.S)[0] # 手机名
    result["phone_model"] = re.findall("ro.product.brand=(\S+)*", output, re.S)[0] # 手机品牌
    return result


def get_men_total(dev):
    cmd = "adb -s " + dev + " shell cat /proc/meminfo"
    output = subprocess.check_output(cmd).split()
    items = [x.decode() for x in output]
    for k,v in enumerate(items):
        if str(v) == 'MemTotal:':
            return int(items[k+1])
    # return  int(output[1].decode())

# # 得到几核cpu
def get_cpu_kel(dev):
    cmd = "adb -s " + dev +" shell cat /proc/cpuinfo"
    output = subprocess.check_output(cmd).split()
    sitem = ".".join([x.decode() for x in output]) # 转换为string
    return str(len(re.findall("processor", sitem))) + "核"



# 得到手机分辨率
def get_app_pix(dev):
    time.sleep(2)
    cmd = "adb -s " + dev + " shell wm size"
    #print(cmd)
    #return  subprocess.check_output(cmd).split()[2].decode()
    result = os.popen(cmd, "r")
    line = result.readline()
    while line:
        if str(line).find('Physical size') != -1:
            line = str(line).strip('\n')
            return str(line.split("Physical size:")[1])
        line = result.readline()

#
def get_phone_Kernel(dev):
    pix = get_app_pix(dev)
    men_total = get_men_total(dev)
    phone_msg = getModel(dev)
    cpu_sum = get_cpu_kel(dev)
    #print(dev + ":"+ pix,men_total,phone_msg,cpu_sum)
    return phone_msg, men_total, cpu_sum, pix


if __name__ == '__main__':
    dev = "c0d2dc31"
    m = getModel(dev)
    print(m)
