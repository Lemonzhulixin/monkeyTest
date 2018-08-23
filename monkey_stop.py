#! /usr/bin/python
# coding: utf-8
import subprocess
from Base import BaseMonitor
import time
import os

def stop_monkey(dev):
    monkey_name = "com.android.commands.monkey"
    pid = subprocess.Popen("adb -s " + dev + " shell ps | findstr " + monkey_name, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.readlines()
    if pid =="":
        print("No monkey running in %s" % dev)
    else:
        for item in pid:
            if item.split()[8].decode() == monkey_name:
                monkey_pid = item.split()[1].decode()
                cmd_monkey = "adb -s " + dev + " shell kill %s" % (monkey_pid)
                os.popen(cmd_monkey)
                print("Monkey in %s was killed" % dev)
                time.sleep(2)

def reboot(dev):
    cmd_reboot = "adb -s " + dev + " reboot"
    os.popen(cmd_reboot)

if __name__ == '__main__':
    device_list = BaseMonitor.get_devices()
    for dev in device_list:
        stop_monkey(dev)
        #reboot(dev,dev_model) #如需要重启设备，删除注释即可