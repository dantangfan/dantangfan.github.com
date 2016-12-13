只看懂这么多，还有mix-in技术，等着一起完善
---

在子类中调用父类函数时，我们经常使用`super`函数，但是你知道他是怎么工作的吗？你知道怎样使用它才是最靠谱的吗？网络上许多介绍super的文章都不太靠谱，所以作者才写了这篇文章来让同学们更好的理解super。

首先，我们看下面一个最简单的例子

```
class LoggingDict(dict):
    def __setitem__(self, key, value):
        logging.info('Settingto %r' % (key, value))
        super().__setitem__(key, value)
```

这个class在功能上跟他的父类dict完全一样，不同点是它重写了__setitem__方法，并为其加入了log功能，使得在每次有元素更新的时候就会记录一行log。

在super函数还没被推广之前，对于上面例子调用父类方法的时候，我们必须显示的调用`dict.__setitem__(self, key, value)`，而super函数只是间接的引用了原始函数。

间接调用让我们在冬天修改一个了类的父类的时候，不用去管调用处（比如用另一个类替换了父类），super函数会自动处理。

这种动态的调用依赖于类本身和它所继承的父类（ancestors tree）。首先，super函数的调用位置是由本函数的代码决定的，比如上例中就在LoggingDict.__setitem__中；其次，就是它的可变性（我们可以创建多个父类的子类）

比如下面，让我们把这个类应用到下面类中

```
class LoggingOD(LoggingDict, collections.OrderedDict):
    pass
```

这个类的原型树如下: LoggingOD, LoggingDict, OrderedDict, dict, object。这里有一个关键点 **OrderedDict被放到了LoggingDict和dict之间，这就使得LoggingDict.__setitem__更新时所使用的super调用了OrderedDict中的__setitem__而不是dict中的！**

先搞清楚这个问题，我们并没有修改LoggingDict类的代码，我们仅仅建了一个新的子类，这个子类的逻辑就是把两个已经存在的类的组件结合起来，并开工至它的查找顺序（原型树的顺序）

### 查找顺序

刚刚被我们成为查找顺序或者原型树的的东西，用官方语言来说就是条件规约顺序(Method Resolution Order or MRO)，通过类的`__mro__`属性，我们可以看到一个类的MRO：

```
>>> pprint(LoggingOD.__mro__)
(<class '__main__.LoggingOD'>,
 <class '__main__.LoggingDict'>,
 <class 'collections.OrderedDict'>,
 <class 'dict'>,
 <class 'object'>)
```

我们的目标是创建一个子类，这个子类的MRO有我们所期望的顺序，所以我们想要了解MRO是怎么计算的。其实原理十分简单，这个序列包含了类本身，类的父类，父类的父类...一直到object类（新式类最终继承object类）。如此的顺序，让父类始终出现在子类之后，如果有一个类有多个父类，那么这些父类的顺序就跟他们作为父类参数调用时一样。

上面例子中的MRO的顺序遵循了以下几个规则

> LoggingOD出现在他的父类LoggingDict,OrderedDict之前
> LoggingDict出现在OrderedDict之前，因为调用顺序就这样
> LoggingDict和OrderedDict都出现在dict之前
> dict出现在object之前

虽然有很多长篇大论来介绍这个搜索顺序的原理，但是，如果我们只想知道如何创建所需的子类，我们只需要记住以下两点

1. 子类在父类之前
2. 多个父类遵循他们本身的调用顺序

### 实践建议

super函数用于调用原型链中某个类的方法，它需要遵循以下几个规定

1. 被super调用的方法必须存在
    通常，我们不能保证被调用的方法一定存在。于是，我们会构造一个root类，包含所有的被super调用的方法，root类继承了object，这样，将它放在原型链的倒数第二，就可以确保super一定能调用成功，并且可以知道是否是所需的方法
    
    ```
    class Root:
    def draw(self):
        # the delegation chain stops here
        assert not hasattr(super(), 'draw')

    class Shape(Root):
        def __init__(self, shapename, **kwds):
            self.shapename = shapename
            super().__init__(**kwds)
        def draw(self):
            print('Drawing.  Setting shape to:', self.shapename)
            super().draw()

    class ColoredShape(Shape):
        def __init__(self, color, **kwds):
            self.color = color
            super().__init__(**kwds)
        def draw(self):
            print('Drawing.  Setting color to:', self.color)
            super().draw()

    cs = ColoredShape(color='blue', shapename='square')
    cs.draw()
    ```

2. 调用者和被调用者的参数序列必须一样。
    由于我们不一定知道被调用的函数的参数序列是怎样的，在知道参数的时候，我们通常直接传参，不知道参数的时候，通常我们用**kwargs来传参

### 