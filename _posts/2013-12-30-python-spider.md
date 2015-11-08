---
layout: post
title: 简单爬虫
description: 说一千道一万，还是不如直接用框架来的快，不过对理解过程还是有点帮助
category: blog
---

###基础知识要求：uri，url，html，http，正则表达式

###1.获取网页源代码：

```python
import urllib# import urllib2
response = urllib.urlopen('www.baidu.com')#获取网页
html = response.read()#获取网页内容
```

在urllib2里面有Request对象来映射你提供的http请求，制造一个请求，而不是直接连接网页

```python
import urllib2
request = urllib2.Request('www.baidu.com')
response = urllib2.urlopen(request)
html = response.read()
效果跟上面是一样的
```

###2.一些网站不愿意被非自动化程序访问（非浏览器），那么我们就需要在获取网页的时候添加一点header内容，把自己伪装成浏览器

```python
import urllib
import urllib2
url = 'www.baidu.com'
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'    
values = {'name' : 'WHY',    
          'location' : 'SDU',    
          'language' : 'Python' }    
  
headers = { 'User-Agent' : user_agent }    
data = urllib.urlencode(values)#需要对头进行编码
req = urllib2.Request(url, data, headers)    
response = urllib2.urlopen(req)    
the_page = response.read() 
```

###3.简单的异常处理

当由于各种原因连接不成功的时候，会发生异常。我们可以简单的处理这个异常

```python
import urllib2

req = urllib2.Request('http://www.baidu.com')
try:
    http = urllib2.urlopen(req)
except urllib2.URLError, e:
    print e.reason#它会返回出错的原因
```

*知识：http状态码

urllib2中还有很多错误反馈信息，可以参见urllib2的教程或者文档。对于常规情况来说，我们只要知道不能联通就够了。

```python
from urllib2 import Request, urlopen, URLError, HTTPError

req = Request('http://www.baidu.com')
try:
    http = urlopen(req)
except URLError, e:
    if hasattr(e,'reason'):
        print e.reason
    elif hasattr(e,'code'):
        print e.code
    else:
        print 'unknow error'
else:
    print 'successful'
```

###4.Openers和Handles:
`Openers:`当我们打开一个url的时候我们使用默认的的opener是urlopen（他是urllib2.OpenerDirector的实例），除此之外，我们可以自己构造opener

`Handers:`Openers使用handlers处理各种事物，每个handler知道如何通过特殊的协议打开特定的url，或者处理特定url打开时的各个方面，例如http重定向。因此，我们就需要自己创建handers来处理我们的需要，比如创建能处理cookie的handler

下面转自http://blog.csdn.net/pleasecallmewhy/article/details/8924889
**********************
要创建一个 opener，可以实例化一个OpenerDirector，然后调用.add_handler(some_handler_instance)。

同样，可以使用build_opener，这是一个更加方便的函数，用来创建opener对象，他只需要一次函数调用。

build_opener默认添加几个处理器，但提供快捷的方法来添加或更新默认处理器。

其他的处理器handlers你或许会希望处理代理，验证，和其他常用但有点特殊的情况。

install_opener 用来创建（全局）默认opener。这个表示调用urlopen将使用你安装的opener。

Opener对象有一个open方法。

该方法可以像urlopen函数那样直接用来获取urls：通常不必调用install_opener，除了为了方便。

说完了上面两个内容，下面我们来看一下基本认证的内容，这里会用到上面提及的Opener和Handler。

Basic Authentication 基本验证

为了展示创建和安装一个handler，我们将使用HTTPBasicAuthHandler。

当需要基础验证时，服务器发送一个header(401错误码) 请求验证。这个指定了scheme 和一个‘realm’，看起来像这样：Www-authenticate: SCHEME realm="REALM".

例如:Www-authenticate: Basic realm="cPanel Users"

客户端必须使用新的请求，并在请求头里包含正确的姓名和密码。

这是“基础验证”，为了简化这个过程，我们可以创建一个HTTPBasicAuthHandler的实例，并让opener使用这个handler就可以啦。

HTTPBasicAuthHandler使用一个密码管理的对象来处理URLs和realms来映射用户名和密码。

如果你知道realm(从服务器发送来的头里)是什么，你就能使用HTTPPasswordMgr。

通常人们不关心realm是什么。那样的话，就能用方便的HTTPPasswordMgrWithDefaultRealm。

这个将在你为URL指定一个默认的用户名和密码。

这将在你为特定realm提供一个其他组合时得到提供。

我们通过给realm参数指定None提供给add_password来指示这种情况。

最高层次的URL是第一个要求验证的URL。你传给.add_password()更深层次的URLs将同样合适。

```python
# -*- coding: utf-8 -*-
import urllib2

# 创建一个密码管理者
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

# 添加用户名和密码

top_level_url = "http://example.com/foo/"

# 如果知道 realm, 我们可以使用他代替 ``None``.
# password_mgr.add_password(None, top_level_url, username, password)
password_mgr.add_password(None, top_level_url,'why', '1223')

# 创建了一个新的handler
handler = urllib2.HTTPBasicAuthHandler(password_mgr)

# 创建 "opener" (OpenerDirector 实例)
opener = urllib2.build_opener(handler)

a_url = 'http://www.baidu.com/'

# 使用 opener 获取一个URL
opener.open(a_url)

# 安装 opener.
# 现在所有调用 urllib2.urlopen 将用我们的 opener.
urllib2.install_opener(opener)
```
 
注意：以上的例子我们仅仅提供我们的HHTPBasicAuthHandler给build_opener。
默认的openers有正常状况的handlers：ProxyHandler，UnknownHandler，HTTPHandler，HTTPDefaultErrorHandler， HTTPRedirectHandler，FTPHandler， FileHandler， HTTPErrorProcessor。
代码中的top_level_url 实际上可以是完整URL(包含"http:"，以及主机名及可选的端口号)。
例如：http://example.com/。
也可以是一个“authority”(即主机名和可选的包含端口号)。
例如：“example.com” or “example.com:8080”。
后者包含了端口号。
******************

###5.简单方法和函数

urllib2中的urlopen返回的对象有两个方法很常用，info(),geturl()

`geturl()`非常有用，因为urlopen可能会有重定向，比如说常见的新浪微博中，页面分享的视屏链接在新窗口中打开之后，链接会完全变化，这个时候的链接才是真正的url

```python
import urllib2

lod = 'http://t.cn/8si16mR'
req = urllib2.Request(old)
http = urllib2.urlopen(req)
new = http.geturl
#这个时候的old和new是完全不一样的
```

`info()`返回一个字典，描述了获取的页面的状态，通常是服务器发送过来特定的header

```python
import urllib2
http = urllib2.urlopen('http://www.baidu.com')
print http.info()
```

`proxy`的设置：urllib2会使用环境变量http_proxy来设置HTTP Proxy，如果想在程序中控制proxy，可以设置代理

```python
import urllib2
enable_proxy = True
proxy_handler = urllib2.ProxyHandler({'http':'http://some-proxy.com:8080'})
null_proxy_handler = urllib2.ProxyHandler({})
if enable_proxy:
    opener = urllib.build_opener(porxy_handler)
else:
    opener = urllib.build_opener(null_proxy_handler)
urllib.install_opener(opener)
```

`timeout`的设置：urllib2.urlopen(url,timeout = 10)

在request中加入特定的头：

```python
import urllib2
request = urllib2.Request('http://www.baidu.com')
request.add_header('User-Agent','fake-client')
response = urllib2.urlopen(request)

cookie:
import urllib2
import cookielib
cookie = cookielib.CookieJar()
opener = urllib.build_opener(urllib2.HTTPCoolieProcessor(cookie))
response = opener.open('http://www.baidu.com')
for i in cookie:
    print 'name'+i.name
    print 'value'+i.value
#运行之后就可以得到访问百度的cookie值
```

`表单处理`：从浏览器和抓包工具可以看到我们需要填写哪些表单,通常用字典的形式

```python
import urllib
import urllib2
postdata = urllib.urlencode({
    'username':'xxx'
    'passwd':'xxx'
    ...
})
request = urllib2.Request(url,postdata)
http = urllib2.urlopen(request)
```

`文件下载：`

```python
import urllib
download = urllib.urlretrieve(url)
```

###6.[正则表达式](http://www.jb51.net/article/15707.htm)

###7.实战，用爬虫访问insysu.com

首先浏览器进入我们美到一逼的第三方教务系统 

![1.png](/images/python-spider/1.png)

肯定是需要登录信息的，所以我们先<F12>查看以下登录目标在哪里

![2.png](/images/python-spider/2.png)

太明显了，本页就是登录点

然后我们再看看登录需要提交的东西在哪里，点击登录，成功登录后查看network有一个post，点进去再点header一看就知道了

![3.png](/images/python-spider/3.png)

恩，然后我们肯定是有cookie的，顺便也记录以下就行了

于是开始编码

```python
# =============================================================================
#      FileName: insysu.py
#          Desc: a spider to walk through the isysu.com using your name and passwd
#        Author: huangjin
#         Email: dantangfan@gmail.com
#      HomePage: https://www.github.com/dantangfan
#       Version: 0.0.1
#    LastChange: 2014-04-04 14:48:11
#       History:
# =============================================================================

#!/bin/env python
# -*-coding: utf-8 -*-

import urllib
import urllib2
import cookielib

cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

#your post data

postdata = urllib.urlencode({
    'username':'11331130',
    'password':'09192970'
    })
#make a request
require = urllib2.Request(url = 'http://insysu.com/sign_in',data = postdata)
#visit
result = opener.open(require)
#print
print result.read()
#print cookie
for item in cookie:
    print 'cookie: Name = '+item.name
    print 'cookie: Value = '+ item.value

#visit the target web site after login
result = opener.open('http://www.insysu.com')
print result.read()
```

* 注意的是要先登录，然后才能进入主页面。看看结果如何

![4.png](/images/python-spider/4.png)

貌似达到了预期效果。

接下来就可以进入相应的页面提取要的数据了


