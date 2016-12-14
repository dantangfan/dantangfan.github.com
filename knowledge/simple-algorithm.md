# 数据结构

### 排序、查找、二叉树、图；

### 快排的退化

### 哈希和B树各自特点；

### 链表归并排序；

### 大根堆的实现，快排（如何避免最糟糕的状态？），bitmap的运用;

### hash(例如为什么一般hashtable的桶数会取一个素数？如何有效避免hash结果值的碰撞);

### 一个管道可以从a端发送字符到b端，只能发送0-9这10个数字，设计消息的协议，让a可以通知b任意大小的数字，并讨论这种消息协议可能发送的错误的处理能力。 

1. 用8进制，8-9分别代表开始和结束，或者结束编码可以省略(然后就可以用9进制了，但是这个方法比较浪费资源，需要编码解码和更多的传输资源)
2. (0代表开始)(消息总长度)(消息体长度)(消息体)(校验和)【除开头的0，后面遇到0都要补充一个0】

### 只用LIFO栈如何构造一个FIFO队列？只用FIFO队列如何构造一个LIFO栈？

### 使用任何一个语言，写一个REPL，功能是echo你输入的字符串。然后将它演化成一个逆波兰表达式的计算器。

# 海量数据

### 请统计100W个不等长字符串中各字符串的出现次数
建立哈希表，遍历一遍让等长的字符串映射到同一位置，里面可以再哈希链表。有两种情况：一种哈希链表中没出现过就存储该字符串并将对应的计数器设为0，有出现过的就+1。遍历一遍就完成统计。然后遍历哈希链表的计数器输出就行了。

### 设计数据结构可以快速返回0～10亿中哪些数出现了or没出现。
这题和一面的一样，而且更简单，125M的bitmap就够了。

### 一个每秒百万级访问量的互联网服务器，每个访问都有数据计算和I/O操作，如果让你设计，你怎么设计？

### 海量日志数据，提取出某日访问百度次数最多的那个IP

```
   解决思路：因为问题中提到了是海量数据，所以我们想把所有的日志数据读入内存，再去排序，找到出现次数最多的，显然行不通了。这里
   我们假设内存足够，我们可以仅仅只用几行代码，就可以求出最终的结果"""：
   代码如下：
   #python2.7
   from collections import Counter
   if __name__ == '__main__':
      ip_list = read_log()     #读取日志到列表中，这里为了简化，我们用一个小的列表来代替。
      ip_list = ["192.168.1.2"，"192.168.1.3","192.168.1.3","192.168.1.4","192.168.1.2"]
      ip_counter = Counter(ip_list) #使用python内置的计数函数，进行统计
      #print ip_counter.most_common() Out:[('192.168.1.3', 2), ('192.168.1.2', 2), ('192.168.1.4', 1)]
      print ip_counter.most_common()[0][0]    #out:192.168.1.3
   在内存足够的情况下，我们可以看到仅仅使用了5、6行代码就解决了这个问题
   """
   下面才是我们的重点，加入内存有限，不足以装得下所有的日志数据，应该怎么办？
   既然内存都不能装得下所有数据，那么我们后面的使用排序算法都将无从谈起，这里我们采取大而化小的做法。
   假设海量的数据的大小是100G，我们的可用内存是1G.我们可以把数据分成1000份（这里只要大于100都是可以的），每次内存读入100M
   再去处理。但是问题的关键是怎么将这100G数据分成1000分呢。这里我们以前学过的hash函数就派上用场了。
   Hash函数的定义：对于输入的字符串，返回一个固定长度的整数，hash函数的巧妙之处在于对于相同的字符串，那么经过hash计算，
   得出来的结果肯定是相同的，不同的值，经过hash，结果可能相同（这种可能性一般都很小）或者不同。那么有了hash函数，
   那么这道题就豁然开朗了，思路如下：
   1.对于海量数据中的每一个ip，使用hash函数计算hash(ip)%1000,输出到1000个文件中
   2.对于这1000个文件，分别找出出现最多的ip。这里就可以用上面提到的Counter类的most_common()方法了（这里方法很多，不一一列举）
   3.使用外部排序，对找出来的1000个ip在进行排序。（这里数据量小，神马排序方法都行，影响不大）
   代码如下：可以直接运行
   
import os
import heapq
import operator
from collections import Counter
source_file = 'C:/Users/Administrator/Desktop/most_ip/bigdata.txt'  #原始的海量数据ip
temp_files = 'C:/Users/Administrator/Desktop/most_ip/temp/'         #把经过hash映射过后的数据存到相应的文件中
top_1000ip = []                                                     #存放1000个文件的出现频率最高的ip和出现的次数
def hash_file():
    """
     this function is map a query to a new file
    """
    temp_path_list = []
    if not os.path.exists(temp_files):
        os.makedirs(temp_files)
    for i in range(0,1000):
        temp_path_list.append(open(temp_files+str(i)+'.txt',mode='w'))
    with open(source_file) as f:
        for line in f:
            temp_path_list[hash(str(line))%1000].write(line)
            #print hash(line)%1000
            print line
    for i in range(1000):
        temp_path_list[i].close()
def cal_query_frequency():
    for root,dirs,files in os.walk(temp_files):
        for file in files:
            real_path = os.path.join(root,file)
            ip_list = []
            with open(real_path) as f:
                for line in f:
                    ip_list.append(line.replace('\n',''))
            try:
                top_1000ip.append(Counter(ip_list).most_common()[0])
            except:
                pass
    print top_1000ip
def get_ip():
    return (sorted(top_1000ip,key = lambda a:a[1],reverse=True)[0])[0]
if __name__ == '__main__':
   hash_file()
   cal_query_frequency()
   print(get_ip())

```

### 寻找热门查询，300万个查询字符串中统计最热门的10个查询

### 有一个1G大小的一个文件，里面每一行是一个词，词的大小不超过16字节，内存限制大小是1M。返回频数最高的100个词

### 海量数据分布在100台电脑中，想个办法高效统计出这批数据的TOP10

### 有10个文件，每个文件1G，每个文件的每一行存放的都是用户的query，每个文件的query都可能重复。要求你按照query的频度排##序

### 给定a、b两个文件，各存放50亿个url，每个url各占64字节，内存限制是4G，让你找出a、b文件共同的url

```
1.常规的解决办法，也是最容易想到的，就是对于文件A，读入内存，对于文件B中的每一个元素，判断是否在A中出现过。
我们来分析一下这样做的空间和时间复杂度：第一步，读入文件到内存，需要的内存是（50*（10**8）*64）= 320G内存，显然
我们在实际中没有那么大的内存。另外通过遍历A文件和B文件中的每一个元素，需要的时间复杂度是o(M*N)，M,N是两个
文件元素的大小，时间复杂度是（50亿*50亿）。。。。。。这是一个悲伤的算法

2.使用bloom过滤器。关于bloom过滤器，介绍它的文章太多了，稍微有点数学基础，都应该可以明白它的大致意思。
用一句话总结bloom过滤器就是：在需要查找，或者查重的场合，我们使用bloom过滤器能够使我们的搜索时间维持在o(1)的水平，
而不用去考虑文件的规模，另外它的空间复杂度也维持在一个可观的水平，但是它的缺陷是存在误报的情况，具体来说就是，
假如你要验证文件中是否存在某个元素，经过bloom过滤器，告诉你的结果是元素已经存在,那么真实的结果可能元素在文件中并不存在，
但是如果bloom过滤器告诉你的结果是不存在，那么文件中肯定不存在这个元素。下面具体分析问题：

3.使用hash算法，相同的url肯定掉进同一个hash
"""
对于A中50亿个文件，我们使用一个误报率为1%的bloom过滤器，那么经过计算（可以参考bloom的分析过程，里面有结论），每个元素
需要使用9.6bits，总计需要（50*(10**8）*9.6)bits =  6G，在内存的使用上，是符合我们要求的，然后对于使用A文件建立的bloom
过滤器，我们遍历B中的每一个元素，判断是否在A中出现过。
我使用了python的 pybloom模块，帮我们实现了bloom的功能。
代码在python2.7.10下测试通过
只用了9行代码
"""

from pybloom import BloomFilter               #pip install pybloom
bloom_A_file =  BloomFilter(capacity = 5000000000, error_rate=0.01)  #生成一个容量为50亿个元素，错误率为1%的bloom过滤器，
                                                           #这里需要估摸一下自己电脑的可用内存，至少保持电脑的可用内存在8G以上，
                                                           #否则死机不要找我。哈哈
with open(file_A) as f1:                      #遍历A文件中的每一个元素，加入到bloom过滤器中
    for sel in f1:
        bloom_A_file.add(sel)
with open(file_B) as f2:                      #遍历B文件，找出在A文件中出现的元素，并打印出来
    for sel in f2:
        if sel in bloom_A_file:
            print sel                       
```

### 在2.5亿个整数中找出不重复的整数，注，内存不足以容纳这2.5亿个整数

```
首先我们考虑在内存充足的情况下，我们可以使用python中的字典结构。对2.5亿个数中的每一个数，出现一次，字典对应的值+1.
最后遍历字典，找出value为1的所有key。代码很简单，10行都不到。

内存不充足的话，我们可以有两种解决方案。
（1）：假设内存有（2.5*（10**8）*2）/8*(10**9) = 0.06G。那么我们可以使用bit数组，下面我详细解释一下上面内存的计算过程：
因为数据可能存在的方式只有三种：没出现过，出现了一次，出现了很多次。所以我们用2bit表示这三种状态。另外数据有2.5亿条，
总计需要内存2.5亿*2 bit，约等于0.6G。算法的过程大致如下：
"""
1:  初始化一个(2.5*10^8) * 2 bool数组，并且初始化为False，对于每一个整数，使用
    2个bit来表示它出现的次数： 0 0：出现0次 0 1：出现一次 1 1:出现多次
2:  遍历文件，当数据是第一次出现的时候，，更改属于它的两个bit状态：从 00变成01
3： 最后遍历文件找出bit为01的数字，那么这个数字只出现了一次
"""

from collections import defaultdict
import numpy as np
mark =np.zeros((2.5*(10**8),2),dtype=np.bool) #初始化一个(2.5*10^8) * 2 bool数组，并且初始化为False，对于每一个整数，使用
两个bit来表示它出现的次数： 0 0：出现0次 0 1：出现一次 1 1:出现多次
def get_unique_int():
    with open('bigdata') as file:       #bigdata:原始的2.5亿个整数大文件
        for num in file:
            if mark[num][0] == False and mark[num][1] == False:  #这个数第一次出现。那么更改属于它的2个bit
                mark[num][0] = True
                mark[num][1] = False
            else:
                mark[num][0] = True                              #出现了不止一次的数据，那么同意赋值 1 1
                mark[num][1] = True
    with open('bigdata') as file:       #bigdata:原始的2.5亿个整数大文件
        for num in file:
        if mark[num][0] == True and mark[num][1] == False:
            yield num
    
    
if __name__ == '__main__':
    unique_list = get_unique_int()   #返回一个不重复整数的迭代器
```

### 100w个数中找出最大的100个数

```
"""
问题8： 100w个数中找出最大的100个数。时间复杂度尽可能的小
方案1：采用局部淘汰法。选取前100个元素，并排序，记为序列L。然后一次扫描剩余的元素x，与排好序的100个元素中最小的元素比，
       如果比这个最小的要大，那么把这个最小的元素删除，并把x利用插入排序的思想，插入到序列L中。
       依次循环，知道扫描了所有的元素。复杂度为O(100w*100)。
方案2：采用快速排序的思想，每次分割之后只考虑比轴大的一部分，知道比轴大的一部分在比100多的时候，采用传统排序算法排序，
       取前100个。复杂度为O(100w*100)。
方案3：在前面的题中，我们已经提到了，用一个含100个元素的最小堆完成。复杂度为O(100w*lg100)。
"""
代码实现如下：
import heapq    #引入堆模块
import random   #产生随机数
test_list = []  #测试列表
for i in range(1000000):                #产生100w个数，每个数在【0,1000w】之间
    test_list.append(random.random()*100000000)
heapq.nlagest(10,test_list)             #求100w个数最大的10个数
heapq.nsmallest(10,test_list)           #求100w个数最小的10个数
```

### 对于一个文本集合，把相似的单词进行归类。这里这样定义相似单词：两个单词只有一个字母不一样!

```
方法一：对于这个问题，我们最开始使用的是暴力穷举办法。遍历文本中的每个单词，找出在文本中与其相似的单词，
算法的时间复杂度是o(n2),
对于常见的英文词典，差不多有将近20000万个单词，那么需要经过4亿次运算，时间惊人，在实际中不可能行得通。
当然这里还是有一个trick，因为相似单词总是长度一样的，所以你也许可以少许多计算。（当然这不能从根本上改变大局）

方法二： 从相似单词的特点入手。‘son’和‘sun’都可以用正则表达式中的‘s.n’来表示，其中.在正则表达式中可以代表任意的符号
我们使用一个一个字典结构：key是正则字符串 value：是相似单词的集合。举个例子：对于单词'son',那么符合它的正则匹配有
‘.on’,'s.n','so.',那么字典中，分别是：key:'.on',value:'son',key:'s.n',value:'son',key:'so.',value:'son'，对于单词‘sun’,
进行同样的计算，同时字典开始更新：key:'.un',value:'sun',key:'s.n',value:['son','sun'],key:'so.',value:'son'
key:'su.',value:'sun'。这样遍历文本，最后的时间复杂度是o(n):

代码：
from collections import defaultdict  #使用了默认字典
words_dict = defaultdict(set)        #词典的value值默认为set（非重复的相似单词集合，例如‘son’和‘sun’）
def cal_similar_words(word):
    if len(word)!=0:
        for item in word:
            pattern = word.replace(item,'.')
            words_dict[pattern].add(word)
words_list = []    #文本单词集合          
with open(r'D:\programesoftware\NLTK\corpora\abc\science.txt') as file: #为了方便，我们读入一个txt文件，可以认为包含了
     words_list = re.findall(r'\w+',file.read())                        #所有常见的单词
for item in set(words_list):
    cal_similar_words(item.lower())
```

# 编译原理

### 简单编译原理
http://www.ruanyifeng.com/blog/2014/11/compiler.html

### 程序运行时堆栈的作用



# 项目

### 有料道
主要内容: 有料道是一个访谈问答形社区,类似于知乎,知乎是一问多答,这里是多问一答
数据库设计: 概要和主要内容分离,消息设计
redis设计: 将 zset 的 score 拆分成单个位
缓存设计: 单个内容分开缓存

异步的测试，分析过程，不如同步,改进后的异步



