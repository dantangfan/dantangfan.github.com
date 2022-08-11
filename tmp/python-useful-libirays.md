## imp
## jsonschema
## cpython
## copy
## traceback
## gc
## contextlib
## collections
## __future__
## uuid
## base64
## hashlib
## Crypto
## struct
## array
## functools
## inspect
inspect模块提供了一系列函数用于帮助使用自省。  
  
检查对象类型  
is{module|class|function|method|builtin}(obj): 检查对象是否为模块、类、函数、方法、内建函数或方法。  
isroutine(obj): 用于检查对象是否为函数、方法、内建函数或方法等等可调用类型。  
  
获取对象信息  
getmembers(object[, predicate]): 这个方法是dir()的扩展版，它会将dir()找到的名字对应的属性一并返回。  
getmodule(object): 它返回object的定义所在的模块对象。  
get{file|sourcefile}(object): 获取object的定义所在的模块的文件名|源代码文件名（如果没有则返回None）。  
get{source|sourcelines}(object): 获取object的定义的源代码，以字符串|字符串列表返回。  
getargspec(func): 仅用于方法，获取方法声明的参数，返回元组，分别是(普通参数名的列表, *参数名, **参数名, 默认值元组)。

## locale
## decimal
<<<<<<< HEAD
## dis
## Queue
## deque
=======
## itertools
## operator

## smtplib 邮件
## pxssh ssh 链接

## six


>>>>>>> u
