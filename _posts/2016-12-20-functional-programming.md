---
layout: post
title: Elixir 和函数式编程
description: 函数式编程
category: blog
---

题目虽然是函数式编程，但是这里并不会介绍函数式编程，Google 一下，全世界都是函数式编程的入门文章。

说起函数式编程的时候，大多数人都知道 Erlang/Haskell/Lisp 是函数式编程语言，并且常见的命令式编程语言如 C/Java/Python 也支持一些函数式的特性。但是，到底什么是函数式编程呢？

<!-- more -->
跟面向对象编程一样，函数式编程只是一些列的思想，也就是如何撸代码的方法论，而不是一套严苛的规定。它的思想源自于 [阿隆佐·邱奇](http://zh.wikipedia.org/zh/%E9%98%BF%E9%9A%86%E4%BD%90%C2%B7%E9%82%B1%E5%A5%87) 的 [lambda演算](http://zh.wikipedia.org/wiki/%CE%9B%E6%BC%94%E7%AE%97)，与之对应的是 [艾伦·图灵](http://zh.wikipedia.org/zh/%E8%89%BE%E4%BC%A6%C2%B7%E5%9B%BE%E7%81%B5) 发明的 [图灵机](http://zh.wikipedia.org/zh/%E5%9B%BE%E7%81%B5%E6%9C%BA)，他们实际上是基友，只是阿隆佐运气没那么好，我们所使用的计算机都是 [冯·诺伊曼设计架构](http://zh.wikipedia.org/zh/%E5%86%AF%C2%B7%E8%AF%BA%E4%BC%8A%E6%9B%BC%E7%BB%93%E6%9E%84)。一直到 Lisp 语言的发明，函数式编程才慢慢的被世人认可。

### 变量不变
跟面向对象所谓的一切皆对象相对应，函数式编程有个一切皆表达式的说法。函数是由更小的函数组成的，函数的参数是函数，函数的返回值也是函数。

Erlang 在这方面就十分严格的遵循了变量不变这一教条，但实际来看，这也带来了不少麻烦。比如一个作用域里的一个名字只能指向一个特定值/地址。比如说要实现斐波那契数列，python 可以这样写

```python
def fib(n):
    if n == 1 or n == 2:
        return 1
    a, b = 1, 1
    for i in range(3, n+1):
        a, b = b, a+b
    return b
```

使用 Erlang 就只能使用尾递归实现，很少写 Erlang 也不知道是否写对了

```erl
fib(1) -> 1;
fib(2) -> 1;
fib(N) -> fib_compute(1, 2, 3, N).

fib_compute(A, B, N, N) -> B;
fib_compute(A, B, I, N) when I < N -> fib_compute(B, A+B, I+1, N).
```

但是千万别写成了这样

```erl
fib(1) -> 1;
fib(2) -> 1;
fib(N) -> fib(N-1) + fib(N-2).
```

这样的递归从形式上来看，就知道会消耗大量的栈空间，Erlang 编译器应该不会聪明到这种递归都为你优化好。

但是 Elixir 突破了这层障碍，它的变量是可变的。于是，我们的斐波那契数列也可以写成和 python 类似

```elixir
def fib(1), do: 1
def fib(2), do: 1
def fib(n) do
  Enum.reduce(3..n+1, {1, 1}, fn _x, {a, b} -> {b, a+b} end)
  |> elem(1)
end
```

这里我们没有使用 for 循环，是因为函数式编程的每个表达式/函数都会返回一个值。而 for 循环作用域中的 a/b 改变，并不会影响到作用域之外的 a/b，也就是说，如果在 for 循环中写了 `{a, b} = {b, a+b}`，每次循环结束之后并不会影响到 for 之外初始化的 a/b，它们的值永远不变。

### 模式匹配
模式匹配本身也不是函数式编程的固有特征，不过加入这个特性，可以让代码简洁很多，省去了一大部分 if-else/switch 之类的分支判断。原理其实也很简单，运用模式匹配的函数，在运行时，编译器会对传入的参数和函数定义的参数进行比较，并选择最为接近的那个。

比如对普通函数的一个多层if语句

```python
def func(a, b, c, d):
    if a == 0:
        if b == 1 and c == 2:
            return d
    else:
        return a
    return None
```

换成 Elixir 的模式匹配之后，会变成这样

```elixir
def func(0, 1, 1, d), do: d
def func(0, _, _, _), do: nil
def func(a, _, _, _), do: a
```

后者明显比前者更加清晰易懂，不过需要注意的是，函数定义的顺序一定要对，模式匹配是从上往下一个一个来的。

### 管道操作
以前只在 linux 中见识过管道，概念简单但却威力惊人。管道使得代码的易读性大大增高，曾经的一层一层的函数包裹，只需要简单 `|>` 即可实现参数传递

### 惰性求值
惰性求值是函数式的一个基本特征。一般情况下，我们再写代码的时候并不关心编译器会如何执行、何时执行我们的语句。指令式编程语言的所有代码都是顺序执行的，这让我们很容易调试比如说一些 print 语句就可以打印出当前上下文的一些信息。可喜的是，大多数函数式在执行的时候也是顺序执行的，我也不知道编译器是如何优化成顺序执行的。但是既然是函数式编程语言，惰性求值自然也不能少。

比如，我们会熟练的使用 Enum 枚举类型

```elixir
Enum.map(1..n, fn x -> x*x end)
|> Enum.filter(fn x -> rem(x, 2) end)
|> Enum.sum
```

在 n 不是很大的时候并不会有任何问题，但在 n 十分大的时候(比如 1000,000,000) 这里就会生成两个 十分大的列表，因为函数是即时执行的，每个管道都会生成一堆中间变量，造成了大量的内存消耗。

Elixir 提供了流 Stream 类型来实现惰性求值，可以将上面写成

```elixir
Strea.map(1..n, fn x -> x*x end)
|> Stream.filter(fn x -> rem(x, 2) end)
|> Enum.sum
```

只有在最后碰到 Enum.sum 的时候，前面才会进行求值。

### 闭包
实际上，大多数编程语言都会不自觉的提到闭包，似乎闭包已经是现代编程语言一项不可缺少的特性。同样，Elixir 也支持闭包，并且是真正的闭包，对作用域外的变量无副作用，也就是仅仅包含指向数据的指针。比如

```elixir
>> a = 5
>> f = fn x -> x+a end
>> f.(10)
15
>> a = 100
>> f.(10)
15
```

可以看到，闭包只捕获了在他之前存在的变量 a 的值，之后 a 改变，但是并没有影响到函数 f 中的 a。由此可见，f 中的 a 已经是一个独立于外部 a 的单独的内存区域(fh在 heap 中）。这一特性，实际上就是变量不变的特性，全局的 a 值发生了变化，仅仅是因为它指向的地址发生了变化而已。所以，并不是说它不修改外部数据，而是它根本没办法修改。

相较与其他语言中的闭包，也不能说哪个更好，比如 Python 的装饰器，可以为我们实现强大的函数缓存

```python
def deco(func):
    instence = {}
    def wrap(*args, **kwargs):
        if func.__name__ in instence:
            instence[func.__name__] += 1
        else
            instence[func.__name__] += 1
        func(*args, **kwargs)
```

### 宏
这才是最令人兴奋的地方，为元编程提供了极大的便利。Python 也提供源编程，并且也有提供访问 AST 的库，比如 ast 和 [pythoscope](http://pythoscope.org)，但好像作用并不是很大，因为是解释型语言并且已经有了各种好用的语法糖。虽然还有如 `__metaclass__` 等更高级的特性来实现元编程，可是在实际生产中却鲜有使用，除非要写一个 ORM 库之类的，少用的另一个原因是难学，要理解 Python 元变成的概念都要花大把时间。

Elixir 完全破解了这种魔咒，在 [元编程](http://dantangfan.github.io/2016/10/10/metaprogramming-elixir-cn.html) 里，我们可以轻轻松松的实现各种奇葩的功能，甚至是直接编写自己的 DSL。后面我想尝试用简单易懂的方法来实现一个 mongodb 的 orm 库，并跟 python 实现相比较，感受一下是否能甩几条街。

### 不爽的地方
#### 作为参数的函数的调用
在把函数当成参数之后，被调用的函数需要在后面加个`.`号，略感奇葩。比如

```elixir
def call(func) do
  func.()
end
```

原因很简单，Elixir 的函数调用 `func` 和 `func()` 是等价的。把函数当成参数的时候，实际上是传的函数的定义/地址，后面加个点号告诉了编译器这样转换之后才是函数本身。

在 1.5 版本之后，函数调用不加括号会报 warning，看来消除加点号的操作还是指日可待的。

#### 严格的格式要求

比如说对一个以 atom 为 key 的 map 里面，`%{a: 1, b: 2}` 冒号后面必须有空格，不然就会报错。虽然 Python 也很奇葩的用缩进来表示代码块，但至少还是说得过去。这个冒号必须要空格就不知道是为什么了，难道是因为 Erlang 的函数调用的形式是 `erlang:some_func` ？

### 参考文档
- [Functional Programming For The Rest of Us](http://www.defmacro.org/ramblings/fp.html)，[译文](https://github.com/justinyhuang/Functional-Programming-For-The-Rest-of-Us-Cn/blob/master/FunctionalProgrammingForTheRestOfUs.cn.md)


### 后记

最近又看到了 [这篇文章](http://blog.plataformatec.com.br/2016/05/beyond-functional-programming-with-elixir-and-erlang/)，是 Elixir 作者写的。开篇就点明：函数式不是 Erlang VM 的目标(goal)，而是达到目标的手段(end)

```
I would like to add a slightly different perspective to functional programming in the Erlang VM: functional programming is not a goal in the Erlang VM. It is a means to an end.
```
