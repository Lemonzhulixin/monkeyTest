## V2.2 2017/0824

* 新增测试因其他原因中断后，仍统计中断之前的所有测试数据

## V2.1 2017/08/08

* 新增手动测试过程中性能数据统计
* monkeyTest.py：line72~line131 为手动测试部分
* monkeyTest.py：line134~line191为Monkey测试部分
* 注意两种测试开始部分注释，按照注释内容进行相关代码操作

## V2.0  2017/08/07

* 优化了统计性能数据的代码,主要是cpu rate的计算方式
* 解决多设备数据统计错误问题，使用持久化记录数据信息
* 最终报告格式修改

## V1.5
* 增加Config配置文件
* 增加设备实时监控，支持随时断开设备、插入新设备，每10s检查一次设备并自动运行
* 增加monkey_stop.py，支持随时停止monkey运行并重启（重启操作可根据需要选择是否执行）
* 设置性能数据统计间隔2s（可自定义）
* 优化并删除部分无用文件及代码

## monkey 配置文件Config.py
```
class Config:
    # apk包名
    package_name = "com.quvideo.slideplus"
    # 默认设备列表
    device_dict = {}
    # 网络
    net = "wifi"
    # monkey seed值，随机产生
    monkey_seed = str(random.randrange(1, 1000))
    # monkey 参数
    monkey_parameters = "--throttle 200 --ignore-crashes --ignore-timeouts --pct-touch 80 --pct-trackball 5 --pct-appswitch 5 --pct-syskeys 5 --pct-motion 5 -v -v 5000"
    # log保存地址
    log_location = "D:\\PyCharm\\Monkey_performance\\log\\"
    #性能数据存储目录
    info_path = "D:\\PyCharm\\Monkey_performance\\info\\"
    

启动monkey测试：执行monkeyTest.py
停止运行monkey：执行monkey_stop.py
如果需要重启设备：在执行monkey_stop.py前，删除#reboot(dev,dev_model)前的注释即可
```


## monkey 压力测试及性能统计
* python3 
* 统计性能信息cpu,men,fps,battery,flow
* 支持wifi,gprs统计
* 统计crash信息
 
fps统计：
需要打开开发者里面的GPU呈现模式分析-在adb shell dumpsys gfxinfo中
