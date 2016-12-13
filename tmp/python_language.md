python中各种对象的实现 http://www.2cto.com/kf/201110/108607.html

1. dict使用hash实现 http://blog.csdn.net/digimon/article/details/7875789
2. list/tuple 数组指针，可变数组 http://www.jianshu.com/p/J4U6rR


redis中基础数据结构

简单动态字符串，双端链表，字典（hash实现），跳表，压缩表

string: 数字用整数，其他用动态字符串
hash：首先用压缩表实现，超过512或者64字节用字典实现
list: 压缩表，双端列表
set：先用压缩表，后用字典
zset：先用压缩表实现，后用调表实现

自己实现list，可以用python实现一个链表来实现list

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        
class List:
    def __init__(self):
        self.head = None
        self.length = 0
       
    def insert(self, index, value):
        pass
        
    def remove(self, index):
        pass
        
    def find(self, index):
        pass
        return Node
    
    def __setitem__(self, index, value):
        pass
        
    def __getitem__(self, index):
        pass
        
        
        
自己实现一个字典，可以用hash

class Node:
    def __init(self, key, value):
        self.next = None
        self.hash = xx