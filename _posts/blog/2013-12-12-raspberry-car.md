---
layout: post
title: 树莓派制作wifi控制小车
description: raspberry pi火到大江南北，我也做了一个简单的小车。
category: blog
---

##树莓派小车
###材料
* [树莓派](http://trade.taobao.com/trade/detail/tradeSnap.htm?spm=a1z09.2.9.8.M4n9cw&tradeID=567688753132954)
* [SD卡](http://item.taobao.com/item.htm?id=19142619516)
* 拓展板(可选)
* [电源](http://item.taobao.com/item.htm?id=19995371946)
* [电机和电机驱动](http://item.taobao.com/item.htm?id=36909029780)
* [摄像头](http://item.taobao.com/item.htm?id=36850212461&ali_trackid=2:mm_10062864_0_0,0:1395925709_3k2_39373907&spm=a230z.1.5634029.7.0Be1hk)
* [无线网卡](http://item.taobao.com/item.htm?spm=a230r.1.14.41.LfxL1r&id=22921464431&_u=rq4fe15dd67)
* [底盘](http://item.taobao.com/item.htm?id=36903458968)


###raspberry基本系统搭建

####系统刷写
可以选择的系统非常多，有Raspbian，Archlinuxarm，Pidora等等，按需选择。

刷系统，主要是往SD卡中写入系统，Linux下可以使用dd命令，windows下可以使用Win32DiskImager。

*可以先刷写一个SD卡，然后进行常规配置和自定义配置，提取镜像，再刷人其他SD卡。*


* [官方系统下载](http://www.raspberrypi.org/downloads),[中科大加速镜像](http://mirrors.ustc.edu.cn/raspberrypi/images/)
* [Quick start guid](http://www.raspberrypi.org/quick-start-guide)
* [浙大课程： Lab1:初见树莓派(Raspberry)(windows平台)](http://mall.egoman.com.cn/index.php?option=com_content&view=article&id=99:-lab1raspberrywindows-&catid=47:shiyongfangan-&Itemid=222)
* [mac下给树莓派安装raspbian系统(DD命令)](http://zhangshenjia.com/it/raspberry_pi/mac-raspbian/)

###小车底板组装
根据实际情况或者买家提供的教程组装

###配置静态ip
无线控制希望每次登录都可以使用同一个ip，省去了查找ip的麻烦。

配置固定IP，不管是有线还是无线都配置静态ip

以Raspbian（debain系）为例：（本配置是在实验室环境下路由器提供的ip，请根据实际情况修改）

编辑 /etc/network/interfaces

```
auto lo
 
iface lo inet loopback
iface eth0 inet static
address 192.168.1.10
netmask 255.255.255.0
gateway 192.168.1.1
 
auto wlan0
iface wlan0 inet static
address 192.168.1.88
netmask 255.255.255.0
gateway 192.168.1.1
wpa-ssid 要连接的wlan ssid
wpa-passphrase wlan密码
wireless-channel 11
```

重启网络服务：

```
#root用户，或者加sudo
/etc/init.d/networking restart 
OR
service networking restart 

```

###wifi控制小车

####摄像头

* 将USB摄像头插上，查看是否找到设备，输入：

```
root@raspberrypi:/# lsusb
```

其中Logitech就是摄像头，说明找到usb设备了，然后再看看设备驱动是否正常：

```
root@raspberrypi:/# ls /dev/vid*
/dev/video0
```

看到video0说明成功。

* 安装必要的软件集：

```
sudo apt-get install subversion
sudo apt-get install libv4l-dev
sudo apt-get install libjpeg8-dev
sudo apt-get install imagemagick
```

* 下载mipg-steamer软件，编译并安装：

```
svn co https://mjpg-streamer.svn.sourceforge.net/svnroot/mjpg-streamer mjpg-streamer
cd mjpg-streamer/mjpg-streamer
make USE_LIBV4L2=true clean all
make DESTDIR=/usr install
```

注：如果这个svn的地址可能已经失效，请使用下面源

```
wget http://sourceforge.net/code-snapshots/svn/m/mj/mjpg-streamer/code/mjpg-streamer-code-182.zip
unzip mjpg-streamer-code-182.zip
cd mjpg-streamer-code-182/mjpg-streamer
```

* 创建一个文件video.sh并编辑如下代码

```
#!/bin/sh

STREAMER=mjpg_streamer
DEVICE=/dev/video0
RESOLUTION=320x240
FRAMERATE=25
HTTP_PORT=8001

PLUGINPATH=/usr/lib

$STREAMER -i "$PLUGINPATH/input_uvc.so -n -d $DEVICE -r $RESOLUTION -f $FRAMERATE -y YUYV" -o        "$PLUGINPATH/output_http.so -n -p $HTTP_PORT " &

```

* 执行代码

```
sudo chmod 777 video.sh 
sudo ./video.sh
```

* 在pc上建立一个html文件，如下编辑

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
        <title>RPi</title>
        <style type="text/css">
                button {
                        margin: 5px 5px 5px 5px;
                        width: 50px;
                        height: 50px;
                        font-size: 24pt;
                        font-weight: bold;
                        color: black;
                }
        </style>
</head>
<body>
        <div id="content" align="center">
                <img width="500" height="400" src="http://"你的raspberry pi ip地址”:8001/?action=stream"><br/>
                <div id="up"></div>
                <div id="middle"></div>
                <div id="down"></div>
        </div>
</body>

```

在pc上运行上面index.html”文件看到视频了，就说明摄像头工作正常了，到此摄像头的工作就结束了

效果图

![ ](/images/raspberry-car/video.png)

* 在执行的过程中，如果显示摄像头关闭不成功，则要杀死进程

```
kill $(pgrep video.sh)
```

####控制代码

小车的控制可以用任何raspberry上能运行的语言编写，这里为方便，直接使用python

```python
#!/usr/bin/env python
#wheel.py
import RPi.GPIO as GPIO
class wheel:
    pins = {'left1':[13,15],'left2':[16,18],'right1':[19,21],'right2':[22,24]}
	
    def __init__(self,name):
		self.name = name
		self.pin = wheel.pins[self.name]
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.pin[0],GPIO.OUT)
		GPIO.setup(self.pin[1],GPIO.OUT)
		self.stop()

    def forward(self):
		GPIO.output(self.pin[0],GPIO.HIGH)
		GPIO.output(self.pin[1],GPIO.LOW)
		
    def back(self):
		GPIO.output(self.pin[0],GPIO.LOW)
		GPIO.output(self.pin[1],GPIO.HIGH)
		
    def stop(self):
		GPIO.output(self.pin[0],GPIO.LOW)
		GPIO.output(self.pin[1],GPIO.LOW)
    
    def __del__(self):
        pass
        #GPIO.cleanup()
```

```python
#!/usr/bin/env python
#car.py
from wheel import *
import RPi.GPIO as GPIO
class car:
    wheels=[wheel('left1'),wheel('left2'),wheel('right1'),wheel('right2')]

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
    
    def forward(self):
        for wheel in car.wheels:
            wheel.forward()

    def back(self):
        for wheel in car.wheels:
            wheel.back()

    def left(self):
        car.wheels[2].forward()
        car.wheels[3].forward()
        car.wheels[0].back()
        car.wheels[1].back()

    def right(self):
        car.wheels[0].forward()
        car.wheels[1].forward()
        car.wheels[2].back()
        car.wheels[3].back()

    def stop(self):
        for wheel in car.wheels:
            wheel.stop()

```

```python
#!/usr/bin/env python
#action.py

from car import *
import clean


def action(com):

    #when control the car
    if com=="forward":
        a = car()
        a.forward()
    elif com=="back":
        a = car()
        a.back()
    elif com=="left":
        a = car()
        a.left()
    elif com=="right":
        a = car()
        a.right()
    elif com=="stop":
        a = car()
        a.stop()
    #clean all
    elif com=="clean":
        clean.clean()
```

```python
#!/usr/bin/env python
#server.py

from actions import *
from socket import *
import sys
import time
import RPi.GPIO as GPIO

host = "192.168.1.10"
port = 8888
s = socket()

s.bind((host,port))
s.listen(5)
print "listen on port 8888"

while 1:
    conn, addr = s.accept()
    print "connected by:",addr

    while 1:
    #if 1:
        command = conn.recv(1024).replace('\n','')
        #print command
        if not command: break
        #this command to test the distance 
        elif command=="distance":
            dis=action(command)
            conn.send(dis)
        else:
            action(command)
    conn.close()
    #action("clean")
    #GPIO.cleanup()
    #conn.close()
```



  * [raspberry GPIO编程指导](http://dreamcolor.net/archives/rpio-document-pwm-py.html)

PC客户端代码：

注意：请先安装wxpython

```python
#!/usr/bin/env python
#coding:utf-8
import time
import wx
import socket
#import sys
import threading
import struct

#Receive message
class Receiver(threading.Thread):
    def __init__(self,threadName,window):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        #连接服务器
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            self.sock.connect((self.window.host, self.window.port))
            self.window.LogMessage("连接服务器成功...\n")
            self.runT = True
        except Exception:
            self.window.LogMessage("连接服务器失败...\n")
            self.sock.close()

    def stop(self):
        self.window.LogMessage("关闭Socket连接...\n")
        self.sock.close()
        self.runT = False
        self.timeToQuit.set()

    def sendMsg(self,msg):
        logMsg = (u"发送：%s\n" % (msg))
        self.window.LogMessage(logMsg)
        self.sock.sendall(msg)

    def run(self):
        try:
            while self.runT:
                data = self.sock.recv(4)
                if data:
                    dataLen, = struct.unpack_from("i",data)
                    wx.CallAfter(self.window.LogMessage,(u"返回数据长度:%s\n" % (dataLen)))
                    wx.CallAfter(self.window.LogMessage,(u"返回数据:%s\n" % (self.sock.recv(dataLen))))
        except Exception:
            pass
class InsertFrame(wx.Frame):

    def __init__(self, parent, id):

        #创建父框
        wx.Frame.__init__(self, parent, id, 'Socket Client', size=(1140, 450))
        #创建画板
        self.panel = wx.Panel(self,-1)
        self.panel.SetBackgroundColour("White")
        #创建按钮
        self.createButtonBar(self.panel)
        #创建静态文本
        self.createTextFields(self.panel)
        #创建文本框
        self.creatTextInput(self.panel)

        #Socket 地址
        self.host, self.port = "localhost", 12340
        self.runT = True
###############################
    #创建文本
    def createTextFields(self, panel):
        for eachLabel, eachPos in self.textFieldData():
            self.createCaptionedText(panel, eachLabel, eachPos)

    def createCaptionedText(self, panel, label, pos):
        static = wx.StaticText(panel, wx.NewId(), label, pos)
        static.SetBackgroundColour("White")
#########################
    #创建按钮
    def createButtonBar(self, panel):
        for eachLabel,eachSize,eachPos, eachHandler in self.buttonData():
            self.buildOneButton(panel, eachLabel,eachSize,eachHandler,eachPos)
    def buildOneButton(self, parent, label,buttonsize,handler, pos=(0,0)):
        button = wx.Button(parent, -1, label, pos,buttonsize)
        #绑定按钮的单击事件
        self.Bind(wx.EVT_BUTTON, handler, button)
#########################
    #按钮栏数据
    def buttonData(self):#(按钮名称，按钮大小，按钮坐标，按钮事件）
        return (("forward",(60,60 ),(875, 100),self.forward),
                ("back",(60, 60),(875, 300),self.back),
                ("left",(60, 60),(750, 200),self.left),
                ("right",(60, 60),(975, 200),self.right),
                ("stop",(60, 60),(875, 200),self.stop),
                ("连 接",(50, 25),(310, 30),self.OnConnection),
                ("断 开", (50, 25),(370, 30),self.OnCloseSocket),
                ("清 空", (50, 25),(430, 30),self.OnClearLog),
                ("发 送", (50, 25),(540, 400),self.OnSend))
    #文本内容
    def textFieldData(self):
        return (("Please Input socket address AND port：", (10, 10)),
                ("输入消息：", (10, 380)))
########################
    #创建文本框
    def creatTextInput(self,panel):
        #服务器地址输入框
        self.socketHostText = wx.TextCtrl(self.panel, wx.NewId(), "", size=(230, 25),pos=(10, 30))
        #服务器端口输入框
        self.socketPortText = wx.TextCtrl(self.panel, wx.NewId(), "", size=(50, 25),pos=(250, 30))
        #信息显示
        self.log = wx.TextCtrl(self.panel, -1, "",size=(620, 310),pos=(10, 60),style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY)
        #信息输入
        self.inputMessage = wx.TextCtrl(self.panel, wx.NewId(), size=(520, 25),style=wx.TE_PROCESS_ENTER,pos=(10, 400))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSend, self.inputMessage)
########################

    #事件处理器(关闭窗口）
    def OnCloseWindow(self, event):
        self.thread.stop()
        self.Destroy()

    #事件处理器(关闭Socket）
    def OnCloseSocket(self, event):
        self.thread.stop()

    #事件处理器(连接到SOCKET）
    def OnConnection(self,event):
        if self.socketHostText.GetValue()!='' and self.socketPortText.GetValue()!='':
            self.host, self.port = str(self.socketHostText.GetValue()),int(self.socketPortText.GetValue())
        threadName = "socketclient"
        self.thread = Receiver(threadName, self)#创建一个线程
        self.thread.setDaemon(True)
        self.thread.start()#启动线程

    #事件处理器(显示LOG）
    def LogMessage(self, msg):#注册一个消息
        self.log.AppendText(msg)

    #事件处理器(清空LOG）
    def OnClearLog(self,event):#注册一个消息
        self.log.Clear()

    #事件处理器(给SOCKET发送消息,并清空输入框）
    def OnSend(self, event):
        self.thread.sendMsg(self.inputMessage.GetValue())
        self.inputMessage.Clear()

    ##############################################
    ##movement button##

    def forward(self,event):
        self.thread.sendMsg("forward")

    def back(self,event):
        self.thread.sendMsg("back")

    def left(self,event):
        self.thread.sendMsg("left")

    def right(self,event):
        self.thread.sendMsg("right")

    def stop(self,event):
        self.thread.sendMsg("stop")


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = InsertFrame(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
```

效果图

![ ](/images/raspberry-car/pc_client.png)

为方便，可以直接使用git下载

```
git clone https://github.com/dantangfan/tank.git tank
git clone https://github.com/dantangfan/clientTank clientTank
```

###管理和应用
* [berryio](https://github.com/NeonHorizon/berryio),[项目介绍](http://www.geekfan.net/3251/）

* [webiopi](https://code.google.com/p/webiopi/),[项目介绍](http://www.2fz1.com/?tag=webiopi）
####相关文档

* [GY-26电子指南针资料（串口+IIC+温度）](http://ishare.iask.sina.com.cn/f/61335036.html)
* [黑白 红外壁障模块 资料](http://share.eepw.com.cn/share/download/id/165040)
* [DHT22_温湿度传感器](http://wenku.baidu.com/view/8f46c2d1b9f3f90f76c61b4f.html)
* [GY-26电子指南针使用手册](http://wenku.baidu.com/view/272b0c69a98271fe910ef926.html)
* [HC-SR04超声波测距模块说明书](http://wenku.baidu.com/view/ce9e5e48767f5acfa1c7cd8a.html)
* [人体红外感应器](http://forum.stmlabs.com/showthread.php?tid=5549)

###其他

* [raspberrytank](http://raspberrytank.ianrenton.com/)
* [传感器的简单应用](http://www.apinglai.com/category/arm/)

####联系人

* 联系：dantangfan@gmail.com，316977394@qq.com
