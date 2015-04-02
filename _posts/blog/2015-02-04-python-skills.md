---
layout: post
title: python小技巧
description: 平时使用python的时候总结出来的一些小技巧
category: blog
---

#### 迭代一个列表

```python
string=['a','b','c']
for index in range(len(string)):
    print index, string[index]
```

可以使用

```python
string=['a','b','c']
for index, item in enumerate(string):
    pring index, item
```

#### 检查列表中的每个元素

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

## 函数

#### 默认值只被计算一次

在python中，函数的默认值是在函数定义的时候实例化的，而不是在函数调用的时候！所以会出现下面结果

```python 
def func(item, stuff=[]):
	stuff.append(item)
	print stuff
func(1)
#print "[1]"
func(2)
#print "[1,2]"
```

```python
def foo(number=[]):
	number.append(9)
	print number
foo()
#[9]
foo([1,2])
#[1,2,9]
foo()
#[9]
foo()
#[9,9]
foo()
#[9,9,9]
```

我们需要理解的是，调用函数的时候，这个默认值会被赋成不同值是因为每次在给函数指定一个默认值的时候，python都会储存这个值。如果在调用函数的时候重写了默认值，那么这个储存的值就不会被使用。当你不重写默认值的时候，python就会让默认值引用储存的值（例子中的number）。它并不是将存储的值拷贝来为这个变量赋值，可以这样理解：有两个变量，一个是内部的，一个是当前运行时的变量。现实就是我们有两个变量来用相同的值进行交互，所以一旦number发生变化，也会改变python里面保存的初始记录。

但是问题不是我们想想那么简单的，比如下面

```python
def foo(count=0):
	count+=1
	print count
foo()
#1
foo()
#1 
```

为什么上面函数运行的时候又是符合预期的呢？原因很简单，整形是一种不可变的类型，跟list不同，在函数的执行过程中，整形变量是不能被改变的。当我们执行count+=1的时候，我们并没有改变count的值，而是将count指向了新的地址；而在前面使用list的时候，我们是直接在当前地址操作了变量。

需要记住的有两个点：

> 在python中，函数的默认值是在函数定义的时候实例化的，而不是在函数调用的时候！

> 默认值会发生改变，是因为我们直接操作的默认值的地址。