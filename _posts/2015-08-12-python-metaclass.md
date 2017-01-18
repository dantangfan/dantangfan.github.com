---
layout: post
title: python元类
description: python中的元类
category: blog
---

本文译自[stackoverflow](http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python)

<!-- more -->


## 类也是对象

在学习元类之前，让我们先来看看什么是python类。在大多数语言中，类是只是一个能产生`对象`的代码段，这对python来说也是没问题的

```
>>> class ObjectCreator(object):
...       pass
... 

>>> my_object = ObjectCreator()
>>> print(my_object)
<__main__.ObjectCreator object at 0x8974f2c>
```

但是，在python中，类不仅仅是能产生对象的工具，类本身也是对象。

一旦你使用了`class`关键字，python就会为它生成一个对象。如下指令

```
>>> class ObjectCreator(object):
...       pass
... 
```

就在内存中产生了一个名叫 **ObjectCreator** 的对象。

**之所以我们把这个对象(上面这个class)叫做类，是因为它本身就可以产生对象(他自己的实例)。**

但说到底，它还是一个对象，也就是说你可以：

- 把它赋值给一个变量
- 复制它
- 给他增加属性
- 把它当成函数参数

e.g.

```
>>> print(ObjectCreator) # 由于类也是一个对象，你可以打印一个类
<class '__main__.ObjectCreator'>
>>> def echo(o):
...       print(o)
... 
>>> echo(ObjectCreator) # 可以把类当成函数参数
<class '__main__.ObjectCreator'>
>>> print(hasattr(ObjectCreator, 'new_attribute'))
False
>>> ObjectCreator.new_attribute = 'foo' # 可以为类增加属性
>>> print(hasattr(ObjectCreator, 'new_attribute'))
True
>>> print(ObjectCreator.new_attribute)
foo
>>> ObjectCreatorMirror = ObjectCreator # 可以把类赋值给变量
>>> print(ObjectCreatorMirror.new_attribute)
foo
>>> print(ObjectCreatorMirror())
<__main__.ObjectCreator object at 0x8997b4c>
```


## 动态创建类

因为类也是对象，所以我们就可以像使用对象一样，在运行时创建它。

首先，我们可以再函数中用class关键字来创建一个类

```
>>> def choose_class(name):
...     if name == 'foo':
...         class Foo(object):
...             pass
...         return Foo # 返回一个类，而不是一个实例
...     else:
...         class Bar(object):
...             pass
...         return Bar
...     
>>> MyClass = choose_class('foo') 
>>> print(MyClass) # the 函数返回了一个类，而不是一个实例
<class '__main__.Foo'>
>>> print(MyClass()) # 我们可以用合格类来创建对象
<__main__.Foo object at 0x89c6d4c>
```

但是这看起来还不是那么动态，毕竟，我们还是需要自己书写整个类.

类也是对象，那么他们一定可以又某种东西生成。

当使用class关键字时，python自动的为你创建了这个对象。但就跟python中其他事物一样，python也提供了手动控制类的方法。

还记得`type`函数吗？就是那个你用来判断对象是神马类型的函数（下面例子只有在新式类，也就是继承object的类中才有效）

```
>>> print(type(1))
<type 'int'>
>>> print(type("1"))
<type 'str'>
>>> print(type(ObjectCreator))
<type 'type'>
>>> print(type(ObjectCreator()))
<class '__main__.ObjectCreator'>
```

然而，type还有一个跟上述完全不同的行为，就是在运行时动态的创建类。type可以用类的描述作为参数，然后返回一个类！就像下面这样

```
type(name of the class, 
     tuple of the parent class (for inheritance, can be empty), 
     dictionary containing attributes names and values)
```

e.g.

```
>>> class MyShinyClass(object):
...       pass
```

可以被这样创建

```
>>> MyShinyClass = type('MyShinyClass', (), {}) # 返回一个类对象
>>> print(MyShinyClass)
<class '__main__.MyShinyClass'>
>>> print(MyShinyClass()) # 用该类生成一个实例对象
<__main__.MyShinyClass object at 0x8997cec>
```

上面，我们用 **MyShinyClass** 作为类名字，也用它作为type的参数。当然，他们本身是可以不同的，但是这样就会造成不必要的误解.

`tpye` 用一个字典来接收类属性，所以

```
>>> class Foo(object):
...       bar = True
```

也可以被写成

```
>>> Foo = type('Foo', (), {'bar':True})
```

然后就能像正常类那样使用它

```
>>> print(Foo)
<class '__main__.Foo'>
>>> print(Foo.bar)
True
>>> f = Foo()
>>> print(f)
<__main__.Foo object at 0x8a9b84c>
>>> print(f.bar)
True
```

当然，我们也可以继承这个类

```
>>>   class FooChild(Foo):
...         pass
```

也可以写成

```
>>> FooChild = type('FooChild', (Foo,), {})
>>> print(FooChild)
<class '__main__.FooChild'>
>>> print(FooChild.bar) # bar is inherited from Foo
True
```

最后，你肯定想为你的类增加方法。没问题，直接定义这些方法，然后绑定到类属性上就行了 

```
>>> def echo_bar(self):
...       print(self.bar)
... 
>>> FooChild = type('FooChild', (Foo,), {'echo_bar': echo_bar})
>>> hasattr(Foo, 'echo_bar')
False
>>> hasattr(FooChild, 'echo_bar')
True
>>> my_foo = FooChild()
>>> my_foo.echo_bar()
True
```

现在我们知道了：类也是对象，我们可以在运行时动态的创建类。

在你使用class关键字的时候python就是这样做的，python是利用`元类`(metaclass)来实现的.(This is what Python does when you use the keyword class, and it does so by using a metaclass.)

## 什么是元类(metaclass)

元类是用来创建类的，我们定义类就是为了创建对象，但是我们知道类本身也是对象，元类就是用来创建类这些对象的，它们是类的类，你可以形象化地理解为:

```
MyClass = MetaClass()
MyObject = MyClass()
```

我们知道type可以这样使用

```
MyClass = type('MyClass', (), {})
```

这是因为`type`实际上就是一个`metaclass`，python利用type这个元类来创建所有类。

我们可以检查一下对象的`__class__`属性，来看看他们的类是谁。

python中一切皆对象，一切就是所有！包括int,str,function,object,class等等，他们都可以用类来创建

```
>>> age = 35
>>> age.__class__
<type 'int'>
>>> name = 'bob'
>>> name.__class__
<type 'str'>
>>> def foo():pass
...
>>> foo.__class__
<type 'function'>
>>> class Bar(object): pass
...
>>> b = Bar()
>>> b.__class__
<class '__main__.Bar'>
>>>
```

那么`__class__`的`__class__`又是谁呢

```
>>> age.__class__.__class__
<type 'type'>
>>> name.__class__.__class__
<type 'type'>
>>> foo.__class__.__class__
<type 'type'>
>>> b.__class__.__class__
<type 'type'>
```

由此可见，元类就是用来创建类的。如果你喜欢，你可以把它叫做『类工厂』

`type`是python内建的元类，当然，如果你愿意，也可以自己创建元类

## __metaclass__属性

可以在类中加入`__metaclass__`属性

```
class Foo(object):
  __metaclass__ = something...
  [...]
```

如果你这样做了，python就会用你定义的元类来创建Foo这个类。

但是！里面有很多坑！面有很多坑！有很多坑！很多坑！多坑！坑！！

我们最先写下了 **class Foo(object)** ，但是这个时候Foo对象还没有在内存中创建。

python会在类定义中寻找`__metaclass__`，一旦找到了，就会用它来创建Foo的类对象，如果没找到，就会用type来创建。

当写下

```
class Foo(Bar):
    pass
```

的时候，python会这样做

1. 有__metaclass__定义吗？
2. 如果有，在内存中建立一个名字为Foo的类对象。用__metaclass__指定的类来创建。
3. 如果没有，那python就会一直查找__metaclass__到 MODULE level(就是整个模块的级别，也就是有可能有全局的__metaclass__)，然后操作 
4. 如果在Foo中没有找到这个属性，它会继续在父类 Bar（第一个父类）中找，Bar的__metaclass__可以是默认的type
5. 这样一直向父类找，父类的父类。。。直到 module 级别的才停止。

**注意** __metaclass__属性是不能被继承的！！如果Bar在创建的时候使用了自己定义的__metaclass__比如`type()`（这不是默认的type().__new__()），它的子类不会继承这个属性。

那我们应该把什么放进__metaclass__中呢？当然就是能创建类的东西咯

那什么能创建类呢？`type`或者它的子类，或者使用它的类

## 普通元类

设计元类的主要目的就是允许我们在类创建的时候动态的修改它。这经常用在API的设计上，这些API需要动态创建符合上下文的类。

我举一个很愚钝的例子，比如我们希望所有类的属性都以大写字母命名，可以有很多办法来实现这个需求，但是这里我们使用元类。

元类可以是任何可调用对象，也就是说，元类可以使类，也可以是函数。

所以，我们从一个函数开始

```
# the metaclass will automatically get passed the same argument
# that you usually pass to `type`
# 元类也需要那些传给type的参数
def upper_attr(future_class_name, future_class_parents, future_class_attr):
  """
    Return a class object, with the list of its attribute turned 
    into uppercase.
  """

  # pick up any attribute that doesn't start with '__' and uppercase it
  uppercase_attr = {}
  for name, val in future_class_attr.items():
      if not name.startswith('__'):
          uppercase_attr[name.upper()] = val
      else:
          uppercase_attr[name] = val

  # let `type` do the class creation
  return type(future_class_name, future_class_parents, uppercase_attr)

__metaclass__ = upper_attr # this will affect all classes in the module

class Foo(): 
  # global __metaclass__ won't work with "object" though，
  # 注意，全局的__metaclass__并不会对继承object的类起作用，因为object的元类是type
  # but we can define __metaclass__ here instead to affect only this class
  # and this will work with "object" children
  bar = 'bip'

print(hasattr(Foo, 'bar'))
# Out: False
print(hasattr(Foo, 'BAR'))
# Out: True

f = Foo()
print(f.BAR)
# Out: 'bip'
```

下面让我们用class来实现元类

```
# remember that `type` is actually a class like `str` and `int`
# so you can inherit from it
class UpperAttrMetaclass(type): 
    # __new__ 是在 __init__ 之前就调用的函数
    # __new__函数用来创建并返回这个类对象
    # __init__ 只是用传给他的参数来初始化这个对象
    # 我们很少使用到__new__， 只有当我们希望控制类对象的初始化等少数情况时才使用它
    # 这里被初始化的对象是这个类, 并且我们想让它变得更一般化，因此我们重写了__new__
    # 有些更高级的用法涉及到__call__，但这里我们不用
    def __new__(upperattr_metaclass, future_class_name, 
                future_class_parents, future_class_attr):

        uppercase_attr = {}
        for name, val in future_class_attr.items():
            if not name.startswith('__'):
                uppercase_attr[name.upper()] = val
            else:
                uppercase_attr[name] = val

        return type(future_class_name, future_class_parents, uppercase_attr)

```

这个方法不是很OOP，我们直接调用了type()，在把type当成父类的情况下，我们应该这样做`type.__new__()`，如下

```
class UpperAttrMetaclass(type): 

    def __new__(upperattr_metaclass, future_class_name, 
                future_class_parents, future_class_attr):

        uppercase_attr = {}
        for name, val in future_class_attr.items():
            if not name.startswith('__'):
                uppercase_attr[name.upper()] = val
            else:
                uppercase_attr[name] = val

        # reuse the type.__new__ method
        # this is basic OOP, nothing magic in there
        return type.__new__(upperattr_metaclass, future_class_name, 
                            future_class_parents, uppercase_attr)
```

我们注意到这里有一个参数并没有使用`upperattr_metaclass`，但这并没有什么特别的：一个类的方法总是把自己的instance当成第一个参数，就跟self一样。

为了清晰，这里的参数名都很长，实际上我会这样写

```
class UpperAttrMetaclass(type): 

    def __new__(cls, clsname, bases, dct):

        uppercase_attr = {}
        for name, val in dct.items():
            if not name.startswith('__'):
                uppercase_attr[name.upper()] = val
            else:
                uppercase_attr[name] = val

        return type.__new__(cls, clsname, bases, uppercase_attr)
```

可以使用`super`让这个例子变得更简洁

```
class UpperAttrMetaclass(type): 

    def __new__(cls, clsname, bases, dct):

        uppercase_attr = {}
        for name, val in dct.items():
            if not name.startswith('__'):
                uppercase_attr[name.upper()] = val
            else:
                uppercase_attr[name] = val

        return super(UpperAttrMetaclass, cls).__new__(cls, clsname, bases, uppercase_attr)
```

这就是有关元类的所有类容了！够简单吧！

使用元类写代码会很多坑，并不是因为元类本身，而是以为这些操作往往需要跟内省，继承之类的机制结合

实际上，元类确实很时候用来发明黑魔法，这样才造成了它的复杂。但它本身的概念是很简单的

- 拦截类创建
- 编辑类
- 返回编辑后的类

## 为什么该使用类而不是函数来作为元类？

- 意思更清晰
- 可以使用OOP。元类可以继承，重载父类函数，元类甚至也可以使用元类
- 可以更好的组织代码
- 可以用__call__,__init__,__new__等多种内省来实现。毕竟，有些人就是喜欢用__init__不喜欢用__new__

## 什么时候才需要使用元类呢

 **元类是比99%的magic更deep的特性，99%的用户根本不用考虑。一旦你在考虑是否需要使用元类，那就意味着你不需要使用元类**

一般式用来创建API，比如jDango的ORM，允许这样定义

```
class Person(models.Model):
  name = models.CharField(max_length=30)
  age = models.IntegerField()
```

但是这样使用的时候

```
guy = Person(name='bob', age='35')
print(guy.age)
```

并不会返回`IntegerField`，而是返回一个int，并且可以直接和数据库打交道。

之所以能这样做，是因为Model实现了__metaclass__

## 最后再说两句

首先，我们知道类是一个可以产生自身实例的对象，实际上，类就是他们自己的实例。

python中一切皆对象，他们不是class的实例，就是metaclass的实例。

除了`type`。。。。

type是自己的metaclass，它不是能用纯python冲新创建的，是在python的实现里面创建.

其次，能不用元类就不要用元类，我们可以用其他很多方法来改变类的行为，比如

- 装饰器
- monkey patching
