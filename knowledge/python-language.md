python 语言基础

python 轻度使用者，知道语法和库就行了；python 中度使用者，就需要知道下面这些基础知识；python 重度使用者，就需要去看 python 的实现了。

## 语言基础

### python是如何执行代码的，也就是说解释型语言如何执行
http://www.cnblogs.com/kym/archive/2012/05/14/2498728.html
### 什么是绑定，把一个对象绑定到一个变量意味着什么
### 什么是generator，可以用来干什么
见generator-coroutine.md

1. 执行效率
2. 内存

```
a = [i for i in range(1000)]
for i in a:
    print i
b = [j for j in xrange(1000)]
for j in b:
    print j
```

当列表非常大的时候, ab的差距就体现出来了.a要将所有内容放入内存,而b只是生成当前值
range() 函数是先将所有的 1000 个数字生成一个数组，然后放到一个临时变量中，然后再来遍历
xrange() 是使用 yield 这样的方法，在遍历的过程中每次生成一个数字，所以不耗内存

### 局部变量和全局变量的规则是什么

```
#!/usr/bin/python
# Filename: variable_localglobal.py
def fun1(a):
            print 'a:', a
            a= 33;
            print 'local a: ', a
a = 100
fun1(a)
print 'a outside fun1:', a
def fun2():
           global b
           print 'b: ', b
           b = 33
           print 'global b:', b
b =100
fun2()
print 'b outside fun2', b
```

输出

```
$ python variable_localglobal.py
a: 100
local a: 33
a outside fun1: 100
b :100
global b: 33
b outside fun2: 33
```

### 什么场景适合使用python
测试\脚本\爬虫

### 理解python中的dict，是如何实现的
http://blog.csdn.net/digimon/article/details/7875789

### list切片操作
a[::]

### 实现一个可迭代对象

```
class iterobj(object):
    def __init__(self, n):
        self.n = n
    def __iter__(self):
        return self
    def __next__(self):
        if self.n < 0:
            raise StopIteration()
        r = self.n
        self.n -= 1
        return r
```

### python传参数原理
见python-argument.py

没有定性的说是传值还是传引用,跟对象本身有关,是否是可变对象

### 列举python的魔术方法
http://pyzh.readthedocs.org/en/latest/python-magic-methods-guide.html

### pickle原理
[http://python3-cookbook.readthedocs.org/zh_CN/latest/c05/p21_serializing_python_objects.html](http://python3-cookbook.readthedocs.org/zh_CN/latest/c05/p21_serializing_python_objects.html)
将文件转化成字节流
pickle 不是不能序列化函数,而是函数包含闭包 [https://www.zhihu.com/question/28566219](https://www.zhihu.com/question/28566219)

### 两种copy的原理，深赋值和浅赋值copy和deepcopy
[http://my.oschina.net/leejun2005/blog/145911](http://my.oschina.net/leejun2005/blog/145911)
**重要**
在 python 中赋值语句总是建立对象的引用值，而不是复制对象。因此，python 变量更像是指针，而不是数据存储区域.

```
a = [1,[2,3],4]
b = a[:] # 浅拷贝,只会将字面值拷贝给b,但 a[1] 和 b[1]指向的地址还是一样的
b=a[:], copy.copy(a), list(a) 都是浅拷贝
b = copy.deepcopy(a) 是深拷贝,其实就是递归的 copy.copy
```

### python cookie处理包

### list, set, tuple, dict对比
http://m.blog.csdn.net/blog/fuxingwe/38085901
http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001386819318453af120e8751ea4d2696d8a1ffa5ffdfd7000
三者的用法可参考：http://blog.sina.com.cn/s/blog_540775a30101bhhx.html

- Tuple 一旦创建即不能进行修改(删除/增加/修改元素)，但是其访问效率较高，且能保护常量数据不被更改，所以适合于存储一些常量数据
- List 适合于需要动态增删改的数据集，但不适用于需要查找的使用；因为其实现类似于C中的数组，也不适应于需要经常在 list 之间插入数据的场景。
- Dict 就像很多语言中的 hash，hash数据结构存储了数据，以达到快速定位的功能

### python中的强制类型转换，对比c语言
python是直接改变了变量指向的地址，c语言是直接操作当前地址，改变解释方式

### python中的self

### python中内存管理方式

### python垃圾回收机制
- Python在内存中存储了每个对象的引用计数（reference count）。如果计数值变成0，那么相应的对象就会小时，分配给该对象的内存就会释放出来用作他用。
- 偶尔也会出现引用循环（reference cycle）。垃圾回收器会定时寻找这个循环，并将其回收。举个例子，假设有两个对象o1和o2，而且符合o1.x == o2和o2.x == o1这两个条件。如果o1和o2没有其他代码引用，那么它们就不应该继续存在。但它们的引用计数都是1。
- Python中使用了某些启发式算法（heuristics）来加速垃圾回收。例如，越晚创建的对象更有可能被回收。对象被创建之后，垃圾回收器会分配它们所属的代（generation）。每个对象都会被分配一个代，而被分配更年轻代的对象是优先被处理的。

### python会出现内存泄露吗
如果对象实现了__del__函数，那么对象间的交叉引用将导致__del__无法被调用，而本该在__del__中释放的资源(比如数据库的连接)将无法释放某些全局变量占用的资源不能被释放
举例:比如使用的是数据库短连接,每次都忘了关闭,就会造成内存泄露

### tornado template、coroutine、stact_context是怎么实现的

### 标准库线程安全的队列是哪一个？不安全的是哪一个？logging是线程安全的吗？

### python适合的场景有哪些？当遇到计算密集型任务怎么办？
io 多的情况,计算密集的情况可以用 c-extend 比如 ctyps/pyx/pyobject

### python高并发解决方案？我希望听到twisted->tornado->gevent，能扯到golang,erlang更好
twisted 没用过,tornado 并不是最好的,特别是涉及到使用其他库的时候,gevent 同样有问题,特别是遇到有 c 实现的时候

### 函数闭包
[http://book42qu.readthedocs.org/en/latest/python/python-closures-and-decorators.html](http://book42qu.readthedocs.org/en/latest/python/python-closures-and-decorators.html)

1. 简单的说,闭包就是一个捕捉了（或者关闭）非本地变量（自由变量）的代码块（比如一个函数）
2. 闭包是在其词法上下文中引用了自由变量的函数。

自己理解:要形成闭包，首先得有一个嵌套的函数，即函数中定义了另一个函数，闭包则是一个集合，它包括了外部函数的局部变量，这些局部变量在外部函数返回后也继续存在，并能被内部函数引用。

### 什么是 lambda函数？它有什么好处？另外 python在函数式编程方面提供了些什么函数和语法？
Python允许你定义一种单行的小函数。
定义lambda函数的形式如下：labmda 参数：表达式lambda函数默认返回表达式的值。
你也可以将其赋值给一个变量。lambda函数可以接受任意个参数，包括可选参数，但是表达式只有一个：

    g = lambda x, y: x*y   
    g(3,4) 
    #12   
    g = lambda x, y=0, z=0: x+y+z   
    g(1) 
    #1  
    g(3, 4, 7) 
    #14 

也能够直接使用lambda函数，不把它赋值给变量： 

    (lambda x,y=0,z=0:x+y+z)(3,5,6) 
    #14 
    
如果你的函数非常简单，只有一个表达式，不包含命令，可以考虑lambda函数。否则，你还是定义函数才对，毕竟函数没有这么多限制

语法有map,reduce, filter, zip


### 知道 greenlet、stackless 吗？说说你对线程、协程、进程的理解；
greenlet 类似于 goto 语句的功能，但是在函数或者说微线程之间实现了跳转，且在结束后
能自动回到调用处
一个 “greenlet” 是一个很小的独立微线程。可以把它想像成一个堆栈帧，栈底是初始调用，
而栈顶是当前 greenlet 的暂停位置。你使用 greenlet 创建一堆这样的堆栈，然后在他们之间
跳转执行。跳转不是绝对的：一个 greenlet 必须选择跳转到选择好的另一个 greenlet，这会
让前一个挂起，而后一个恢复。两 个 greenlet 之间的跳转称为 切换(switch) 。
当你创建一个 greenlet，它得到一个初始化过的空堆栈；当你第一次切换到它，他会启动指
定的函数，然后切换跳出 greenlet。当最终栈底 函数结束时， greenlet 的堆栈又编程空的了，
而 greenlet 也就死掉了。greenlet 也会因为一个未捕捉的异常死掉。
stackless 是 python 的一个协程实现版本？还没有仔细看。
线程，进程是比较经典的概念了，进程可以包括文件句柄等系统资源的单位，线程一般是
现代 CPU 的基本调度单位
而协程是通过用户调度，切换的消耗要小于线程/进程的切换。
协程的优势在于可以自己控制切换，适合于顺序执行的一些情况，而线程更加适合并行处
理数据的情况；同时使用协程可以控制调度，减少切换的消耗。

### 关于 python 程序的运行性能方面，有什么手段能提升性能？
合理的使用数据结构：比如由于 dict 使用了 hash table，当需要经常在大容量 list 中使用查找时，将 list 转换成 dict 将大大提高性能
在一些性能瓶颈问题上，考虑使用 c/c++库来实现，将大大提高程序性能

1. 使用内建函数
2. 使用 join()连接字符串.
3. 使用 Python 多重赋值，交换变量
4. 尽量使用局部变量
5. 尽量使用 "in"
6. 使用延迟加载加速
7. 为无限循环使用 "while 1"
8. 使用 list comprehension
9. 使用 xrange()处理长序列
10. 使用 Python generator
11. 了解 itertools 模块
12. 学习 bisect 模块保持列表排序
13. 理解 Python 列表，实际上是一个数组
14. 使用 dict 和 set 测试成员
15. 使用 Schwartzian Transform 的 sort()
16. Python 装饰器缓存结果
17. 理解 Python 的 GIL（全局解释器锁）

### 什么是pyc文件,为什么需要pyc
pyc是一种二进制文件，是由py文件经过编译后，生成的文件，是一种byte code，py文件变成pyc文件后，加载的速度有所提高，而且pyc是一种跨平台的字节码，
是由python的虚拟机来执行的，这个是类似于JAVA或者.NET的虚拟机的概念。pyc的内容，是跟python的版本相关的，不同版本编译后的pyc文件是不同的，2.5编译的pyc文件，2.4版本的 python是无法执行的。

### dict中的.items() .iteritems()区别
一个生成全部，一个是迭代器

### 为什么不能并行计算？Python的线程实际上是使用单核在运行。
在大多数系统上，Python同时支持消息传递和基于线程的并发编程。
尽管大多数程序员熟悉的往往是线程接口，但实际上Python线程受到的限制有很多。
尽管最低限度是线程安全的，但Python解释器还是使用了内部的GIL(Global Interperter Lock,全局解释器锁定)，在任意指定的时刻只能在一个处理器上运行。
尽管GIL经常是Python社区中争论的热点，但在可以预见的将来它都不可能消失。


### 元类

### @staticmethod, @classmethod

### python 的自省机制

### 格式化 %s 和 .format

### 鸭子类型
新类和旧类 http://www.cnblogs.com/btchenguang/archive/2012/09/17/2689146.html

python3 已经不存在旧类了，这个问题只需要了解一下

### __init__ 和 __new__ 的区别

### 垃圾回收
1. 引用计数
2. 标记清除
3. 分代回收


## 简单编程

### 列表去重的几种方法

```
a = [1,3,3,4,5,3,7,8]
newa = []
for i in a:
    if i not in newa:
        newa.append(i)

newa = list(set(a))  # 但是这样是乱序的,还需要排序
newa.sort(a.index)

newa = filter(lambda x, y: x if y in x else x + [y], [[],] + a)

{}.fromkeys(a).keys()  # 这个会直接排序了
```

### 实现一个简单的 lru-cache

**重要,一定要熟记在心啊**
要实现 lru ,就必须要有过期时间(可以不要), 最近访问时间, 元素最大数量这几个指标
[https://github.com/the5fire/Python-LRU-cache/blob/master/lru.py](https://github.com/the5fire/Python-LRU-cache/blob/master/lru.py)

```
from collections import OrderedDict
import time

class Dict(object):
    def __init__(self, expire=3600, max_size=1024):
        self.expire_at = expire
        self.max_size = max_size
        self.expire = OrderdDict()
        self.access = OrderedDict()
        self.value
    
    def __getitem__(self, key):
        t = self.now
        # 删除以前的访问记录,并将当前记录放到最后(也就是最近访问)
        del self.access[key]
        self.access[key] = t
        self.clear()
        return self.value[key]
    
    def __setitem__(self, key, value):
        t = self.now
        self.expire[key] = t + self.expire_at
        self.access[key] = t
        self.value[key] = value
        self.clear()
    
    def __delete__(self, key):
        if self.has_key(key):
            del self.values[key]
            del self.access[key]
            del self.expire[key]
    
    def clear():
        keys = self.value.keys()
        t = self.now
        # 先删除超时的
        for k in keys:
            if self.expire[k] < t:
                self.__delete__(k)
            else:
                break
        llen = len(keys)
        # 当达到最大大小时,删除最久没访问的
        while llen > self.max_size:
            self.__delete__(self.access.keys()[0])
    
    def has_key(self, key):
        return self.values.has_key(key)
    
    @property
    def now(self):
        return int(time.time())

def lru_cache(expire=3600, max_size=1024):
    cache = Dict(expire, max_size)
    def deco(func):
        def __(*args, **kwargs):
            key = repr((args, kwargs)) + '#' + func.__name__
            try:
                return cache[key]
            except:
                value = func(*args, **kwargs)
                cache[key] = value
                return value
        return __
    return deco
```
### partial 函数的实现
其实就是使用闭包的方式实现的,也可以说就是一个装饰器而已

```python
def partial(func, *args, **kwargs):
    def _(*fn_args, **fn_kwargs):
        kwargs.update(fn_kwargs)
        return func(*args + fn_args, **kwargs)
    return _
```

### python单例模式

```python
class Singleton(objict):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            #setattr(cls, "_instance", object.__new__(cls, *args, **kwargs))
            setattr(cls, "_instance", super(Singleton, cls).__new__(*args, **kwargs))
        return getattr(cls, "_instance")

# 这个用装饰器好理解
def singleton(cls):
    _instance = {}
    def _(*args, **kwargs):
        if not _instance.get(cls):
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return _
```

### 检查一个对象属性的方法
dir(obj)

### list 排序

alist = [{'name':'a','age':20},{'name':'b','age':30},{'name':'c','age':25}]， 请按 alist 中元素的age 由大到小排序；

```python
alist.sort(key=lambda x: x['age'])
```

### list 合并
alist = ['a','b','c','d','e','f'], blist = ['x','y','z','d','e','f']，请用简洁的方法合并这两个 list， 并且 list 里面的元素不能重复；

```
c = list(set(a)|set(b))

c = list(set(a.extend(b)))
```

### 实现一个stack，其实list本身就可以当stack用
这里我们不需要把size记录下来，因为 list 是指针数组实现的

```
class Stack:
    def __init__(self):
        self.items = []
    def __iter__(self):
        return self.items.__iter__()
    def pop(self):
        return self.items.pop()
    def top(self):
        if len(self.items) > 0:
            return self.items[len(self.items)-1]
    def push(self, item):
        self.items.append(item)
    def empty(self):
        self.items = []
    def size(self):
        return len(self.items)
```

### 删除list中重复元素，保持顺序不变

```
r = list(set(L))
sorted(r, key=lambda x: L.index(x))
```

