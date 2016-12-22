---
layout: post
title: Python 中的协程
description: yield 语法说起来简单,实际用起来总是绕来绕去,于是这里简单的总结了一下
category: opinion
---

`yield` 语法说起来简单,用起来总是绕来绕去,虽然已经很方便了,但是依然不够方便.
<!-- more -->

### 教科书实例

让我们来看看教科书上都对`yield`有哪些谆谆教诲，这里我随便找了一本书

```
def count(n):
    print "start to count"
    i = 0
    while i < n:
        yield i
        i += 1
    return
```

感觉简直就是在介绍冒泡排序。这还算好，好多书都是只对`yield`一句带过。

**大部分内容来自网上**

###可迭代对象（iterble）
创建一个list，并逐个读取其中的元素，这个过程称之为迭代

```
for i in [1,2,3,4]:
    print i
```

任何支持`for in `操作的对象都称之为可迭代对象，比如（dict,string,tuple,file..），像dict对象一样，任何实现了__iter__()或者__getitem__()方法的类也都是可迭代对象。

这些可迭代对象使用非常方便，因为它能如你所愿的尽可能读取其中的元素，缺点是你不得不把所有的值存储在内存中，当对象有大量元素时，性能会急剧降低。

### 迭代器简介
之所以我们能对不同的对象进行迭代，是因为这些可迭代对象都遵循了一个共同的协议（姑且称之为协议），也就是迭代器。

迭代器代表一个数据流对象，当一个可迭代对象作为参数传递给内建函数iter()时，它会返回一个迭代器对象。
不断重复调用迭代器对象的next()方法可以逐次地返回数据流中的每一项，当没有更多数据可用时，next()方法会抛出异常StopIteration。
此时迭代器对象已经枯竭了，之后调用next()方法都会抛出异常StopIteration。迭代器需要有一个__iter()__方法用来返回迭代器本身，因此它也是一个可迭代的对象。

```
>>> items = [1, 4, 5] 
>>> it = iter(items) 
>>> it.next()
1
>>> it.next() 
4
>>> it.next() 
5
>>> it.next()
Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    StopIteration
    >>>
```

通常没必要自己来处理迭代器本身或者手动调用iter()，for语句会自动调用iter()，它会在循环中创建一个临时变量来持有这个迭代。 

那么for循环调用一个可迭代对象的时候到底发生了什么呢？下面是for循环的的简化版本

```
_iter = iter(obj)
while 1:
    try:
        x = _iter.next()
    except StopIteration:
        break
        # statements
...
```

这里将可迭代对象换个方式定义：支持`iter()`和`next()`操作的对象都被称之为可迭代对象。

也就是说，即便是用户自定义的对象，只要满足了上述条件，也是可迭代对象。如下for循环

```
>>> for x in countdown(10): 
...  print x,
...
10 9 8 7 6 5 4 3 2 1
>>>

>>> c = countdown(5) 
>>> for i in c:
...     print i, 
...
5 4 3 2 1 
>>>
```

我们只需要实现`__iter__`和`next()`就能满足

```
class countdown(object):
    def __init__(self,start):
        self.count = start
    def __iter__(self):
        return self
    def next(self):
        if self.count <= 0:
            raise StopIteration
        r = self.count
        self.count -= 1
        return r
```

同样是上面方法，我们也可以使用yield实现。不同的是，这里我们`生成了`一系列的数字，而不是返回数字

```
def countdown(n):
    while n > 0:
        yield n
        n -= 1
>>> for i in countdown(5):
... print i, 
...
5 4 3 2 1
>>>
```

### 生成器
上面的yield实现就是一种生成器，生成器函数跟普通的函数工作方式完全不同：当调用一个生成器函数的时候，他会立即返回一个生成器对象，而不是执行这个函数

```
def countdown(n):
    print "Counting down from", n
        while n > 0:
￼￼          yield n 
            n -= 1
>>> x = countdown(10)  # 这里我们可以发现，『counting down from 10』不会立即打印出来
>>> x                  # 这里我们可以看到，x实际上是一个对象
<generator object at 0x58490> 
>>>
>>> x.next()  # 这里才打印出来，并且执行了第一个yield
Counting down from 10
10
>>> x.next()
9
>>> x.next()
8
...
>>> x.next()
1
>>> x.next() # 当生成器函数执行完（有可能是return），再调用next的时候就抛出异常了
Traceback (most recent call last):
    File "<stdin>", line 1, in ?
StopIteration
```

由上面代码我们可以看出，用生成器来实现可迭代对象不仅看起来更牛逼，而且还更简单，都不用去管iter()之类的了。

生成器对象比起用iter()实现的可迭代对象来说更轻量级，但是你只可以迭代他们一次，不能重复迭代，因为它并没有把所有值存储在内存中，而是实时地生成值。
要想再循环一圈就需要再初始化一个对象，而list等可迭代对象却可以无限次的使用。

### 生成器表达式

生成器表达式其实很简单，我们平时经常用的列表表达式

```
a = [i for i in range(5)]
```

生成器表达式就是这样

```
>>> a = (i for i in range(5))
>>> a
<generator object <genexpr> at 0x107bb6960>
```

这个表达式等价于

```
for i in range(5):
    yield i
```

### yield关键字

Yield是关键字，它类似于return，只是函数会返回一个生成器。

```
def gen():
    seq = range(2)
    for i in seq:
        yield i*3
>>> print g
<generator object gen at 0x1067dfe60>
>>> g.next()
0
>>> g.next()
3
>>> g.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

为了完全弄懂yield，你必须清楚的是： **当函数被调用时，函数体中的代码是不会运行的，函数仅仅是返回一个生成器对象** 。

执行第一个next()的时候，代码将会从函数的开始处运行直到遇到yield为止（这里返回了循环的第一个值），然后直到下次调用next()的时候从前一次停下的地方继续执行，一直执行到遇到yield为止，如此反复。
一旦函数运行再也没有遇到yield时，生成器就被认为是空的，这个生成器就会永远停在这里，而不再执行其他代码了。这有可能是因为循环终止，也有可能是因为满足了其他if/else条件而退出了。

```
flag = True
def gen():
    global flag
    while flag:
        yield 1
>>> g=gen()
>>> g.next()
1
>>> g.next()
1
>>> flag=False
>>> g.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>> flag=True
>>> g.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>>
```

如上例，当flag为False之后g停止执行，即便再次将flag置True，g依然不能执行。如果还想执行，就必须再初始化一个generator对象。

### itertools

标准库中的itertools包提供了更加灵活的生成循环器的工具，这些工具的输入大都是已有的循环器。
另一方面，这些工具完全可以自行使用Python实现，该包只是提供了一种比较标准、高效的实现方式。这也符合Python“只有且最好只有解决方案”的理念。

```
import itertools
c = [1, 2, 3]
t = itertools.permutations(c)
print list(t)
[(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
```

## yield的用法

Python中 yield 是一个关键词，它可以用来创建协程。

1. 当调用 yield value 的时候，这个 value 就被返回出去了，CPU控制权就交给了协程的调用方。调用 yield 之后，如果想要重新返回协程，需要调用Python中内置的 next 方法。
2. 当调用 y = yield x 的时候，x被返回给调用方。要继续返回协程上下文，调用方需要再执行协程的 send 方法。在这个列子中，给send方法的参数会被传入协程作为这个表达式的值(本例中，这个值会被y接收到)。

### 例1

比如说我们有格式如下的日志文件，我们要计算一共传输了多少字节，也就是把每一行的最后一个数字加起来

```
81.107.39.38 -  ... "GET /ply/ HTTP/1.1" 200 7587
81.107.39.38 -  ... "GET /favicon.ico HTTP/1.1" 404 133
```

传统的做法是这样

```
wwwlog = open("access-log")
total = 0
for line in wwwlog:
    bytestr = line.rsplit(None,1)[1]  # split 函数默认从左边开始切割，这个是从右边，没用过的自行反省
    total += int(bytestr)
print "Total", total
```

用生成器的做法是这样的

```
wwwlog     = open("access-log")
bytecolumn = (line.rsplit(None,1)[1] for line in wwwlog)
bytes      = (int(x) for x in bytecolumn)
print "Total", sum(bytes)
```

代码简短了好多，并且编程的思考方式也不一样了，是不是有点像传说中的函数式编程。。。

生成器实现的日志处理是基于pipeline的，让数据在多个组件之间传输。

### 例2

我们有很多日志文件分布在不同的文件夹里，而且有些日志文件还是压缩的，我们要找出所有满足条件的文件名

```
foo/
        access-log-012007.gz
        access-log-022007.gz
        access-log-032007.gz
        ...
        access-log-012008
bar/
        access-log-092007.bz2
        ...
        access-log-022008
```

让我们先来认识一下`os.walk()`这个函数，它在遍历系统文件的时候十分有用

```

import os
for path, dirlist, filelist in os.walk(topdir):
    # path     :  Current directory
    # dirlist  :  List of subdirectories
    # filelist :  List of files
...
```

要完成目标，我们可以这样做，这也是最容易想到的了

```
find / -name '*.py'
```

当然，我们要用的是python

```
import os
import fnmatch

def gen_find(filepat,top):
    for path, dirlist, filelist in os.walk(top):
        for name in fnmatch.filter(filelist,filepat):
            yield os.path.join(path,name)
            
# Example use
if __name__ == '__main__':
    lognames = gen_find("access-log*","www")
    for name in lognames:
        print name
```

同理，我们还可以用python实现一些bash，如cat、grep等

```
def gen_cat(sources):
    for s in sources:
        for item in s:
            yield item

# Example use

if __name__ == '__main__':
    from genfind import  gen_find
    from genopen import  gen_open

    lognames = gen_find("access-log*","www")
    logfiles = gen_open(lognames)
    loglines = gen_cat(logfiles)
    for line in loglines:
        print line,
```

### 例3

我们经常用`tail -f xxx`，那用python 应该怎样实现呢

```
import time
def follow(thefile):
    thefile.seek(0,2) # 到文件末尾
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

if __name__ == '__main__':
    logfile = open("run/foo/access-log","r")
    loglines = follow(logfile)
    for line in loglines:
        print line,
```

### 例4，我们看看加上装饰器有啥效果

```
def consumer(func):
    def start(*args,**kwargs):
        c = func(*args,**kwargs)
        c.next()
        return c
    return start

# Example
if __name__ == '__main__':

    @consumer
    def recv_count():
        try:
            while True:
                n = (yield)
                print "T-minus", n
        except GeneratorExit:
            print "Kaboom!"

    r = recv_count()
    for i in range(5,0,-1):
        r.send(i)

    r.close()
```

如果我们再包装一下，让func的返回值是一个future，就跟tornado很像了。

### 一个更具体的例子-实现一个简单爬虫

#### 首先，我们看一个最常见的以纯 python socket 实现的爬虫

```
def fetch(url):
    sock = socket.socket()
    sock.connect(('xkcd.com', 80))
    request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
    sock.send(request)
    response = b''
    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)
    # 然后剥离出 link 
    #links = parse_links(response)
    #q.append(links)
```

#### 然后，我们来看看一个非阻塞 socket 的实现

```
from selectors import DefaultSelector, EVENT_WRITE

selector = DefaultSelector()
sock = socket.socket()
sock.setblocking(False)
try:
    sock.connect(('xkcd.com', 80))
except BlockingIOError as e:
    raise e

def connected():
    selector.unregister(sock.fileno())
    print('connected')

selector.register(sock.fileno(), EVENT_WRITE, connected)
while True:
    events = selector.select()
    for key, mask in events:
        callback = key.data
        callback()
```

虽然没有感受到非阻塞的闪光点，但是我还是马不停蹄的用回调的方式写一个爬虫

```
selector = DefaultSelector()
urls_todo = set(['/'])
urls_seen = set(['/'])
stopped = False
class Fetcher(object):
    def __init__(self, url):
        self.response = b''
        self.url = url
        self.sock = None

    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            sock.conn(('xkcd.com', 80))
        except BlockingIOError:
            pass
        selector.register(self.sock.fileno(), EVENT_WRITE, self.connected)

    def connected(self, key, mask):
        print('connected')
        selector.unregister(key.fd)
        request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(self.url)
        self.sock.send(request)
        selector.register(key.fd, EVENT_WRITE, self.read_response)

    def read_response(self, key, mask):
        global stopped
        chunk = self.sock.recv(4096)
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)
            links = self.parse_links()

            for link in links.different(urls_seen):
                urls_todo.add(link)
                Fetcher(link).fetch()
            urls_seen.update(links)
            urls_todo.remove(self.url)
            if not urls_todo:
                stopped = True

Fetcher('/353').fetch()

def loop():
    while not stopped:
        events = selector.select()
        for key, mask in events:
            callback = key.data
            callback(key, mask)
loop()
```

实际上效率确实会提高不少，但是写起来未免也太复杂了吧

#### 然后再用 coroutine 写一个吧
准备好，下面要开始绕圈子了。 python 其实不是那么易用的

比如，首先我们先把 connected 放进来

```
class Future:
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)

class Fetcher:
    ...
    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect(('xkcd.com', 80))
        except BlockingIOError:
            pass
        f = Future()
        def connected(key, mask):
            f.set_result(None)

        selector.register(self.sock.fileno(), EVENT_WRITE, connected)
        yield f
        selector.unregister(self.sock.fileno())
        print('connected')

class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            return
        next_future.add_done_callback(self.step)

f = Fetcher('/353').fetch()
Task(f)
loop()
```

下面，我们就来捋一捋。

1.首先，f是一个 generator 并不会马上执行 ————> 
2.到 Task 中，初始化的时候第一次执行了 self.step ，这个时候， f 遇到了 fetch 函数中的第一个 yield ，并将值送给了 step 中的 nest_future ，并且把 step 函数注册为 next_future 的回调函数————> 
3.接下来开始 loop ————> 
4.当发生 EVENT_WRITE 事件的时候，执行 connected 函数，connected 函数执行 Future.set_result 函数 ————> 
5.set_result 函数执行了里面所有的 callback，也包括了第2步的step函数 ————>
6.step函数执行了 self.coro.send ，这时候会 except StopIteration，这个 Task 也就结束了，恰好，fetch 函数中的 yield 就返回了，而这个时候确实也 connect 成功了

就是这么绕来绕去，我也不知道怎么回事了。

#### 虽然很绕，但是不妨碍我要把 read_response 也加进来

```
class Fetcher:
    ...
    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect(('xkcd.com', 80))
        except BlockingIOError:
            pass
        f = Future()
        def connected(key, mask):
            f.set_result(None)

        selector.register(self.sock.fileno(), EVENT_WRITE, connected)
        yield f
        selector.unregister(self.sock.fileno())
        print('connected')

        request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(self.url)
        self.sock.send(request)
        while True:
            f = Future()
            def on_readable():
                f.set_result(self.sock.recv(4096))

            selector.register(self.sock.fileno(), EVENT_WRITE, on_readable)
            chunk = yield f
            selector.unregister(self.sock.fileno())
            if chunk:
                self.response += chunk
            else:
                break  # done
```

这里接着前面的第6步分析

6.step函数执行了 self.coro.send ，这里会继续将 step 当成回调函数，connect 成功了
7.fetch函数继续执行，直到 while 循环中的第一次 yield
8.再次等待 selector 中的可写事件，发生事件时，执行 on_readable 函数，并执行里面的所有回调函数，包括了 step(future) 这个函数，在 Future.set_result 函数中
我们执行回调函数的时候是 fn(self) ，于是，这里 step 函数中 self.coro.send(future.result) 就直接将 sock.recv(4096) 返回到了 chunk 中，如此循环反复

看起来确实是很复杂的,每一步都要精心设计，正常情况下我们也不能轻易写出逻辑这么绕的代码,但是他效率确实十分搞。

#### todo 
还有 `yield from` 也是个高级的关键字,但是平时多用 python2 ,就没有深入去研究了. 有空再看吧


参考链接[stackoverflow](http://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python)
