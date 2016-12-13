---
layout: post
title: 如何正确地区分和使用python中的static、class、abstract method
description: python 类中的几种类型的方法各有各的用途，一般情况下我们不会很严格的区分，但知道各个类型的作用确是很有必要的
category: opinion
---

##python中的方法是怎么工作的

method是被当做类属性的function，它介于function和class之间。我们可以像下面这样声明和获取一个方法

```
>>> class Pizza(object):
...     def __init__(self, size):
...         self.size = size
...     def get_size(self):
...         return self.size
...
>>> Pizza.get_size
<unbound method Pizza.get_size>
```

从上面这个例子可以看出，`get_size`是一个未绑定（unbound）的方法，下面解释什么这是什么意思

```
>>> Pizza.get_size()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unbound method get_size() must be called with Pizza instance as first argument (got nothing instead)
```

从上面我们可以知道：之所以不能这样调用get_size方法，是因为他还没有被绑定到一个Pizza的实例上面。

未绑定的方法必须使用一个Pizza实例作为第一个参数来调用(python2中需要这个类的实例，python3中随便什么都可以)。那我们来试试

```
>>> Pizza.get_size(Pizza(42))
42
```

这样就能工作了，此时，我们把这个类的实例当成了该方法的第一个参数。但是，我们平时都不这么写，因为这不仅复杂，而且有时候我们不一定知道那个作为参数的实例到底是什么类的实例。

因此，python是这样做的：把所有Pizza的方法都绑定到Pizza的实例上！也就是说，get_size是一个Pizza实例的绑定方法，而 **被绑定的方法的第一个参数就是绑定它的实例本身**

```
>>> Pizza(42).get_size
<bound method Pizza.get_size of <__main__.Pizza object at 0x7f3138827910>>
>>> Pizza(42).get_size()
42
```

正如预期，我们不需要显示的将Pizza实例传给被绑定的方法，它的`self`参数自动的关联到了实例本身上。下面这个例子更能说明这个问题

```
>>> m = Pizza(42).get_size
>>> m()
42
```

在python3中，附属于类的函数不在被认为是未绑定的方法，它们被看成了普通的函数，只在有必要的时候才会被绑定。但是对于实例对象来说，跟python2还是一样的

```
>>> class Pizza(object):
...     def __init__(self, size):
...         self.size = size
...     def get_size(self):
...         return self.size
...
>>> Pizza.get_size
<function Pizza.get_size at 0x7f307f984dd0>
```

### static method
静态方法是方法中的特例，有时候，我们希望有一个属于类的方法，但是这个方法又没有涉及到类实例

```
class Pizza(object):
    @staticmethod
    def mix_ingredients(x, y):
        return x + y
 
    def cook(self):
        return self.mix_ingredients(self.cheese, self.vegetables)
```

就像上面这个例子，我们也可以写成那种带有self参数的方法，但是self参数永远都不会被使用。

@staticmethod装饰器给我们带来了以下几个便利

- python可以不用把每个未绑定方法都绑定到实例上面，因为绑定实例也是对象（python中一切皆对象），因此创建它们也是有开销的。静态方法避免了这种开销

```
>>> Pizza().cook is Pizza().cook
False
>>> Pizza().mix_ingredients is Pizza.mix_ingredients
True
>>> Pizza().mix_ingredients is Pizza().mix_ingredients
True
```

- 增强了代码可读性，一旦我们看到了这个装饰器，我们就应该知道这个方法适合类实例本省没有关系的

- 我们可以重载这个方法。尽管这个方法是和类无关的，但如果单独隔离出来当成一个函数，那所有的子类都必须使用这个函数而不能重写他，可喜的是，如果我们当成静态方法，子类就可以自由的改动。

我们一般在这些情况下使用静态方法

### class method

类方法就是直接绑定到类本身的方法，而不是绑定到类实例上面。

```
>>> class Pizza(object):
...     radius = 42
...     @classmethod
...     def get_radius(cls):
...         return cls.radius
... 
>>> 
>>> Pizza.get_radius
<bound method type.get_radius of <class '__main__.Pizza'>>
>>> Pizza().get_radius
<bound method type.get_radius of <class '__main__.Pizza'>>
>>> Pizza.get_radius is Pizza().get_radius
True
>>> Pizza.get_radius()
42
```

不管你怎么调用这个方法，他始终是绑定在它的类上面的。

类方法对以下两种方法很有用

- 工场方法，不用显示调用类名称，使得子类可以使用这个方法创建属于自己的实例

```
class Pizza(object):
    def __init__(self, ingredients):
        self.ingredients = ingredients
 
    @classmethod
    def from_fridge(cls, fridge):
        return cls(fridge.get_cheese() + fridge.get_vegetables())
```

- 静态方法调用静态方法的时候使用类方法，这样就避免了每次都显示的调用类名称

```
class Pizza(object):
    def __init__(self, radius, height):
        self.radius = radius
        self.height = height
 
    @staticmethod
    def compute_area(radius):
         return math.pi * (radius ** 2)
 
    @classmethod
    def compute_volume(cls, height, radius):
         return height * cls.compute_area(radius)
 
    def get_volume(self):
        return self.compute_volume(self.height, self.radius)
```

###abstract method

虚方法(虚函数)定义在基类中但没有被实现

```
class Pizza(object):
    def get_radius(self):
        raise NotImplementedError
```

子类都应该实现所有父类的虚方法，不然调用的时候会报错，也只有在调用的时候才会报错

```
>>> Pizza()
<__main__.Pizza object at 0x7fb747353d90>
>>> Pizza().get_radius()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 3, in get_radius
NotImplementedError
```

这里有个办法能让初始化一个实例的时候就报虚方法没有实现的错误

```
import abc
 
class BasePizza(object):
    __metaclass__  = abc.ABCMeta
 
    @abc.abstractmethod
    def get_radius(self):
         """Method that should do something."""
```

abc是内置模块，这是再实例化base类的时候就会报错了

```
>>> BasePizza()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: Can't instantiate abstract class BasePizza with abstract methods get_radius
```
