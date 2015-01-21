---
layout: post
title: 半天简单总结python
description: 我就是没事了写着玩儿的
category: blog
---

help(func)随便什么函数都可以查到

##数据类型
整数定义跟c语言一样,type(ver)返回变量类型

"""三引号表示注释,三引号表示格式化输入

```python
mail = """ Hi
    I am 
    Jim
"""
```

序列切片-->str[x:y],str[x,step,y]

序列都有的函数

```python
len()
+
*    str=str1*5
in   's' in str
max()
min()
cmp(tuple1,tuple2)
id(str)查看内存空间
```

内存存储的是值，不是元素，每当变量值改变的时候，内存都会变化

```python
str = "ssg"
id(str)
str = "ss"
id(str)#两次结果是不一样的
```

###元组：元组不可以单独元素变化，

创建元祖：

```python
myempty = ()
singleone = (2,)
many = (1,3,4)
```

###列表：

```python
list.append(msg)
list.remove('msg')选第一次出现的msg删除
```


###字典：

```python
key不可变，value可变
keys()返回键列表
values()返回键值列表
items()返回字典中的元组
fdict = dict(['x',1],['y',2])生成字典
dict.pop(key,val=msg)删除,不存在的时候返回msg（可选）
del(dict[key])删除
dict.clear()删除所有元素
del dict删除字典
dict.git(key,'msg')取值不存在返回msg，msg可选
dict.fromkeys(seq,val=None)以seq中的元素为键创建一个字典，键值为空
dict.has_key(key) 判断是否存在key，常用in或者not in 代替
dict.update(temp_dict)把temp中的元素添加到dict，不存在则建立，存在则覆盖
```

分支语句：if,if-else,if-elif-else

##函数

```python
def f(x,*args.**kwarg):
    print x
    if(args):
        print args
    if(kwarg):
        print kwarg
```

可以传入任意数量参数，f('x',1,2,y=9)

lambda x,y:x*y 直接返回x*y

比如阶乘 reduce (lambda x,y:x*y , range(1,100))

* 在目录下创建\_\_init\_\_.py 就可以把文件变成一个包，使用import xxx.xxx导入包内文件






##文件操作：

```python
fileptr = file(filename)
fileptr = open(filename,mode)默认模式是r.
fileptr.read()读取整个文件
fileptr.close()关闭
fileptr.write('msg')只有当关闭文件或者缓冲区的时候才会写入
```

::r+读写，w+先删除再读写，没有则创建
r+直接从指针开头写入，如果要追加就需要先read()到文件尾部然后再来write
a在文件末尾追加新内容，a+读写
b打开二进制文件

###文件方法：

```python
string = f.readline(size)size可选，小于一行
List = f.readlines(size)...
string = f.read(size)...
file.next()读取一行，指向下一行
for i in open(filename):
    print i#每次读取一行打印出来

f.write(msg)写一行
f.writelines(List)写多行
```

f.seek(偏移量,选项)

* 0：表示将文件指针指到从文件0开始到偏移量处

* 1：将指针从当前位置开始到偏移量处，

* 2：从文件末尾倒数偏移量处

* 偏移方向用正负控制

`eg`f.seek(0,0)回到文件开始

* f.flush()提交更新






##OS模块：常见函数

```python
import os
os.mkdir('/home/hj/test')
os.mkdir(path[,mode=0777])
makedirs(name,mode=511)创建多级目录
rmdir(path)
removedirs(path)删除多级目录
listdir(path)
getcwd()==>pwd
chdir(path)
walk(top,topdown=true,onerror=None)
os.isdir(name)判断是否为目录
os.path.join(path)#会把当前路进跟path连接起来
os.walk(path)返回一个元祖，有三个元素，分别为每次遍历的路径名，目录列表，文件列表
g = os.walk('.')
g.next()每次遍历一个目录下
```

于是就有了这样的办法来遍历目录打印全路径

```python
for path,d,filelist in os.walk('.'):
    for filename in filelist:
        os.path.join(path,filename)

```


##面向对象：

```python
class hj:
    first = 1
    second = 2
    name = 'd'
    __var = "私有属性"
    def __init__(self,n='dd'):
        self.name = n
        pirnt "初始化"
    def stati():
        print = "静态"
    def __se(self):
        print "私有方法"
    def f(self):
        print 'hj'
    def __str__(self):
        return "类被调用、运行的时候就自动出现"
    def __del__():
        pass
if __name__=='__main__':
    me = hj('hj')


class parent:
    def f(self):
        print "father"

class son(father):
    def func(self):
        print 'I am son'

test = son()
test.f()
test.func()
```


##正则表达式：

import re

###常用元字符： `. ^ $ * + ? {} () \ | []`	

`s = r'abx'`字符串前面加r，内部元字符就需要转义后才能匹配

re.findall(s,'avxxaagadfgdfg')返回一个列表

* \d 匹配任何十进制数字

* \D 匹配任何非数字

* \s 匹配任何空白字符

* \S 匹配任何非空白

* \w 匹配任何数字字母

* \W 匹配任何非数字字母

* {8}重复8次

###常用函数

```python
r = r'\d{3,4}-?\d{8}'
p_tel = re.compile(r)
p_tel.findall('010-12345678')效果和re.findall(r,'101-12345678')一样，但是速度更快
match()决定re是否在字符串刚开始的位置匹配
x = p_tel.match() x是一个迭代器，只判断是否有值
x.group()返回x指向的对象

search()扫描字符串，找到re匹配的位置
findall()返回所有匹配的列表
finditer()找到re匹配的所有字符串，并把他们作为一个迭代器返回
x = p_tel.finditer(msg)
x.group() 返回所有匹配
x.start() 返回第一个匹配
x.end() 返回最后一个匹配
x.span() 返回一个元组，包含(开始，结束)的位置

s.replace(str,str1)字符串替换
使用正则形式如下
rs = r'c..t'
re.sub(rs,'python', 'fsfhglskuegjceet')用rs替换后者中的位置为中间的

s.split(brk)字符串切割
使用正则形式如下
re.split(r'sfs*',str)
dir(re)查看re的内置属性和方法，任何包都可以使用

属性
S匹配任何字符，包括换行等re.findall(r,str,re.S)
M多行匹配 re.findall(r,file,re.M)
I大小写不敏感re.I
```

##调用外部程序

```python
import subprocess
subprocess.call('ls -l ', shell=True)#默认false，为true时使用shell执行命令
subprocess.call(['ls','l','.'])相同效果，推荐使用上面
dir(subprocess)

import os
os.system('ls -l')#执行正确返回0，错误返回其他数字。可以接收任何shell命令
os.listdir('.')
f = os.popen('ls')
f.read()获得内容
stdin, stdout = os.popen2('sort')#返回标准输入和输出
stdin.write('a\n')
stdin.write('c\n')
stdin.write('b\n')
stdin.close()
stdout.read()
```



##爬虫下载图片
###简单爬虫

首先查看网页代码，图片代码的特征。正则提取图片地址，开始下载

```python
#!/bin/env python

import re
import urllib#从地址获取源代码
#获取指定地址源代码
def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

#获得图片
def getImage(html):
    reg = r'src="(.*\.jpg)" width'
    imgre = re.compile(reg)
    imglist = re.findall(reg,html)
    x = 1
    for i in imglist:
        urllib.urlretrieve(i,'%s.jpg' % x)
        x = x+1

if __name__=='__main__':
    getImage(getHtml('www.baidu.com'))

```

##GUI--wxpython:

步骤：

* 导入wxpython包

* 子类化wxpython应用程序类

* 定义一个应用程序的初始化方法

* 创建一个应用程序类的实例

* 进入这个应用程序的主实践循环

* 创建应用程序对象：app = wx.app()

* 创建窗口：win = wx.Frame(None)

* 显示窗口：win.Show()

* 进入应用程序管理循环:app.MainLoop()

###一个简单的记事本，通过像素管理尺寸（特别是文本框）

```python
import wx
app = wx.App()
win = wx.Frame(None,title='hj',size = (410,335))
win.Show()#显示
loadButton = wx.Button(win,lable='load',pos = (225,5), size = (80,25))#按钮
saveButton = wx.Button(win,lable='save',pos = (315,5), size = (80,25))

filename = wx.TextCtrl(win,pos = (5,5),size = (210,25))#文本框
content = wx.TextCtrl(win, pos = (5,35), size = (390,260), style = wx.TE_MULTILINE | wx.HSCROLL)#style分别有竖着的下拉跳和横着的下拉条
app.MainLoop()
```


###记事本，用尺寸器管理大小

```python
import wx
app = wx.App()
win = wx.Frame(None,title='hj',size = (410,335))

bkg = wx.Panel(win)#尺寸管理,背景画板

loadButton = wx.Button(bkg,lable='load')#按钮
saveButton = wx.Button(bkg,lable='save')
filename = wx.TextCtrl(bkg)#文本框
content = wx.TextCtrl(bkg, style = wx.TE_MULTILINE | wx.HSCROLL)#style分别有竖着的下拉跳和横着的下拉条

#划分组建位置
hbox = wx.BoxSizer()#不加参数，默认左右管理（上面一个文本框两个按钮，上部份）
hbox.add(filename，proportion=1,flag = wx.EXPAND)#proportion表示占位置大小,1为最大空间，flag表示是否拉伸
hbox.add(loadButton, proportion=0,flag = wx.LEFT,boder = 5)#表示在左边有边界，像素5
hbox.add(saveButton, proportion=0,flag = wx.LEFT,boder = 5)

bbox = wx.BoxSizer(wx.VERTICAL)#上下划分页面管理
bbox.add(hbox,proportion = 0,flag = wx.EXPAND | wx.ALL,border=5)
bbox.add(content,proportion = 1,flag = wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT,border = 5)

bkg.SetSize(bbox)#让布局管理器生效

win.Show()#显示
app.MainLoop()
```

###按钮事件处理，事件绑定

```python
import wx
app = wx.App()
win = wx.Frame(None,title='hj',size = (410,335))

bkg = wx.Panel(win)#尺寸管理,背景画板

#定义load按钮
def openfile(evt):
    filepath = filename.GetValue()#获取输入
    fopen = open(filepath,'a+')#打开文件
    content.SetValue(fopen.read())#把文件放在content
    fopen.close()

def savefile(evt):
    filepath = filename.GetValue()
    fopen = open(filepath,'a+')
    fopen.write(content.GetValue())
    fopen.close()

loadButton = wx.Button(bkg,lable='load')#按钮
saveButton = wx.Button(bkg,lable='save')
filename = wx.TextCtrl(bkg)#文本框
content = wx.TextCtrl(bkg, style = wx.TE_MULTILINE | wx.HSCROLL)#style分别有竖着的下拉跳和横着的下拉条

loadButton.Bind(wx.EVT_BUTTON,openfile)#load键绑定了button类型的openfile事件
saveBUtton.Bind(wx.EVT_BUTTON,savefile)
#划分组建位置
hbox = wx.BoxSizer()#不加参数，默认左右管理（上面一个文本框两个按钮，上部份）
hbox.add(filename，proportion=1,flag = wx.EXPAND)#proportion表示占位置大小,1为最大空间，flag表示是否拉伸
hbox.add(loadButton, proportion=0,flag = wx.LEFT,boder = 5)#表示在左边有边界，像素5
hbox.add(saveButton, proportion=0,flag = wx.LEFT,boder = 5)

bbox = wx.BoxSizer(wx.VERTICAL)#上下划分页面管理
bbox.add(hbox,proportion = 0,flag = wx.EXPAND | wx.ALL,border=5)
bbox.add(content,proportion = 1,flag = wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT,border = 5)

bkg.SetSize(bbox)#让布局管理器生效

win.Show()#显示
app.MainLoop()
```

##多线程：

```python
import thread
import time
def go(name,n):
    for i in xrange(3)
        print name,i
        time.sleep(1)

thread.start_new_thread(go,('baby',3))
thread.start_new_thread(go,('gay', 3))
time.sleep(6)#线程工作需要时间，如果不sleep，进程就会直接瞬间结束，这个时候线程也就自动结束了，不会相互等待
```

###线程锁:

```python
import thread
import time
def go(name,n,l):
    for i in xrange(3)
        print name,i
        time.sleep(1)
    l.release()
locket = thread.allocate_lock()#申明锁对象
locket.acquire()#把锁锁上
print locket.locked()#查看状态

thread.start_new_thread(go,('baby',3),locket)

#locket.release()#解锁

while locket.locked():
    pass
```

其实个人感觉python的多线程就是一个坑，很多情况下根本达不到多线程的效果，或者是我根本就不会用。估计是后者。。。orz...

##Json格式储存文件：

Json必须是unicode类型的（utf-32,utf-16,utf-8默认）

```python
import json
d = {'n':,'tag':89,'id':('sdf',234),'pk':[12,'sfs']}#元组会自动转化成列表
with open('test.txt','w') as f:
    json.dump(d,f)#顺序储存
    json.dump(d,f,indent = 0)#每个数据存一行
    json.dump(d,f,indent = 2)#每个数据的内部数据缩进为2
```
