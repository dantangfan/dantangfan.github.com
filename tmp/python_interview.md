#python 基础
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
b = [j for j in range(1000)]
for j in b:
    print j
```

当列表非常大的时候, ab的差距就体现出来了.a要将所有内容放入内存,而b只是生成当前值

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

### python中怎么跨文件共享全局变量，是如何实现的
通过 import xxx
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

### 推荐一本看过最好的python书籍？ 拉开话题好扯淡

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

### 语法糖
语法糖（Syntactic sugar），也译为糖衣语法，是由英国计算机科学家彼得·约翰·兰达（Peter J. Landin）发明的一个术语，指计算机语言中添加的某种语法，这种语法对语言的功能并没有影响，但是更方便程序员使用。通常来说使用语法糖能够增加程序的可读性，从而减少程序代码出错的机会。

### partial 函数的实现
其实就是使用闭包的方式实现的,也可以说就是一个装饰器而已

```
def partial(func, *args, **kwargs):
    def _(*fn_args, **fn_kwargs):
        kwargs.update(fn_kwargs)
        return func(*args + fn_args, **kwargs)
    return _
```

### python单例模式

```
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

### 什么是 lambda函数？它有什么好处？另外 python在函数式编程方面提供了些什么函数和语 法？
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

### range xrange区别（python3中统一成了xrange，并命名为range）
一个列表 一个迭代器 xrange

### 为什么不能并行计算？Python的线程实际上是使用单核在运行。
在大多数系统上，Python同时支持消息传递和基于线程的并发编程。
尽管大多数程序员熟悉的往往是线程接口，但实际上Python线程受到的限制有很多。
尽管最低限度是线程安全的，但Python解释器还是使用了内部的GIL(Global Interperter Lock,全局解释器锁定)，在任意指定的时刻只能在一个处理器上运行。
尽管GIL经常是Python社区中争论的热点，但在可以预见的将来它都不可能消失。

### 检查一个对象属性的方法
dir(obj)

### list 对象 alist [{'name':'a','age':20},{'name':'b','age':30},{'name':'c','age':25}]， 请按 alist 中元素的age 由大到小排序；

```
alist.sort(key=lambda x: x['age'])
```

### 两个 list 对象 alist ['a','b','c','d','e','f'], blist ['x','y','z','d','e','f']，请用简洁的方法合并这两个 list， 并且 list 里面的元素不能重复；

```
c = list(set(a)|set(b))

c = list(set(a.extend(b)))
```

### 实现一个stack，其实list本身就可以当stack用

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



# 数据库相关

### 数据库的4个事务隔离级别是什么？它们之间的区别是什么？是如何实现的？MySQL的默认级别是什么？
 不清楚,没用过

### 谈谈mysql字符集和排序规则？
用 `show character set` 和 `show collation` 来查看支持的字符集,最常见的排序规则是利用大小写或字母的二进制编码进行排序。
不太懂

### varchar与char的区别是什么？大小限制？utf8字符集下varchar最多能存多少个字符
#### varchar 

    保存了可变长度的字符串，是使用较多的字符串类型。它比固定长度类型占用更少的存储空间，因为它只占用了实际需要空间，比较灵活。
    使用额外的1到2字节来存储值得长度。如果列的最大长度小于或等于255，则使用1字节，否则使用2字节。
    的灵活性能节约不少空间，对性能有一定的帮助。但因为是可变长度类型，所以在更新的时候通常长度会发生变化，引发多余的操作。如果行的长度增加并不再适合原始位置时，具体的行为则会和存储引擎相关。
    当长度大于平均长度，并且很少更改的时候，通常适合使用varchar。这样就不会轻易发生磁盘碎片问题。当然跟字符集的选择也有一定的关系，比如UTF8占的长度GBK就不一样，所以每个字符可能会占用不同的存储空间。

#### char
    
    char是固定长度类型，MySQL会为它分配足够的空间。当保存char值得时候，MySQL会自动把末尾空格清除。比较的时候也是同样清除。
    char最佳的使用方案就是存储很短的字符串或者长度近似相同的字符串的时候非常有用。如固定长度的MD5、定长值、短网址等等，不会容易产生碎片，对于很短的值效率高于varchar。char(1)字符串对于单字节字符来说只会占用1个字节，但是varchar(1)会占用2个字节，其中1个字节用来存储长度信息。

####  varchar 最大能放多少个 utf8
> varchar(n) 表示n个字符，无论汉字和英文，MySql都能存入 n 个字符，仅实际字节长度有所区别
mysql的记录行长度是有限制的，不是无限长的，这个长度是64K，即65535个字节，对所有的表都是一样的。
MySQL对于变长类型的字段会有1-2个字节来保存字符长度。
当字符数小于等于255时，MySQL只用1个字节来记录，因为2的8次方减1只能存到255。
当字符数多余255时，就得用2个字节来存长度了。
在utf-8状态下的varchar，最大只能到 (65535 - 2) / 3 = 21844 余 1。
在gbk状态下的varchar, 最大只能到 (65535 - 2) / 2 = 32766 余 1

### primary key和unique的区别？
- Primary key的1个或多个列必须为NOT NULL，如果列为NULL，在增加PRIMARY KEY时，列自动更改为NOT NULL。而UNIQUE KEY 对列没有此要求
- 一个表只能有一个PRIMARY KEY，但可以有多个UNIQUE KEY
- 主键和唯一键约束是通过参考索引实施的，如果插入的值均为NULL，则根据索引的原理，全NULL值不被记录在索引上，所以插入全NULL值时，可以有重复的，而其他的则不能插入重复值。

### 外键有什么用，是否该用外键？外键一定需要索引吗？
关系型数据库中的一条记录中有若干个属性，若其中某一个属性组(注意是组)能唯一标识一条记录，该属性组就可以成为一个主键
比如

```
学生表(学号，姓名，性别，班级) 
其中每个学生的学号是唯一的，学号就是一个主键 
课程表(课程编号,课程名,学分) 
其中课程编号是唯一的,课程编号就是一个主键 
成绩表(学号,课程号,成绩)
```

成绩表中单一一个属性无法唯一标识一条记录，学号和课程号的组合才可以唯一标识一条记录，所以 学号和课程号的属性组是一个`主键` 
  
成绩表中的学号不是成绩表的主键，但它和学生表中的学号相对应，并且学生表中的学号是学生表的主键，则称成绩表中的学号是学生表的`外键`,同理 成绩表中的课程号是课程表的外键 
定义主键和外键主要是为了维护关系数据库的完整性;主键是能确定一条记录的唯一标识;外键用于与另一张表的关联。是能确定另一张表记录的字段，用于保持数据的一致性。

1. 互联网行业应用不推荐使用外键： 用户量大，并发度高，为此数据库服务器很容易成为性能瓶颈，尤其受IO能力限制，且不能轻易地水平扩展；若是把数据一致性的控制放到事务中，也即让应用服务器承担此部分的压力，而引用服务器一般都是可以做到轻松地水平的伸缩；
因为也没用过,所以不知道太多

### MySQL的存储引擎，InnoDB的索引的实现算法、具体在硬盘上怎么存的，索引B+Tree的叶子节点存储的具体数据是什么

### mysql索引原理及慢查询优化
http://tech.meituan.com/mysql-index.html
http://blog.codinglabs.org/articles/theory-of-mysql-index.html

### 怎么在mysql中储存树形结构数据（比如节点分支，知乎的话题节点）
https://www.zhihu.com/question/20417447/answer/15078011
http://blog.csdn.net/imagse/article/details/4240998

### 为什么SELECT * FROM table WHERE field = null不能匹配空的字段？

### 什么是ACID(原子性，一致性，隔离性，持久性)原则？

### 什么场景用redis，为什么mysql不适合？
[http://timyang.net/tag/redis/](http://timyang.net/tag/redis/)
Memcache当容量到达瓶颈会 截取LRU链以释放空间。

暂时还没用 redis 做过数据库

1. 缓存

2. 数据库

- 访问量大
- key value或者key list数据结构
- 容量小，可控，可以全部放入内存。由于Redis是单线程设计，因此大value会导致后续的请求一定的堵塞。另外hashset当hgetall时候由于存在遍历操作，也不适合集合太大。如果数据超过单机容量可以使用常规的sharding方法分布到多台机
- 需持久化的场景

 MySQL与Redis各自适合什么样的场景？
数据冷热？
数据大小？
数据量级？
数据增长速度？
是否持久化？
访问量(read/write)？
请求性能要求？

### redis内存满了会怎么样？
redis 相比 mysql 有几个缺点：

1. 内存占用巨大 
2. 持久化并不一定是实时的，此时掉电或者其他故障可能会有大量的数据丢失 

过期时间有两种机制

- 被动过期——client访问key时，判断过期时间选择是否过期
- 主动过期——默认使用valatile-lru

        volatile-lru：从已设置过期时间的数据集中挑选最近最少使用的数据淘汰
        volatile-ttl：从已设置过期时间的数据集中挑选将要过期的数据淘汰
        volatile-random：从已设置过期时间的数据集中任意选择数据淘汰
        allkeys-lru：从全部数据集中挑选最近最少使用的数据淘汰
        allkeys-random：从全部数据集中任意选择数据淘汰no-enviction（驱逐）：禁止驱逐数据

所以,内存满的时候,就看看我们的主动过期机制是什么,淘汰是直接删除,还是写回磁盘
maxmemory 参数设置:
设置redis能够使用的最大内存。当内存满了的时候，如果还接收到set命令，redis将先尝试剔除设置过expire信息的key，
而不管该key的过期时间还没有到达。在删除时，将按照过期时间进行删除，
最早将要被过期的key将最先被删除。如果带有expire信息的key都删光了，
那么将返回错误。这样，redis将不再接收写请求，只接收get请求。
maxmemory的设置比较适合于把redis当作于类似memcached的缓存来使用。

### Redis的事务是真事务么？同一时刻能执行多个事务么？
[http://redisdoc.com/topic/transaction.html](http://redisdoc.com/topic/transaction.html)
不是,事务中有某条/某些命令执行失败了， 事务队列中的其他命令仍然会继续执行,并且没有回滚操作.
不能同时执行多个事务(有项关键的),被 WATCH 的键会被监视，并会发觉这些键是否被改动过了。 如果有至少一个被监视的键在 EXEC 执行之前被修改了， 那么整个事务都会被取消， EXEC 返回空多条批量回复（null multi-bulk reply）来表示事务已经失败。
`乐观锁`

### Redis Server的网络并发模型是什么？实现原理

### Redis 的持久化方式有哪些？实现原理
[http://redisdoc.com/topic/persistence.html](http://redisdoc.com/topic/persistence.html)
- RDB 持久化可以在指定的时间间隔内生成数据集的时间点快照
- AOF 持久化记录服务器执行的所有写操作命令，并在服务器启动时，通过重新执行这些命令来还原数据集。 AOF 文件中的命令全部以 Redis 协议的格式来保存，新命令会被追加到文件的末尾。 Redis 还可以在后台对 AOF 文件进行重写（rewrite），使得 AOF 文件的体积不会超出保存数据集状态所需的实际大小。
- Redis 还可以同时使用 AOF 持久化和 RDB 持久化。 在这种情况下， 当 Redis 重启时， 它会优先使用 AOF 文件来还原数据集， 因为 AOF 文件保存的数据集通常比 RDB 文件所保存的数据集更完整。
- 你甚至可以关闭持久化功能，让数据只在服务器运行时存在。

#### RDB
pros

- RDB 是一个非常紧凑（compact）的文件，它保存了 Redis 在某个时间点上的数据集。 这种文件非常适合用于进行备份： 比如说，你可以在最近的 24 小时内，每小时备份一次 RDB 文件，并且在每个月的每一天，也备份一个 RDB 文件。 这样的话，即使遇上问题，也可以随时将数据集还原到不同的版本。
- RDB 非常适用于灾难恢复（disaster recovery）：它只有一个文件，并且内容都非常紧凑，可以（在加密后）将它传送到别的数据中心，或者亚马逊 S3 中。
- RDB 可以最大化 Redis 的性能：父进程在保存 RDB 文件时唯一要做的就是 fork 出一个子进程，然后这个子进程就会处理接下来的所有保存工作，父进程无须执行任何磁盘 I/O 操作。
- RDB 在恢复大数据集时的速度比 AOF 的恢复速度要快。

cons

- 如果你需要尽量避免在服务器故障时丢失数据，那么 RDB 不适合你。 虽然 Redis 允许你设置不同的保存点（save point）来控制保存 RDB 文件的频率， 但是， 因为RDB 文件需要保存整个数据集的状态， 所以它并不是一个轻松的操作。 因此你可能会至少 5 分钟才保存一次 RDB 文件。 在这种情况下， 一旦发生故障停机， 你就可能会丢失好几分钟的数据。
- 每次保存 RDB 的时候，Redis 都要 fork() 出一个子进程，并由子进程来进行实际的持久化工作。 在数据集比较庞大时， fork() 可能会非常耗时，造成服务器在某某毫秒内停止处理客户端； 如果数据集非常巨大，并且 CPU 时间非常紧张的话，那么这种停止时间甚至可能会长达整整一秒。 虽然 AOF 重写也需要进行 fork() ，但无论 AOF 重写的执行间隔有多长，数据的耐久性都不会有任何损失。


#### AOF
...

### Redis的hash是如何实现的，rehash的策略


# Linux

### select和epoll区别，水平触发和边缘触发的区别
1. 连接数受限 
2. 查找配对速度慢 
3. 数据由内核拷贝到用户态。 

epoll有EPOLLLT和EPOLLET两种触发模式，LT是默认的模式，ET是“高速”模式。LT模式下，只要这个fd还有数据可读，每次 epoll_wait都会返回它的事件，提醒用户程序去操作，而在ET（边缘触发）模式中，它只会提示一次，直到下次再有数据流入之前都不会再提示了，无 论fd中是否还有数据可读。所以在ET模式下，read一个fd的时候一定要把它的buffer读光，也就是说一直读到read的返回值小于请求值，或者 遇到EAGAIN错误。

### 阻塞和非阻塞I/O区别；
[https://www.zhihu.com/question/19732473](https://www.zhihu.com/question/19732473)
在处理 IO 的时候，阻塞,非阻塞,多路复用(包括 select/epoll/poll)都是同步 IO
只有使用了特殊的 API 才是异步 IO(linux AIO, windows IOCP)。

epoll应该是同步的。属于IO多路复用的一种（IO多路复用还有一个名字叫做事件驱动，这个概念和异步的概念有点相似，所以很容易混）

#### 同步与异步
同步和异步关注的是**消息通信机制** (synchronous communication/ asynchronous communication),是针对合作双方而言的
所谓同步，就是在发出一个**调用**时，在没有得到结果之前，该*调用*就不返回。但是一旦调用返回，就得到返回值了。
换句话说，就是由**调用者**主动等待这个**调用**的结果。

而异步则是相反，**调用**在发出之后，这个调用就直接返回了，所以没有返回结果。换句话说，当一个异步过程调用发出后，调用者不会立刻得到结果。而是在**调用**发出后，**被调用者**通过状态、通知来通知调用者，或通过回调函数处理这个调用。

典型的异步编程模型比如Node.js

举个通俗的例子：
你打电话问书店老板有没有《分布式系统》这本书，如果是同步通信机制，书店老板会说，你稍等，”我查一下"，然后开始查啊查，等查好了（可能是5秒，也可能是一天）告诉你结果（返回结果）。
而异步通信机制，书店老板直接告诉你我查一下啊，查好了打电话给你，然后直接挂电话了（不返回结果）。然后查好了，他会主动打电话给你。在这里老板通过“回电”这种方式来回调。

#### 阻塞与非阻塞
阻塞和非阻塞关注的是**程序在等待调用结果（消息，返回值）时的状态**,是正对调用方而言的

阻塞调用是指调用结果返回之前，当前线程会被挂起。调用线程只有在得到结果之后才会返回。
非阻塞调用指在不能立刻得到结果之前，该调用不会阻塞当前线程。

还是上面的例子，
你打电话问书店老板有没有《分布式系统》这本书，你如果是阻塞式调用，你会一直把自己“挂起”，直到得到这本书有没有的结果，如果是非阻塞式调用，你不管老板有没有告诉你，你自己先一边去玩了， 当然你也要偶尔过几分钟check一下老板有没有返回结果。
在这里阻塞与非阻塞与是否同步异步无关。跟老板通过什么方式回答你结果无关。

### 多进程同步方式；
 管道,消息,信号量,共享内存,socket

### linux系统的各类异步机制；

### 如何实现守护进程？

### linux的内存管理机制是什么？

### linux的任务调度机制是什么？

### 系统如何将一个信号通知到进程？

### 什么是死锁？如何避免死锁？

### 共享内存的使用实现原理；

### 多线程和多进程的区别（从cpu调度，上下文切换，数据共享，多核cup利用率，资源占用，等等各方面回答。哪些东西是一个线程私有的？答案中必须包含寄存器）；

### 标准库函数和系统调用的区别？

### cpu 内存 硬盘 等等与系统性能调试相关的命令；

### 设置修改权限;
chmod

### tcp网络状态查看;

### 各进程状态;

### 什么是竞争条件（Race Condition）？用任何一个语言写一个例子。

### 什么是死锁？用代码解释一下。

### netstat tcpdump ipcs ipcrm命令；




# 数据结构

### 排序、查找、二叉树、图；

### 快排的退化

### 哈希和B树各自特点；

### 链表归并排序；

### 大根堆的实现，快排（如何避免最糟糕的状态？），bitmap的运用;

### hash(例如为什么一般hashtable的桶数会取一个素数？如何有效避免hash结果值的碰撞);

### 一个管道可以从a端发送字符到b端，只能发送0-9这10个数字，设计消息的协议，让a可以通知b任意大小的数字，并讨论这种消息协议可能发送的错误的处理能力。 

1. 用8进制，8-9分别代表开始和结束，或者结束编码可以省略(然后就可以用9进制了，但是这个方法比较浪费资源，需要编码解码和更多的传输资源)
2. (0代表开始)(消息总长度)(消息体长度)(消息体)(校验和)【除开头的0，后面遇到0都要补充一个0】

### 只用LIFO栈如何构造一个FIFO队列？只用FIFO队列如何构造一个LIFO栈？

### 使用任何一个语言，写一个REPL，功能是echo你输入的字符串。然后将它演化成一个逆波兰表达式的计算器。





# 网络

### 几层协议(TCP属于传输层，IP属于网络层)
tcp/udp ip

### tcp与udp的区别;
TCP: 

    面向连接
    可靠传输
    效率低
    全双工
    流量控制(滑动窗口)
    拥塞控制(慢启动,拥塞避免)

UDP:

    非连接
    不可靠
    效率高

### udp调用connect有什么作用？
1. 因为UDP可以是一对一，多对一，一对多，或者多对多的通信，所以每次调用sendto()/recvfrom()时都必须指定目标IP和端口号。通过调用connect()建立一个端到端的连接，就可以和TCP一样使用send()/recv()传递数据，而不需要每次都指定目标IP和端口号。但是它和TCP不同的是它没有三次握手的过程。

### 三次握手和四次挥手的理解
- 为什么要三次握手：避免过时的重复连接再次建立时造成的混乱。比如，客户在某个时刻向服务端发起了一个请求，即一个SYN包。该包由于某种原因未能在链接建立超时之前到达服务器，这个时候客户端就会主动放弃链接，并且释放与该链接有关的所有数据结构。需要注意的是，上面的那个SYN虽然没能准时到达，但是它并没有消失，并且能在其生存周期内到达服务器，这个时候服务器就发一个ACK到客户端，客户端收到这个ACK之后找不到相应的数据结构，于是就会发一个RESET给服务端，这个时候服务器就知道这是一个超时的链接。
- 为什么要有四次挥手：假设主动断开链接的客户端（TCP是全双工，服务器主动断开也适合下面讨论）。服务器收到客户端发来的FIN后，不能马上就断开链接，因为他可能还没有把之前收到的数据交给应用程序处理。因此服务器端就需要等一会儿再通知客户端断开链接，这一段等待时间就确保了之前的所有数据都交给应用程序处理了。也正是由于这段等待的时间，使得服务器端需要主动发一个FIN给客户端来告知链接可以断开了。由于在TCP中收到一个一个数据包（不带数据的ACK除外）都需要确认，所以服务器在收到客户端发送的FIN后需要马上发送一个ACK，不然客户端就会认为它发送的FIN丢失了，就会重发。因此，断开比建立多的一个数据包就是服务器为了保证收到的所有数据都已经交给应用程序处理而发出的那个FIN包。
- 在四次挥手的过程中，主动断开链接的一方在收到服务器端发来的FIN之后，要进入一个TIME_WAIT状态，时间为两倍数据在网络中传输的时间（2MSL），之后才会放开与链接相关的所有数据结果。原因有二：首先是主动断开方在收到服务器发送的FIN之后要发送ACK，但是这个ACK有可能会丢失，这个时候服务器就会重新发送一个FIN,如果这个之前已经把数据结构丢失了，自然就无法处理这个FIN。第二个原因是如果直接释放相关数据结构，那么就意味着该IP和端口可以复用来建立一个新的链接了。这个时候就可能有个问题，由于旧的数据包还在网络中传输并且能在生存周期中达到服务器，这个时候服务器就不知道数据包是旧的还是新的。

### tcp连接中时序图，状态图，必须非常非常熟练;

### tcp结束连接怎么握手，time_wait状态是什么,为什么会有time_wait状态？哪一方会有time_wait状态，如何避免?
三次握手,time_wait 是断开连接方在最后一次接受发送 fin 的 ack 之后出现的,用于避免被断开方没能正常接收这个 ack 造成的 fin 重发

不能避免这个状态,只能避免他占用过多资源.
如果是客户端有这个状态,一般可以不用管.
如果是服务端出现这个状态,那么他会占用这个端口,限制这个端口的重新连接,不过我们可以通过socket的选项SO_REUSEADDR来强制进程立即使用处于time_wait状态的连接占用的端口。
通过socksetopt设置后，即使sock处于time_wait状态，与之绑定的socket地址也可以立即被重用。

### tcp头多少字节？哪些字段?(必问)
20字节
源端口\目的端口\序号\确认号\tcp头长度\窗口大小\校验和\可选项

### 什么是滑动窗口?（必问）
简单解释下，发送和接受方都会维护一个数据帧的序列，这个序列被称作窗口。发送方的窗口大小由接受方确定，目的在于控制发送速度，以免接受方的缓存不够大，而导致溢出，同时控制流量也可以避免网络拥塞。

### connect会阻塞，怎么解决?
提示：设置非阻塞，返回之后用select检测状态

### keepalive 是什么东东？如何使用？
TCP是无感知的虚拟连接，中间断开两端不会立刻得到通知。一般在使用长连接的环境下，需要心跳保活机制可以勉强感知其存活。业务层面有心跳机制，TCP协议也提供了心跳保活机制。
一般在 mtqq 之类的协议下使用,默认关闭的

### 列举你所知道的tcp选项，并说明其作用。

### tcp粘包是怎么回事，如何处理？udp有粘包吗？
[http://blog.csdn.net/ce123/article/details/8976006](http://blog.csdn.net/ce123/article/details/8976006)
UDP 没有粘包,因为 UDP 数据包是有边界的

UDP:面向报文的传输方式是应用层交给UDP多长的报文，UDP就照样发送，即一次发送一个报文。因此，应用程序必须选择合适大小的报文。若报文太长，则IP层需要分片，降低效率。若太短，会是IP太小。UDP对应用层交下来的报文，既不合并，也不拆分，而是保留这些报文的边界。这也就是说，应用层交给UDP多长的报文，UDP就照样发送，即一次发送一个报文。

TCP:面向字节流的话，虽然应用程序和TCP的交互是一次一个数据块（大小不等），但TCP把应用程序看成是一连串的无结构的字节流。TCP有一个缓冲，当应用程序传送的数据块太长，TCP就可以把它划分短一些再传送。如果应用程序一次只发送一个字节，TCP也可以等待积累有足够多的字节后再构成报文段发送出去。

下面我们来谈谈TCP和UDP中报文的边界问题。在默认的阻塞模式下，TCP无边界，UDP有边界。

- 对于TCP协议，客户端连续发送数据，只要服务端的这个函数的缓冲区足够大，会一次性接收过来，即客户端是分好几次发过来，是有边界的，而服务端却一次性接收过来，所以证明是无边界的；

-  而对于UDP协议，客户端连续发送数据，即使服务端的这个函数的缓冲区足够大，也只会一次一次的接收，发送多少次接收多少次，即客户端分几次发送过来，服务端就必须按几次接收，从而证明，这种UDP的通讯模式是有边界的。

TCP无边界，造成对采用TCP协议发送的数据进行接收比较麻烦，在接收的时候易出现粘包，即发送方发送的若干包数据到接收方接收时粘成一包。由于TCP是流协议，对于一个socket的包，如发送 10AAAAABBBBB两次，由于网络原因第一次又分成两次发送， 10AAAAAB和BBBB，如果接包的时候先读取10(包长度)再读入后续数据，当接收得快，发送的慢时，就会出现先接收了 10AAAAAB,会解释错误 ,再接到BBBB10AAAAABBBBB，也解释错误的情况。这就是TCP的粘包。

处理粘包:

    在网络传输应用中，通常需要在网络协议之上再自定义一个协议封装一下，简单做法就是在要发送的数据前面再加一个自定义的包头，包头中可以包含数据长度和其它一些信息，接收的时候先收包头，再根据包头中描述的数据长度来接收后面的数据。
    详细做法是：先接收包头，在包头里指定包体长度来接收。设置包头包尾的检查位（ 比如以0xAA开头，0xCC结束来检查一个包是否完整）

避免粘包:

    一、对于发送方引起的粘包现象，用户可通过编程设置来避免，TCP提供了强制数据立即传送的操作指令push，TCP软件收到该操作指令后，就立即将本段数据发送出去，而不必等待发送缓冲区满；
    二对于接收方引起的粘包，则可通过优化程序设计、精简接收进程工作量、提高接收进程优先级等措施，使其及时接收数据，从而尽量避免出现粘包现象；
    三、由接收方控制，将一包数据按结构字段，人为控制分多次接收，然后合并，通过这种手段来避免粘包。

### time_wait是什么情况？出现过多的close_wait可能是什么原因？

### 简单说说https的过程？

1. 浏览器 https 发出请求,包含了自己支持的加密算法
2. 服务器接受请求,并选取一个加密算法和 hash 算法,并将自己的证书发给浏览器
3. 浏览器获得证书,验证其正确性,如果正确,浏览器生成一个随机的密码,并用服务器的公钥加密
    使用约定好的 hash 计算握手信息,并使用生成的随机数对消息进行加密,然后将之前生成的所有信息发送给服务器
4. 服务器接收浏览器发过来的数据,用私钥计算出随机密码,然后用这个随机密码和 hash 算法计算握手信息,并跟浏览器发送过来的对比,查看正确性,然后生成一个随机加密一段握手信息,并发送给浏览器
5. 浏览器用刚刚自己产生的随机密码解密出新的随机密码,并计算握手信息hash,如果跟服务器发过来的一致,那么握手结束.
6. 之后所有的通信都由之前服务器生成的的随机密码用对称加密算法加密

或者这样说

1. c端请求，s端响应并提供证书；
2. c端检查接收后生成pre-master-securet使用s端发过来的公钥加密；
3. s端接收到后使用私钥解密，并最终通过某种算法生成master-securet；
4. 后续的通信中s和c端均使用这个master-securet生成的密钥。

这样c端和s端都可以进行加密解密，所以叫对称加密。
之前c端和s端是非对称加密，即私钥可以解密公钥加密的信息，公钥可以解密私钥加密的信息，但是不能自己解密自己加密的信息。

而两个master-securet的作用是由于不信任机器随机数的随机性，所以使用pre-master-securet，这个东西是c端生成的，而由s端加密生成master-securet，两个机器的随机性会大大增强，不容易被猜出来。


# 海量数据

### 请统计100W个不等长字符串中各字符串的出现次数
建立哈希表，遍历一遍让等长的字符串映射到同一位置，里面可以再哈希链表。有两种情况：一种哈希链表中没出现过就存储该字符串并将对应的计数器设为0，有出现过的就+1。遍历一遍就完成统计。然后遍历哈希链表的计数器输出就行了。

### 设计数据结构可以快速返回0～10亿中哪些数出现了or没出现。
这题和一面的一样，而且更简单，125M的bitmap就够了。

### 一个每秒百万级访问量的互联网服务器，每个访问都有数据计算和I/O操作，如果让你设计，你怎么设计？

### 海量日志数据，提取出某日访问百度次数最多的那个IP

```
   解决思路：因为问题中提到了是海量数据，所以我们想把所有的日志数据读入内存，再去排序，找到出现次数最多的，显然行不通了。这里
   我们假设内存足够，我们可以仅仅只用几行代码，就可以求出最终的结果"""：
   代码如下：
   #python2.7
   from collections import Counter
   if __name__ == '__main__':
      ip_list = read_log()     #读取日志到列表中，这里为了简化，我们用一个小的列表来代替。
      ip_list = ["192.168.1.2"，"192.168.1.3","192.168.1.3","192.168.1.4","192.168.1.2"]
      ip_counter = Counter(ip_list) #使用python内置的计数函数，进行统计
      #print ip_counter.most_common() Out:[('192.168.1.3', 2), ('192.168.1.2', 2), ('192.168.1.4', 1)]
      print ip_counter.most_common()[0][0]    #out:192.168.1.3
   在内存足够的情况下，我们可以看到仅仅使用了5、6行代码就解决了这个问题
   """
   下面才是我们的重点，加入内存有限，不足以装得下所有的日志数据，应该怎么办？
   既然内存都不能装得下所有数据，那么我们后面的使用排序算法都将无从谈起，这里我们采取大而化小的做法。
   假设海量的数据的大小是100G，我们的可用内存是1G.我们可以把数据分成1000份（这里只要大于100都是可以的），每次内存读入100M
   再去处理。但是问题的关键是怎么将这100G数据分成1000分呢。这里我们以前学过的hash函数就派上用场了。
   Hash函数的定义：对于输入的字符串，返回一个固定长度的整数，hash函数的巧妙之处在于对于相同的字符串，那么经过hash计算，
   得出来的结果肯定是相同的，不同的值，经过hash，结果可能相同（这种可能性一般都很小）或者不同。那么有了hash函数，
   那么这道题就豁然开朗了，思路如下：
   1.对于海量数据中的每一个ip，使用hash函数计算hash(ip)%1000,输出到1000个文件中
   2.对于这1000个文件，分别找出出现最多的ip。这里就可以用上面提到的Counter类的most_common()方法了（这里方法很多，不一一列举）
   3.使用外部排序，对找出来的1000个ip在进行排序。（这里数据量小，神马排序方法都行，影响不大）
   代码如下：可以直接运行
   
import os
import heapq
import operator
from collections import Counter
source_file = 'C:/Users/Administrator/Desktop/most_ip/bigdata.txt'  #原始的海量数据ip
temp_files = 'C:/Users/Administrator/Desktop/most_ip/temp/'         #把经过hash映射过后的数据存到相应的文件中
top_1000ip = []                                                     #存放1000个文件的出现频率最高的ip和出现的次数
def hash_file():
    """
     this function is map a query to a new file
    """
    temp_path_list = []
    if not os.path.exists(temp_files):
        os.makedirs(temp_files)
    for i in range(0,1000):
        temp_path_list.append(open(temp_files+str(i)+'.txt',mode='w'))
    with open(source_file) as f:
        for line in f:
            temp_path_list[hash(str(line))%1000].write(line)
            #print hash(line)%1000
            print line
    for i in range(1000):
        temp_path_list[i].close()
def cal_query_frequency():
    for root,dirs,files in os.walk(temp_files):
        for file in files:
            real_path = os.path.join(root,file)
            ip_list = []
            with open(real_path) as f:
                for line in f:
                    ip_list.append(line.replace('\n',''))
            try:
                top_1000ip.append(Counter(ip_list).most_common()[0])
            except:
                pass
    print top_1000ip
def get_ip():
    return (sorted(top_1000ip,key = lambda a:a[1],reverse=True)[0])[0]
if __name__ == '__main__':
   hash_file()
   cal_query_frequency()
   print(get_ip())

```

### 寻找热门查询，300万个查询字符串中统计最热门的10个查询

### 有一个1G大小的一个文件，里面每一行是一个词，词的大小不超过16字节，内存限制大小是1M。返回频数最高的100个词

### 海量数据分布在100台电脑中，想个办法高效统计出这批数据的TOP10

### 有10个文件，每个文件1G，每个文件的每一行存放的都是用户的query，每个文件的query都可能重复。要求你按照query的频度排##序

### 给定a、b两个文件，各存放50亿个url，每个url各占64字节，内存限制是4G，让你找出a、b文件共同的url

```
1.常规的解决办法，也是最容易想到的，就是对于文件A，读入内存，对于文件B中的每一个元素，判断是否在A中出现过。
我们来分析一下这样做的空间和时间复杂度：第一步，读入文件到内存，需要的内存是（50*（10**8）*64）= 320G内存，显然
我们在实际中没有那么大的内存。另外通过遍历A文件和B文件中的每一个元素，需要的时间复杂度是o(M*N)，M,N是两个
文件元素的大小，时间复杂度是（50亿*50亿）。。。。。。这是一个悲伤的算法

2.使用bloom过滤器。关于bloom过滤器，介绍它的文章太多了，稍微有点数学基础，都应该可以明白它的大致意思。
用一句话总结bloom过滤器就是：在需要查找，或者查重的场合，我们使用bloom过滤器能够使我们的搜索时间维持在o(1)的水平，
而不用去考虑文件的规模，另外它的空间复杂度也维持在一个可观的水平，但是它的缺陷是存在误报的情况，具体来说就是，
假如你要验证文件中是否存在某个元素，经过bloom过滤器，告诉你的结果是元素已经存在,那么真实的结果可能元素在文件中并不存在，
但是如果bloom过滤器告诉你的结果是不存在，那么文件中肯定不存在这个元素。下面具体分析问题：

3.使用hash算法，相同的url肯定掉进同一个hash
"""
对于A中50亿个文件，我们使用一个误报率为1%的bloom过滤器，那么经过计算（可以参考bloom的分析过程，里面有结论），每个元素
需要使用9.6bits，总计需要（50*(10**8）*9.6)bits =  6G，在内存的使用上，是符合我们要求的，然后对于使用A文件建立的bloom
过滤器，我们遍历B中的每一个元素，判断是否在A中出现过。
我使用了python的 pybloom模块，帮我们实现了bloom的功能。
代码在python2.7.10下测试通过
只用了9行代码
"""

from pybloom import BloomFilter               #pip install pybloom
bloom_A_file =  BloomFilter(capacity = 5000000000, error_rate=0.01)  #生成一个容量为50亿个元素，错误率为1%的bloom过滤器，
                                                           #这里需要估摸一下自己电脑的可用内存，至少保持电脑的可用内存在8G以上，
                                                           #否则死机不要找我。哈哈
with open(file_A) as f1:                      #遍历A文件中的每一个元素，加入到bloom过滤器中
    for sel in f1:
        bloom_A_file.add(sel)
with open(file_B) as f2:                      #遍历B文件，找出在A文件中出现的元素，并打印出来
    for sel in f2:
        if sel in bloom_A_file:
            print sel                       
```

### 在2.5亿个整数中找出不重复的整数，注，内存不足以容纳这2.5亿个整数

```
首先我们考虑在内存充足的情况下，我们可以使用python中的字典结构。对2.5亿个数中的每一个数，出现一次，字典对应的值+1.
最后遍历字典，找出value为1的所有key。代码很简单，10行都不到。

内存不充足的话，我们可以有两种解决方案。
（1）：假设内存有（2.5*（10**8）*2）/8*(10**9) = 0.06G。那么我们可以使用bit数组，下面我详细解释一下上面内存的计算过程：
因为数据可能存在的方式只有三种：没出现过，出现了一次，出现了很多次。所以我们用2bit表示这三种状态。另外数据有2.5亿条，
总计需要内存2.5亿*2 bit，约等于0.6G。算法的过程大致如下：
"""
1:  初始化一个(2.5*10^8) * 2 bool数组，并且初始化为False，对于每一个整数，使用
    2个bit来表示它出现的次数： 0 0：出现0次 0 1：出现一次 1 1:出现多次
2:  遍历文件，当数据是第一次出现的时候，，更改属于它的两个bit状态：从 00变成01
3： 最后遍历文件找出bit为01的数字，那么这个数字只出现了一次
"""

from collections import defaultdict
import numpy as np
mark =np.zeros((2.5*(10**8),2),dtype=np.bool) #初始化一个(2.5*10^8) * 2 bool数组，并且初始化为False，对于每一个整数，使用
两个bit来表示它出现的次数： 0 0：出现0次 0 1：出现一次 1 1:出现多次
def get_unique_int():
    with open('bigdata') as file:       #bigdata:原始的2.5亿个整数大文件
        for num in file:
            if mark[num][0] == False and mark[num][1] == False:  #这个数第一次出现。那么更改属于它的2个bit
                mark[num][0] = True
                mark[num][1] = False
            else:
                mark[num][0] = True                              #出现了不止一次的数据，那么同意赋值 1 1
                mark[num][1] = True
    with open('bigdata') as file:       #bigdata:原始的2.5亿个整数大文件
        for num in file:
        if mark[num][0] == True and mark[num][1] == False:
            yield num
    
    
if __name__ == '__main__':
    unique_list = get_unique_int()   #返回一个不重复整数的迭代器
```

### 100w个数中找出最大的100个数

```
"""
问题8： 100w个数中找出最大的100个数。时间复杂度尽可能的小
方案1：采用局部淘汰法。选取前100个元素，并排序，记为序列L。然后一次扫描剩余的元素x，与排好序的100个元素中最小的元素比，
       如果比这个最小的要大，那么把这个最小的元素删除，并把x利用插入排序的思想，插入到序列L中。
       依次循环，知道扫描了所有的元素。复杂度为O(100w*100)。
方案2：采用快速排序的思想，每次分割之后只考虑比轴大的一部分，知道比轴大的一部分在比100多的时候，采用传统排序算法排序，
       取前100个。复杂度为O(100w*100)。
方案3：在前面的题中，我们已经提到了，用一个含100个元素的最小堆完成。复杂度为O(100w*lg100)。
"""
代码实现如下：
import heapq    #引入堆模块
import random   #产生随机数
test_list = []  #测试列表
for i in range(1000000):                #产生100w个数，每个数在【0,1000w】之间
    test_list.append(random.random()*100000000)
heapq.nlagest(10,test_list)             #求100w个数最大的10个数
heapq.nsmallest(10,test_list)           #求100w个数最小的10个数
```

### 对于一个文本集合，把相似的单词进行归类。这里这样定义相似单词：两个单词只有一个字母不一样!

```
方法一：对于这个问题，我们最开始使用的是暴力穷举办法。遍历文本中的每个单词，找出在文本中与其相似的单词，
算法的时间复杂度是o(n2),
对于常见的英文词典，差不多有将近20000万个单词，那么需要经过4亿次运算，时间惊人，在实际中不可能行得通。
当然这里还是有一个trick，因为相似单词总是长度一样的，所以你也许可以少许多计算。（当然这不能从根本上改变大局）

方法二： 从相似单词的特点入手。‘son’和‘sun’都可以用正则表达式中的‘s.n’来表示，其中.在正则表达式中可以代表任意的符号
我们使用一个一个字典结构：key是正则字符串 value：是相似单词的集合。举个例子：对于单词'son',那么符合它的正则匹配有
‘.on’,'s.n','so.',那么字典中，分别是：key:'.on',value:'son',key:'s.n',value:'son',key:'so.',value:'son'，对于单词‘sun’,
进行同样的计算，同时字典开始更新：key:'.un',value:'sun',key:'s.n',value:['son','sun'],key:'so.',value:'son'
key:'su.',value:'sun'。这样遍历文本，最后的时间复杂度是o(n):

代码：
from collections import defaultdict  #使用了默认字典
words_dict = defaultdict(set)        #词典的value值默认为set（非重复的相似单词集合，例如‘son’和‘sun’）
def cal_similar_words(word):
    if len(word)!=0:
        for item in word:
            pattern = word.replace(item,'.')
            words_dict[pattern].add(word)
words_list = []    #文本单词集合          
with open(r'D:\programesoftware\NLTK\corpora\abc\science.txt') as file: #为了方便，我们读入一个txt文件，可以认为包含了
     words_list = re.findall(r'\w+',file.read())                        #所有常见的单词
for item in set(words_list):
    cal_similar_words(item.lower())
```

# 编译原理

### 简单编译原理
http://www.ruanyifeng.com/blog/2014/11/compiler.html

### 程序运行时堆栈的作用



# 项目

### 有料道
主要内容: 有料道是一个访谈问答形社区,类似于知乎,知乎是一问多答,这里是多问一答
数据库设计: 概要和主要内容分离,消息设计
redis设计: 将 zset 的 score 拆分成单个位
缓存设计: 单个内容分开缓存

异步的测试，分析过程，不如同步,改进后的异步



# 开放式

### 后来就是聊聊天，自己的技术职业规划，对于新的工作机会更看重什么。

### 一次印象深刻的debug

### 知识体系，学习线路

### 讲一个印象最深的项目

### 最近看过什么书，说说说感受

### 如何让客户端生成token，保证不重复，销毁后可以重复利用(可能？)

### 100个磁盘组成的存储系统，有3个磁盘同时损坏，才会发生数据丢失。如果1个磁盘的损坏率是p，整个存储系统丢失数据的概率是多少
1-((C(100, 98)+C(100, 99)+1)*(1-P))

### 为什么函数式编程重要？什么时候适用函数式语言？

### 如果你需要使用缓存，你使用哪些原则来确定缓存的大小？

### 如何在一个不可靠的协议之上构建一个可靠的通信协议？如何让UDP变得可靠

### 闭包是什么？它有什么用途？闭包和类有什么共同点？

### 什么是高阶函数？有什么用途？用你的首选语言写个例子出来。

### 名字空间(Namespace)有什么用？有什么可以替代它的吗？

### 什么是栈？什么是堆？

### 什么情况下缓存是没用的，甚至是危险的

### RESTful
http://www.ruanyifeng.com/blog/2011/09/restful.html 评论区更精彩
一般说来，uri里面不该有动词，都应该是名词，因为uri代表资源的位置。
原则上对于同一个资源的请求的uri是一样的，不一样的是他的动作，比如对于/topic/1，可以有post，delete，put，get(增删改查)等几种动作
但是现代浏览器或实现的HTTP协议对REST的支持并不完善，所以，通常，我们只以get，post作为动作，把部分动词语义放入到uri中

### QPS计算方式
- QPS = req/sec = 请求数/秒 

单台服务器每天PV计算 :

- 公式1：每天总PV = QPS * 3600 * 6 
- 公式2：每天总PV = QPS * 3600 * 8 

服务器计算 

- 服务器数量 = ceil( 每天总PV / 单台服务器每天总PV ) 

峰值QPS和机器计算公式

原理：每天80%的访问集中在20%的时间里，这20%时间叫做峰值时间 
公式：( 总PV数 * 80% ) / ( 每天秒数 * 20% ) = 峰值时间每秒请求数(QPS) 
机器：峰值时间每秒QPS / 单台机器的QPS = 需要的机器 

问：每天300w PV 的在单台机器上，这台机器需要多少QPS？ 
答：( 3000000 * 0.8 ) / (86400 * 0.2 ) = 139 (QPS) 

问：如果一台机器的QPS是58，需要几台机器来支持？ 
答：139 / 58 = 3 