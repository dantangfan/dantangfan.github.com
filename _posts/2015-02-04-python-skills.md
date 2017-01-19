---
layout: post
title: python小技巧
description: <持续更新> 平时使用python的时候总结出来的一些小技巧
category: blog
---

>  <持续更新> 平时使用python的时候总结出来的一些小技巧，不算常用的 python 特性

<!-- more -->

#### 1. 比较大小

```python
>>> x = 5
>>> 1 < x < 10
True
>>> 10 < x < 20 
False
>>> x < 10 < x*10 < 100
True
>>> 10 > x <= 9
True
>>> 5 == x > 4
True
```

#### 2. 枚举对象

```python
>>> a = ['a', 'b', 'c', 'd', 'e']
>>> for index, item in enumerate(a): print index, item
...
0 a
1 b
2 c
3 d
4 e
>>>
```

枚举对象还可以接收一个参数，代表其实值

```
>>> l = ["spam", "ham", "eggs"]
>>> list(enumerate(l))
>>> [(0, "spam"), (1, "ham"), (2, "eggs")]
>>> list(enumerate(l, 1))
>>> [(1, "spam"), (2, "ham"), (3, "eggs")]
```

#### 3. 注意你的默认参数

```python
>>> def foo(x=[]):
...     x.append(1)
...     print x
... 
>>> foo()
[1]
>>> foo()
[1, 1]
>>> foo()
[1, 1, 1]
```

并没有达到我们的预期值，而是每次都在上一个x后面append了一个数。
因为python参数并不是我们在C/C++等语言中所见的申明+赋值的形式，而是采用了创建+指向的类似于指针的方式实现，也就是说python的变量实际上是
对值或者对象的一个指针，比如下面代码

```python
>>> p=1
>>> id(p)
140680863166744
>>> p=p+1
>>> id(p)
140680863166720
```

对于C/C++等传统语言，P的地址是不应该发生变化的，而是直接改变当前地址的值；在python代码中，实际是创建了一个整数1对象，然后用p指向它，
当执行加法操作时，又创建了一个2对象，并用p指向它，整个过程中，改变的是p的地址。

一句话解释这个函数参数默认陷阱：`Python’s default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby).
This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.`

可见，函数的默认参数在定义的时候就已经被绑定了。
而对于foo函数中的默认参数`x=[]`，我们看如下代码

```python
>>> a=[1]
>>> a.append(1)
>>> id(a)
4302841976
>>> a.append(1)
>>> id(a)
4302841976
```

可以知道，修改列表类型的对象，是直接修改变量指向的地址，而不同于纯整数对象，因此就出现了上述陷阱，不知道算不算设计上的bug。

因此，不要使用可变对象作为函数的默认参数。如下

```python
>>> def foo(x=None):
...     x= [] if x is None
...     x.append(1)
...     print x
>>> foo()
[1]
>>> foo()
[1]
```

#### 4. 切片规则

```python
a = [1,2,3,4,5]
>>> a[::2]  # 跳两步
[1,3,5]
>>> a[::-1] # 反着跳
[5,4,3,2,1]
```

#### 5. for的else语法

```python
for i in foo:
    if i == 0:
        break
else:
    print("i was never 0")
```

如果for循环执行完之后还没有执行break语句，那么就会执行else语句

#### 6. 打包参数

我们知道函数调用时 **def func(\*args, \*\*kwargs)** ， \*args代表将传入的参数放入一个`元组`如 **func(1,2,3)** , \*\*kwargs代表将参数放入一个`字典`中，
如 **func(a=1,b=2,c=3)**

与此同时，对于一个函数`def func(x, y)`，同样可以将参数打包成arg, kwargs的形式，如 args=(1,3,5), kwargs={'x':1, 'y':3},
调用的时候使用 **func(\*args, \*\*kwargs)**

#### 7. with statement，上下文管理器

我们知道可以使用with语法来处理文件，这样在使用完成之后能默认关闭文件，如下

```python
with open('a.txt', 'r') as f:
    do something
```

原理是with关键字调用了对象的`__enter__`和`__exit__`函数，也就是说，我们可以对实现了这两个魔术方法的任何对象使用with关键字。

- enter:进入上下文管理器的运行时上下文，在语句体执行前调用。with 语句将该方法的返回值赋值给 as 子句中的 target，如果指定了 as 子句的话
- exit:退出与上下文管理器相关的运行时上下文，返回一个布尔值表示是否对发生的异常进行处理。参数表示引起退出操作的异常，如果退出时没有发生异常，则3个参数都为None。如果发生异常，返回True 表示不处理异常，否则会在退出该方法后重新抛出异常以由 with 语句之外的代码逻辑进行处理。如果该方法内部产生异常，则会取代由 statement-body 中语句产生的异常。要处理异常时，不要显示重新抛出异常，即不能重新抛出通过参数传递进来的异常，只需要将返回值设置为 False 就可以了。之后，上下文管理代码会检测是否 __exit__() 失败来处理异常

```python
class DemoContextManger(object):
    def __init__(self, name):
        self.name = name
        print "Context manager name:" + self.name
    
    def __enter__(self):
        print "enter context manager and return the object"
        return self
    
    def __exit__(self, exc_type, exc_value, ext_tb):
        print "free resource"
        if exc_type is None:
            print "Nothing run, exit without exception"
        else:
            print "error:" + exc_value
            return False  # 返回false表示要外部代码来处理异常

with DemoContextManger("text") as t:
    pass
```

一个db的context manager例子

```python
class DBConnection():
    ...
    def cursor(self):
        """return a cursor and start a new transaction"""
    def commit(self):
        """commit the current transaction"""
    def rollback(self):
        """rollback a transaction"""
    def __enter__(self):
        # start a new transaction
        return self.cursor()
    def __exit__(self, type, value, tb):
        if tb is None:
            self.commit()
        else:
            self.rollback()
with DBConnection() cursor:
    cursor.execute("...")
    cursor.execute("...")
```

python也提供了一个简单模块contextlib来辅助实现上下文管理器

```python
from contextlib import contextmanager
import time
import sys

@contextmanager
def timeit(msg):
    start = time.time()
    yield
    print sys.stderr, msg, 'took %0.3f secs' % (time.time() - start)

with timeit('myfunc'):
    myfunc()
```

yield之前的语句等同于enter，之后的语句等同于exit，yield就是当前with之后的语句，如果有yield 值，那么这个值就是enter的返回值

#### 8. try-catch-else

我们常见的错误处理方法如下

```python
try:
    do something here
exec Exception, e:
    do something here
```

我们可以为语句加上else语句，用于处理没有任何错误发生

```python
try:
    do something here
exec Exception, e:
    do something here
else:
    do something here
finally:
    close xxx
```

#### 9. 巧用set操作

```python
>>> a = set([1,2,3,4])
>>> b = set([3,4,5,6])
>>> a | b # 并集
{1, 2, 3, 4, 5, 6}
>>> a & b # 交集
{3, 4}
>>> a < b # 是否为子集
False
>>> a - b # 差集
{1, 2}
>>> a ^ b # 亦或
{1, 2, 5, 6}
```

### 10. 字典操作

```
>>> dict((["a", 1], ["b", 2])) # ⽤两个序列类型构造字典
{'a': 1, 'b': 2}

>>> dict(zip("ab", range(2)))
{'a': 0, 'b': 1}

>>> dict(map(None, "abc", range(2)))
{'a': 0, 'c': None, 'b': 1}

>>> d = {"a":1, "b":2}
>>> d.setdefault("a", 100) # key 存在,直接返回 value
1
>>> d.setdefault("c", 200) # key 不存在,先设置,后返回
200
>>> d
{'a': 1, 'c': 200, 'b': 2}
```

在collection中，还有一个`defaultdict`用于为字典添加默认类型，指定字典默认值。

### 11. pow函数

我们熟知的pow函数可以用做求次方比如

    pow(12, 34) # 表示12的34次方，当然，也可以用小数或者负数

还有一种用法

    pow(12, 34, 56) # 表示12的34次方对56求余数
    
### 12. partial函数

```
>>> from functools import partial
>>> bound_func = partial(range, 0, 10)
>>> bound_func()
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> bound_func(2)
[0, 2, 4, 6, 8]
```

尽管这很常见，但是这在实际工作中十分有用。可以为函数绑定任意多个默认参数

### 13. round函数

python的round函数可以根据需求保留浮点数的精确数位

```
>>> print round(1123.456789, 4)
1123.4568
 >>> print round(1123.456789, 2)
1123.46
 >>> print round(1123.456789, 0)
1123.0
 >>> print round(1123.456789, -1)
1120.0
 >>> print round(1123.456789, -2)
1100.0
```

### 14. 深拷贝和浅拷贝

我们在实际开发中都可以向对某列表的对象做修改,但是可能不希望改动原来的列表. 浅拷贝只拷贝父对象，深拷贝还会拷贝对象的内部的子对象

```
list1 = [1, 2, 3]
list2 = list1  # 就是个引用, 你操作list2,其实list1的结果也会变，跟c语言传地址一样
list3 = list1[:]
import copy
list4 = copy.copy(list1)  # list3和list4都是对整个list1对象的复制，操作他们不会改变list1的值
list2[0] = 5
list3[1] = 10
list4[2] = 15
# 此时的list1=[5, 2, 3]
```

### 15. 检查列表中的每个元素

```python 
numbers = [10,100,1000,10000]
if [number for numeber in numbers if number<10000]:
    print "at list one small than 10000"
```

可以使用

```python 
numbers = [10,100,1000,10000]
if any(number < 10000 for number in numbers):
    print "at list one small than 10000"
```
类似的

```python 
numbers = [10,100,1000,10000]
if all(number < 10000 for number in numbers):
	print "all small than 10000"
```

### 16. filter函数

相对于map、reduce而言，filter使用量相对要少些，就像他的名字一样，filter的作用就是按照规则过滤一些元素

```
lst = [1, 2, 3, 4, 5, 6]
# 所有奇数都会返回True, 偶数会返回False被过滤掉
print filter(lambda x: x % 2 != 0, lst)
#输出结果
[1, 3, 5]
```

### 17. print

在python2.7之后，`>>`操作符被重载了，可以这样使用print

```
print >> sys.stderr, "message"
print >> file("test.txt", 'w'), "message"
```

第一个参数需要是一个文件对象

### 18.快速把一个序列按照n个元素生成一组

```
seq = range(10)
zip(*[iter(seq)]*3)
```

### 19.一行筛选质数

```python
filter(lambda x: all(map(lambda p: x % p != 0, range(2, x))), range(2, n))
```

### 20.在某个路径下打开http服务器

```python
python -m SimpleHTTPServer 8000
```

这样就能在浏览器上面展示当前目录下地文件了，可以用于代替ftp

### 21.简单计算器

```python
print input()
```

函数会打印出输入的值，比如输入2\*\*3，输出8，支持括号等

### 22.八皇后问题

```python
_=[__import__('sys').stdout.write("\n".join('.' * i + 'Q' + '.' * (8-i-1) for i in vec) + "\n===\n") for vec in __import__('itertools').permutations(xrange(8)) if 8 == len(set(vec[i]+i for i in xrange(8))) == len(set(vec[i]-i for i in xrange(8)))]
```

### 23.命令行执行python

```bash
>> python -c 'print 1'
```

### 24.一行求三个数的最值和平均值

```bash
>>> [f(n) for f, n in zip((max, min, lambda s: float(sum(s))/len(s)), ([list(map(int, map(raw_input, ':::')))]*3))]
```

### 25.在shell中执行，可以快速格式化json数据

```bash
cat file.json | python -m json.tool
```

### 26.一行实现树

[来自](https://gist.github.com/hrldcpr/2012250)

```python
from collections import defaultdict
def tree(): return defaultdict(tree)
```

对，就是这样，你没看错。。简单地来说，一颗树就是一个默认值是其子树的字典。

#### 举个例子，json风格

现在我们可以创建一个 JSON 风格的嵌套字典，我们不需要显式地创建子字典——当我们需要时，它们神奇地自动出现了：

```python
users = tree()
users['harold']['username'] = 'hrldcpr'
users['handler']['username'] = 'matthandlersux'
```

我们可以将这些用 print(json.dumps(users)) 以 JSON 的形式输出，于是我们得到：

```python
{"harold": {"username": "hrldcpr"}, "handler": {"username": "matthandlersux"}}
```

#### 不需要赋值

我们甚至可以不需要任何赋值就可以创建整个树结构：

```python
taxonomy = tree()
taxonomy['Animalia']['Chordata']['Mammalia']['Carnivora']['Felidae']['Felis']['cat']
taxonomy['Animalia']['Chordata']['Mammalia']['Carnivora']['Felidae']['Panthera']['lion']
taxonomy['Animalia']['Chordata']['Mammalia']['Carnivora']['Canidae']['Canis']['dog']
taxonomy['Animalia']['Chordata']['Mammalia']['Carnivora']['Canidae']['Canis']['coyote']
taxonomy['Plantae']['Solanales']['Solanaceae']['Solanum']['tomato']
taxonomy['Plantae']['Solanales']['Solanaceae']['Solanum']['potato']
taxonomy['Plantae']['Solanales']['Convolvulaceae']['Ipomoea']['sweet potato']
```

我们接下来将漂亮地输出他们，不过需要先将他们转换为标准的字典：

```python
def dicts(t): return {k: dicts(t[k]) for k in t}
```

现在我们用 pprint(dicts(taxonomy)) 来漂亮地输出结构：

```python
{'Animalia': {'Chordata': {'Mammalia': {'Carnivora': {'Canidae': {'Canis': {'coyote': {},
                                                                            'dog': {}}},
                                                      'Felidae': {'Felis': {'cat': {}},
                                                                  'Panthera': {'lion': {}}}}}}},
 'Plantae': {'Solanales': {'Convolvulaceae': {'Ipomoea': {'sweet potato': {}}},
                           'Solanaceae': {'Solanum': {'potato': {},
                                                      'tomato': {}}}}}}
```

#### 迭代

这棵树可以很欢乐地被迭代处理，同样因为只要简单地引用一个结构它就会出现。

举例来说，假设我们想要解析一个新动物的列表，将它们加入我们上面的 taxonomy，我们只要这样调用一个函数：

```python
add(taxonomy,
    'Animalia,Chordata,Mammalia,Cetacea,Balaenopteridae,Balaenoptera,blue whale'.split(','))
```

我们可以简单地这样实现它：

```python
def add(t, keys):
  for key in keys:
    t = t[key]
```

再一次，我们完全没有对字典使用任何赋值，仅仅是引用了这些键，我们便创建了我们新的结构：

```python
{'Animalia': {'Chordata': {'Mammalia': {'Carnivora': {'Canidae': {'Canis': {'coyote': {},
                                                                            'dog': {}}},
                                                      'Felidae': {'Felis': {'cat': {}},
                                                                  'Panthera': {'lion': {}}}},
                                        'Cetacea': {'Balaenopteridae': {'Balaenoptera': {'blue whale': {}}}}}}},
 'Plantae': {'Solanales': {'Convolvulaceae': {'Ipomoea': {'sweet potato': {}}},
                           'Solanaceae': {'Solanum': {'potato': {},
                                                      'tomato': {}}}}}}
```

### 27.CSV 转 json

```bash
python -c "import csv,json;print json.dumps(list(csv.reader(open('csv_file.csv'))))"
```

### 28.脚本性能分析

```bash
python -m cProfile my_script.py
```

### 29.列表 flatten

```python
a = [[1, 3], 4, [4, 5, 6, [7, 8]]]
print(list(itertools.chain.from_iterable(a)))
```

### 30.集合的所有子集

```python
f = lambda x: [[y for j, y in enumerate(set(x)) if (i >> j) & 1] for i in range(2**len(set(x)))]
f([10,9,1,10,9,1,1,1,10,9,7])
```

### 30.打印 unicode 字符

```bash
python -c "print unichr(234)"
```

### 31.压缩 CSS 代码

```bash
python -c 'import re,sys;print re.sub("\s*([{};,:])\s*", "\\1", re.sub("/\*.*?\*/", "", re.sub("\s+", " ", sys.stdin.read())))'
```
