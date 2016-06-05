---
layout: post
title: ubuntu更新死掉了
description: ubuntu号称最好用的桌面系统，然而还是不怎么好用啊
category: opinion
---
离开了翔厂，告别了 Mac ，新公司配的开发机是双显示器的华硕台式机，系统自选，于是选择了 ubuntu，运维拿过来装好之后，发现是14.04的，并不是最新版本，本着与时俱进的思想，我决定把它升级到16.xx（然而，这是一个错误的决定）

简单的直接执行

```
sudo apt-get update
sudo apt-get dist-upgrade
```

刚开始没什么问题，一直好好的，我也一直刷网页，结果中途突然崩了！重启也进不了系统了！在网上找到了解决方案，能够进入系统

	GRUB界面 按 e 编辑启动项 在 linux ... kernel /vmlinuz…… 一段末尾加入 init=/bin/bash，类似这样：...... ro quiet splash init=/bin/bash
	按 Ctrl + x 启动
	进入 root shell 后，输入：

		mount -o remount,rw /
		ln -fs /proc/self/mounts /etc/mtab

	然后按 Ctrl + Alt + Delete 重启

于是可以进入命令行了，只要能进系统就有办法解决问题。

`wget baidu.com` 发现并不能联网，于是手动配置好 `/etc/network/interface` (还有可能要配 DNS )之后，测试通过了。
于是执行 `sudo apt-get dist-upgrade` 继续更新，重启后系统恢复正常(虽然我感觉依然不太正常，但是已经能用了).

ubuntu 发热严重，一般是双显卡的问题
直接在rc.local中加入

```
echo IGD > /sys/kernel/debug/vgaswitcheroo/switch
echo OFF > /sys/kernel/debug/vgaswitcheroo/switch 
```

然后 `cat /sys/kernel/debug/vgaswitcheroo/switch `

看到 DIS 行有 off 字样，表示独显已经关了，只使用了集显。当然，这样就不方便打游戏了.
