---
layout: post
title: python的装饰器
description: 如果你还没有经常性的用装饰器, 你就要思考你的工作需求是不是的太简单了, 或者该考虑下这种AOP模式的开发的作用了
category: blog
---

本文译自[stackoverflow](http://stackoverflow.com/questions/739654/how-can-i-make-a-chain-of-function-decorators-in-python/1594484#1594484)

##函数也是对象

为了了解装饰器，我们必须先知道python中的函数也是对象，这非常重要。我们看看下面这个简单的例子

<pre class="prettyprint" style="border: 0">
def shout(word="yes"):
    return word.capitalize()+"!"

print shout()
# outputs : 'Yes!'

# 最为一个对象，你可以将这个函数赋值给任何变量
scream = shout

# 注意我们呢没有用括号：也就是说没有调用这个函数，我们只把函数名『shout』赋值给了scream
# 也就是说，我们能从scream中调用shout
print scream()
# outputs : 'Yes!'

# 不仅如此，我们还可以删除那个旧的名字『shout』
# 此时，我们依然可以通过scream调用原来的函数（因为python的del采用的是引用计数的方式）
del shout
try:
    print shout()
except NameError, e:
    print e
    #outputs: "name 'shout' is not defined"

print scream()
# outputs: 'Yes!'
</pre>

OK!我们先把这个例子放在这儿，待会儿还会用到它

另外一个有趣的特性就是，python的函数可以定义在函数体内部。

<pre class="prettyprint" style="border: 0">
def talk():

    # 我们可以在talk函数内动态的定义函数
    def whisper(word="yes"):
        return word.lower()+"..."

    # 然后直接使用这个定义的函数
    print whisper()

# 你调用talk函数的时候，talk又调用了whisper函数
talk()
# outputs: 
# "yes..."

# 但是whisper函数在talk函数外是不存在的

try:
    print whisper()
except NameError, e:
    print e
    #outputs : "name 'whisper' is not defined"*
    Python's functions are objects
</pre>

##函数引用

前面我们知道函数也是对象，于是就有

- 函数可以被赋值给变量
- 函数可以定义在另一个函数体中

既然是对象，那函数当然也能作为返回值啦

<pre class="prettyprint" style="border: 0">
def getTalk(kind="shout"):

    # 我们先动态的定义两个函数
    def shout(word="yes"):
        return word.capitalize()+"!"

    def whisper(word="yes") :
        return word.lower()+"...";

    # 然后返回其中一个
    if kind == "shout":
        # 我们不用『()』，因为我们并不想调用它，而是要返回函数对象
        return shout  
    else:
        return whisper

# 得到getTalk的返回值，然后赋值给一个变量
talk = getTalk()      

# 我们可以看到，这里的talk是一个函数对象
print talk
#outputs : <function shout at 0xb7ea817c>

print talk()
#outputs : Yes!

# 同理
print getTalk("whisper")()
#outputs : yes...
</pre>

不仅如此，既然都能把函数当成返回值了，那把函数当成参数也是没问题滴

<pre class="prettyprint" style="border: 0">
def doSomethingBefore(func): 
    print "I do something before then I call the function you gave me"
    print func()

doSomethingBefore(scream)
#outputs: 
#I do something before then I call the function you gave me
#Yes!
</pre>

到这里，我们学习了理解装饰器所需的所有预备知识。实际上，装饰器就仅仅是个『包装袋』而已，它可以让你在不改变函数体的情况下，在函数的周围(函数执行前执行后)做文章

##手动模拟装饰器

我们可以这样做

<pre class="prettyprint" style="border: 0">
# 装饰器就是一个以函数作为参数的函数
def my_shiny_new_decorator(a_function_to_decorate):

    # 装饰器的内部定义了一个wrapper函数
    # wrapper函数对原始的被装饰函数做了包装，在它执行的前后加入的语句
    def the_wrapper_around_the_original_function():

        # 这里在原始添加希望在原始函数执行前执行的语句
        print "Before the function runs"

        # 调用原始函数
        a_function_to_decorate()

        # 添加在原始函数执行后执行的代码
        print "After the function runs"

    # 到现在，我们的wrapper函数(也就是the_wrapper_around_the_original_function)依然没有被调用
    # 相反，我们wrapper函数直接返回了
    # wrapper函数里包含了原始函数和执行原始函数之前、之后要执行的代码
    return the_wrapper_around_the_original_function

# 下面，假设我们需要创建一个以后再也不能改动的函数
def a_stand_alone_function():
    print "I am a stand alone function, don't you dare modify me"

a_stand_alone_function() 
#outputs: I am a stand alone function, don't you dare modify me

# 为了给这个不能改动的函数添加功能，我们可以包装它
# 做法很简单，直接把这个函数当成参数传递给装饰器就行了，装饰器会动态的去包装它
a_stand_alone_function_decorated = my_shiny_new_decorator(a_stand_alone_function)
a_stand_alone_function_decorated()
#outputs:
#Before the function runs
#I am a stand alone function, don't you dare modify me
#After the function runs
</pre>

##揭开装饰器的神秘的面纱

对上面的例子，我们用装饰器语法可以这样写

<pre class="prettyprint" style="border: 0">
@my_shiny_new_decorator
def another_stand_alone_function():
    print "Leave me alone"

another_stand_alone_function()  
#outputs:  
#Before the function runs
#Leave me alone
#After the function runs
</pre>

`@`语法糖就等价于

<pre class="prettyprint" style="border: 0">
another_stand_alone_function = my_shiny_new_decorator(another_stand_alone_function)
</pre>

装饰器只是[装饰器模式](http://en.wikipedia.org/wiki/Decorator_pattern)在python中的变种。

当然，我们可以使用多层装饰器

<pre class="prettyprint" style="border: 0">
def bread(func):
    def wrapper():
        print "</''''''\>"
        func()
        print "<\______/>"
    return wrapper

def ingredients(func):
    def wrapper():
        print "#tomatoes#"
        func()
        print "~salad~"
    return wrapper

def sandwich(food="--ham--"):
    print food

sandwich()
#outputs: --ham--
sandwich = bread(ingredients(sandwich))
sandwich()
#outputs:
#</''''''\>
# #tomatoes#
# --ham--
# ~salad~
#<\______/>
</pre>

用装饰器语法糖可以这样写

<pre class="prettyprint" style="border: 0">
@bread
@ingredients
def sandwich(food="--ham--"):
    print food

sandwich()
#outputs:
#</''''''\>
# #tomatoes#
# --ham--
# ~salad~
#<\______/>
</pre>

具体的输出和装饰器的顺序息息相关

<pre class="prettyprint" style="border: 0">
@ingredients
@bread
def strange_sandwich(food="--ham--"):
    print food

strange_sandwich()
#outputs:
##tomatoes#
#</''''''\>
# --ham--
#<\______/>
# ~salad~
</pre>

#装饰器进阶
##被装饰的函数有参数

<pre class="prettyprint" style="border: 0">
def a_decorator_passing_arguments(function_to_decorate):
    def a_wrapper_accepting_arguments(arg1, arg2):
        print "I got args! Look:", arg1, arg2
        function_to_decorate(arg1, arg2)
    return a_wrapper_accepting_arguments

# 在我们调用装饰器返回的的函数的时候，调用的实际是wrapper
# 将参数传给wrapper，wrapper又将参数传给了原始函数

@a_decorator_passing_arguments
def print_full_name(first_name, last_name):
    print "My name is", first_name, last_name

print_full_name("Peter", "Venkman")
# outputs:
#I got args! Look: Peter Venkman
#My name is Peter Venkman
</pre>

便于理解，我们可以看到，在给没有参数的函数用装饰器的时候，实际过程是这样的

<pre class="prettyprint" style="border: 0">
@decorator
def func():
    pass

# 调用函数
func()
# 等价于下面两行
aft = decorator(func)
aft()
</pre>

也就是说`func()`等价于`decorator(func)()`

同理，如果func有参数的时候，调用`func(arg1, arg2)`就等价于`decorator(func)(arg1, arg2)`

##装饰方法

在python中，函数和方法其实是一样的，唯一的不同是：方法有一个self参数。

那么只要将self参数正确地传入了，那方法的装饰器跟函数的装饰器也没什么两样

<pre class="prettyprint" style="border: 0">
def method_friendly_decorator(method_to_decorate):
    def wrapper(self, lie):
        lie = lie - 3 # very friendly, decrease age even more :-)
        return method_to_decorate(self, lie)
    return wrapper


class Lucy(object):

    def __init__(self):
        self.age = 32

    @method_friendly_decorator
    def sayYourAge(self, lie):
        print "I am %s, what did you think?" % (self.age + lie)

l = Lucy()
l.sayYourAge(-3)
#outputs: I am 26, what did you think?
</pre>

更多地情况下，我们使用不定参数`*args, **kwargs`

<pre class="prettyprint" style="border: 0">
def a_decorator_passing_arbitrary_arguments(function_to_decorate):
    # wrapper函数可以接受任何参数
    def a_wrapper_accepting_arbitrary_arguments(*args, **kwargs):
        print "Do I have args?:"
        print args
        print kwargs
        # 然后我们可以再这里解包这两个参数*args,**kwrags
        # 如果不知道怎么解包，那就看看下面这个链接
        # http://www.saltycrane.com/blog/2008/01/how-to-use-args-and-kwargs-in-python/
        function_to_decorate(*args, **kwargs)
    return a_wrapper_accepting_arbitrary_arguments

@a_decorator_passing_arbitrary_arguments
def function_with_no_argument():
    print "Python is cool, no argument here."

function_with_no_argument()
#outputs
#Do I have args?:
#()
#{}
#Python is cool, no argument here.

@a_decorator_passing_arbitrary_arguments
def function_with_arguments(a, b, c):
    print a, b, c

function_with_arguments(1,2,3)
#outputs
#Do I have args?:
#(1, 2, 3)
#{}
#1 2 3 

@a_decorator_passing_arbitrary_arguments
def function_with_named_arguments(a, b, c, platypus="Why not ?"):
    print "Do %s, %s and %s like platypus? %s" %\
    (a, b, c, platypus)

function_with_named_arguments("Bill", "Linus", "Steve", platypus="Indeed!")
#outputs
#Do I have args ? :
#('Bill', 'Linus', 'Steve')
#{'platypus': 'Indeed!'}
#Do Bill, Linus and Steve like platypus? Indeed!

class Mary(object):

    def __init__(self):
        self.age = 31

    @a_decorator_passing_arbitrary_arguments
    def sayYourAge(self, lie=-3): # You can now add a default value
        print "I am %s, what did you think ?" % (self.age + lie)

m = Mary()
m.sayYourAge()
#outputs
# Do I have args?:
#(<__main__.Mary object at 0xb7d303ac>,)
#{}
#I am 28, what did you think?
</pre>


##带参数的装饰器

带参数的装饰器是难点。

首先我们回顾一下上面类似的例子

<pre class="prettyprint" style="border: 0">
# 装饰器就是普通函数
def my_decorator(func):
    print "I am an ordinary function"
    def wrapper():
        print "I am function returned by the decorator"
        func()
    return wrapper

# 所以我们不用@语法也能正常调用

def lazy_function():
    print "zzzzzzzz"

decorated_function = my_decorator(lazy_function)
#outputs: I am an ordinary function

# 然后用装饰器语法也能调用

@my_decorator
def lazy_function():
    print "zzzzzzzz"

#outputs: I am an ordinary function
</pre>

两种调用方式完全一样。第一种方式直接调用了`my_decorator`。而通过`@my_decorator`的方式，我们告诉python，调用函数lazy_function的时候『这个函数被变量my_decorator标记了』
(It’s exactly the same. "my_decorator" is called. So when you @my_decorator, you are telling Python to call the function 'labelled by the variable "my_decorator"'.)

这十分重要，你给的合格「标记」可以直接指向使用的装饰器

<pre class="prettyprint" style="border: 0">
def decorator_maker():

    print "I make decorators! I am executed only once: "+\
          "when you make me create a decorator."

    def my_decorator(func):

        print "I am a decorator! I am executed only when you decorate a function."

        def wrapped():
            print ("I am the wrapper around the decorated function. "
                  "I am called when you call the decorated function. "
                  "As the wrapper, I return the RESULT of the decorated function.")
            return func()

        print "As the decorator, I return the wrapped function."

        return wrapped

    print "As a decorator maker, I return a decorator"
    return my_decorator

# 首先，让我们创建一个装饰器
new_decorator = decorator_maker()       
#outputs:
#I make decorators! I am executed only once: when you make me create a decorator.
#As a decorator maker, I return a decorator

# 然后，我们用创建的装饰器来装饰一个函数

def decorated_function():
    print "I am the decorated function."

decorated_function = new_decorator(decorated_function)
#outputs:
#I am a decorator! I am executed only when you decorate a function.
#As the decorator, I return the wrapped function

# 最后，让我们调用这个函数
decorated_function()
#outputs:
#I am the wrapper around the decorated function. I am called when you call the decorated function.
#As the wrapper, I return the RESULT of the decorated function.
#I am the decorated function.
</pre>

然后，让我们剥去令人厌烦的中间变量在来一次

<pre class="prettyprint" style="border: 0">
def decorated_function():
    print "I am the decorated function."
decorated_function = decorator_maker()(decorated_function)
#outputs:
#I make decorators! I am executed only once: when you make me create a decorator.
#As a decorator maker, I return a decorator
#I am a decorator! I am executed only when you decorate a function.
#As the decorator, I return the wrapped function.

# Finally:
decorated_function()    
#outputs:
#I am the wrapper around the decorated function. I am called when you call the decorated function.
#As the wrapper, I return the RESULT of the decorated function.
#I am the decorated function.
</pre>

语法糖来写一遍

<pre class="prettyprint" style="border: 0">
@decorator_maker()
def decorated_function():
    print "I am the decorated function."
#outputs:
#I make decorators! I am executed only once: when you make me create a decorator.
#As a decorator maker, I return a decorator
#I am a decorator! I am executed only when you decorate a function.
#As the decorator, I return the wrapped function.

#Eventually: 
decorated_function()    
#outputs:
#I am the wrapper around the decorated function. I am called when you call the decorated function.
#As the wrapper, I return the RESULT of the decorated function.
#I am the decorated function.
</pre>

到这里，认真读代码的人应该都理解了。

我们继续来看带参数的装饰器。我们可以用函数动态的生成装饰器，同时，对这个函数，我们是不是也可以传入参数呢！

<pre class="prettyprint" style="border: 0">
def decorator_maker_with_arguments(decorator_arg1, decorator_arg2):

    print "I make decorators! And I accept arguments:", decorator_arg1, decorator_arg2

    def my_decorator(func):
        # The ability to pass arguments here is a gift from closures.
        # If you are not comfortable with closures, you can assume it’s ok,
        # or read: http://stackoverflow.com/questions/13857/can-you-explain-closures-as-they-relate-to-python
        print "I am the decorator. Somehow you passed me arguments:", decorator_arg1, decorator_arg2

        # Don't confuse decorator arguments and function arguments!
        def wrapped(function_arg1, function_arg2) :
            print ("I am the wrapper around the decorated function.\n"
                  "I can access all the variables\n"
                  "\t- from the decorator: {0} {1}\n"
                  "\t- from the function call: {2} {3}\n"
                  "Then I can pass them to the decorated function"
                  .format(decorator_arg1, decorator_arg2,
                          function_arg1, function_arg2))
            return func(function_arg1, function_arg2)

        return wrapped

    return my_decorator

@decorator_maker_with_arguments("Leonard", "Sheldon")
def decorated_function_with_arguments(function_arg1, function_arg2):
    print ("I am the decorated function and only knows about my arguments: {0}"
           " {1}".format(function_arg1, function_arg2))

decorated_function_with_arguments("Rajesh", "Howard")
#outputs:
#I make decorators! And I accept arguments: Leonard Sheldon
#I am the decorator. Somehow you passed me arguments: Leonard Sheldon
#I am the wrapper around the decorated function. 
#I can access all the variables 
#   - from the decorator: Leonard Sheldon 
#   - from the function call: Rajesh Howard 
#Then I can pass them to the decorated function
#I am the decorated function and only knows about my arguments: Rajesh Howard
</pre>
