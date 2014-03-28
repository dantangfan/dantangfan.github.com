---
layout: post
title: c语言编程内存管理(未完成)
description: One large difference between C and other programming languages is that in C, you have to handle memory yourself rather than having a garage collector do it for you.
category: blog
---
* 本文翻译自[nethack4.org/blog/memory.html](http://www.nethack4.org/blog/memory.html)
* 作者：Alex Smith

C语言和其他语言最大的不同就是你必须要手动管理内存，而不像其他语言那样有垃圾回收器来帮你管理内存。要保证内存在某种特定的情况下被正确分配并不困难（并且有些操作几乎在所有语言中都需要手动完成）；困难的是要保证分配的内存足够大并且不再使用的时候能够回收。

这里例举出几种可以应用在C语言的内存分配技术。其中很多都已被应用于NetHack 3.4.3；NetHack 4中应用得更广泛。我将在这篇博客中为大家分享这些方法的有点和缺点。在此，我最关心的是程序的正确性，而不是效率，因此，在性能差距不是特别大的情况下，我将尽量使用整洁的代码而不是高效的代码。

## 分配固定大小内存的技术

在这里我们关心两个问题：跟踪分配的内存的使用寿命，并且确保他们的大小是正确的。因此，我将从查看在编译时已经知道大小的内存开始，然后再转向可以处理未知大小内存的技术。

### 在栈中固定大小的缓冲区

在C语言中分配内存最简单的方法大概要数直接使用堆栈分配了。如果一个变量在函数内声明的时候没有指定成`static`或者`extern`，那么当这个变量的作用域启动的时候，系统将为他分配足够的内存，当作用域结束的时候，系统将释放刚刚分配的内存（有时候这个变量被称为“自动变量”）。因为在c语言中，作用域是良好嵌套的，一个典型的c语言实现将会用堆栈实现这一点：变量将从栈顶分配新的空间，并且在作用域结束的时候释放栈顶空间。（这里说的栈顶并离堆栈内存真正的顶部很远，因为栈是从高地址向低地址衍生的）

这里是这么做主要优点（和一些小缺点）：

* 它不需要额外的操作或者状态来实现这个操作。很多时候，内存分配计划本身就需要内存来工作，这反而导致了效率的倒退。栈分配内存经常就是用来提供这些内存。

* 