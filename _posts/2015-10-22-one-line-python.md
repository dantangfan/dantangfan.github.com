---
layout: post
title: 一行 python 代码能实现的功能
description: python 是如此的强大，我们来看看一行 python 能做哪些有趣的事情
category: opinion
---

### 一行筛选质数

```python
filter(lambda x: all(map(lambda p: x % p != 0, range(2, x))), range(2, n))
```

### 对两个等长字符串的亦或操作

```python
"".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])
```

### 在某个路径下打开http服务器

```python
python -m SimpleHTTPServer 8000
```

这样就能在浏览器上面展示当前目录下地文件了，可以用于代替ftp


### 简单计算器

```python
print input()
```

函数会打印出输入的值，比如输入2\*\*3，输出8，支持括号等

### 有一个这样的库，可以把你所有python实现，包裹到一行当中

https://github.com/csvoss/oneliner

几乎直接转变成了scheme

### 八皇后问题

```python
_=[__import__('sys').stdout.write("\n".join('.' * i + 'Q' + '.' * (8-i-1) for i in vec) + "\n===\n") for vec in __import__('itertools').permutations(xrange(8)) if 8 == len(set(vec[i]+i for i in xrange(8))) == len(set(vec[i]-i for i in xrange(8)))]
```

### 命令行执行python

```bash
>> python -c 'print 1'
```

### 一行求三个数的最值和平均值

```bash
>>> [f(n) for f, n in zip((max, min, lambda s: float(sum(s))/len(s)), ([list(map(int, map(raw_input, ':::')))]*3))]
```

### 打开浏览器，展示python给你看

```python
import antigravity
```

### 在shell中执行，可以快速格式化json数据

```bash
cat file.json | python -m json.tool
```

### 一行实现树

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

### CSV 转 json

```bash
python -c "import csv,json;print json.dumps(list(csv.reader(open('csv_file.csv'))))"
```

### 脚本性能分析

```bash
python -m cProfile my_script.py
```

### 列表 flatten

```python
a = [[1, 3], 4, [4, 5, 6, [7, 8]]]
print(list(itertools.chain.from_iterable(a)))
```

### 集合的所有子集

```python
f = lambda x: [[y for j, y in enumerate(set(x)) if (i >> j) & 1] for i in range(2**len(set(x)))]
f([10,9,1,10,9,1,1,1,10,9,7])
```

### 打印 unicode 字符

```bash
python -c "print unichr(234)"
```

### 压缩 CSS 代码

```bash
python -c 'import re,sys;print re.sub("\s*([{};,:])\s*", "\\1", re.sub("/\*.*?\*/", "", re.sub("\s+", " ", sys.stdin.read())))'
```
