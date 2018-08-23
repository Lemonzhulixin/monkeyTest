# -*- coding: GB2312 -*-
import os
import os.path
import time
import glob

# 删除已有测试cmd脚本
path = "D:\\PyCharm\\Monkey_performance\\"
for file in glob.glob(os.path.join(path, '*.cmd')):
    os.remove(file)

os.system("cls")  # os.system("cls")具有清屏功能
rt = os.popen('adb devices').readlines()  # os.popen()执行系统命令并返回执行后的结果
#print(rt)
n = len(rt) - 2
print("当前已连接待测手机数为：" + str(n))
aw = input("是否要开始你的monkey测试，请输入(y or n): ")
run_time =time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

if aw == 'y':
    print("monkey测试即将开始....")
    for i in range(n):
        nPos = rt[i + 1].index("\t")
        #print(nPos)
        dev = rt[i + 1][:nPos]
        print(dev)
        phone_model = os.popen("adb -s " + dev + ' shell cat /system/build.prop | find "ro.product.model="').readlines()  # 获取手机型号
        model = phone_model[0][17:].strip('\r\n')
        #print(model)
        phone_name = os.popen("adb -s " + dev + ' shell cat /system/build.prop | find "ro.product.brand="').readlines()  # 获取手机名称
        #roname = phone_name[0]
        name = phone_name[0][17:].strip('\r\n')
        package_name = os.popen("adb -s " + dev + ' shell pm list packages | find "com.quvideo.slideplus"').readlines() #获取package包名
        #package = package_name[0]
        app_name = package_name[0][8:].strip('\r\n')
        path_log = "D:\\PyCharm\\Monkey_performance\\" + name + '-' + model
        if app_name == 'com.quvideo.slideplus':
            device_dir = os.path.exists(path_log)
            if device_dir:
                print("File Exist, go on testing!")
            else:
                os.mkdir(path_log)  # 按设备ID生成日志目录文件夹
            """w_log = open(path_log + '-logcat' + '.cmd', 'w')
            w_log.write('adb -s ' + dev + ' logcat -v time > ' + '"' + path_log + '"' + '\\'+ run_time + '_logcat.txt\n' )
            w_log.close()"""

            w_adb = open(path_log + '-device' + '.cmd', 'w')
            w_adb.write(
                'adb -s ' + dev + ' shell monkey -p ' + app_name + ' -s 200 --throttle 500 --ignore-crashes --ignore-timeouts --pct-touch 45 --pct-trackball 15 --pct-appswitch 10 --pct-syskeys 10 --pct-motion 20 -v -v 1000 > ')  # 选择设备执行monkey
            w_adb.write('"' + path_log + '"' + '\\' + run_time + '_monkey.txt\n')
            #wd.write('测试完成，请查看日志文件!')
            w_adb.close()

        else:
            print("待测手机" + name + '-' + model + "未安装小影记")

    # 执行上述生成的cmd脚本'

    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) == True:
            if file.find('.cmd') > 0:
                os.system('start ' + os.path.join(path, '"' + file + '"'))  # dos命令中文件名如果有空格，需加上双引号
                time.sleep(1)
elif aw == 'n':
    print('用户主动放弃测试，测试结束！')
else:
    print("测试结束，输入非法，请重新输入y or n！")