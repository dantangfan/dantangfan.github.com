---
layout: post
title: 服务器编程的几种常见模型
description: 高性能的服务器是站点良好运作的基础，文章介绍了几种常见的服务器编程模型。
category: blog
---

废话不说，进入主题，例子都用为代码描述。

## 同步阻塞式

这是最简单的一种IO模型，它就是一个一问一答的形式。多数的python网络编程socket一节都会有一个简单服务器例子，就是这个模型：

```c
bind(serverfd);
listen(serverfd);
while(1):{
    clientfd = accept(serverfd, ...); //接收客户端传来的数据
    read(clientfd, buf, ...); //读取客户端数据
    do_logic(buf); //对数据进行操作，内部逻辑处理
    write(clientfd, buf); //返回客户端数据
}
```

很明显的可以看到，上面有几个地方是需要等待的。

- 等待客户端请求，如果没有客户端发起请求的话，就会一直等着。
- 读取客户端数据，建立请求后，就需要等着客户端送来数据(我们知道tcp连接是有几次握手的，所以不能直接来数据)，此时不能接受其他客户端的连接。
- 同样，写回客户端的时候也需要等待。

## 多进程

同步的方式几乎已经失传了，多进程稍稍改进了同步阻塞的问题：

```c
bind(serverfd);
listen(serverfd);
while(1){
    clientfd = accept(serverfd, ...);
    ret = fork();
    switch(ret){
        case -1: //出错
            error();
            break;
        case 0: //子进程
            client(clientfd);
            break;
        default:
            close(clientfd);
            continue;
    }
}

void clien(clientfd){
    read(clientfd, buf, ...);
    do_logic(buf);
    write(clientfd, buf);
}
```

这样做的效果很明显，可以让每个进程处理一个请求，所以有多个请求来的时候就不会等待了。

但是劣势也很明显，fork一个进程的资源耗费太大了，而且系统资源有限，所以能处理请求的个数也很有限。

##多线程

这个就不用多说了，跟多进程的处理方式差不多，只是把进程换成了线程。这样虽然相对减少了资源消耗，但是如果一个线程跪了，其他的都得跪。

## I/O多路复用之select

多进程/线程模型每个进程/线程都只能处理一路IO，这样过多的请求也会让服务器不堪重负。而通过IO复用，让一个进程可以处理多个请求，简单描述如下：

```c 
bind(serverfd);
listen(serverfd);
FD_ZERO(&allset);
FD_SET(serverfd, &allset); //allset是一个数组，用于记录监听的连接
while(1){
    select(...);
    if(FD_ISSET(serverfd, &rset)){ //有新的连接来了
        clientfd = accept();
        clientarray[] = clientfd; //保存新连接的套接字
        FD_SET(clientfd, &allset); //将新连接的描述符加入到监听数组中
    }
    for(;;){//检查所有已经连接的客户端是否有数据参与读写
        fd = clientarray[i];
        if(FD_ISSET(fd, &rset)){
            do_logic();
        }
    }
}
```

从代码中我们可以看到这种模型一样有缺点：

1. 单个进程能够监听的文件描述符有限，监听得越多性能越差（在大于一定的数量之后）
2. 内核/用户空间之间拷贝数据，产生大量开销
3. 内核返回的是含有整个句柄的数组，应用程序要遍历数组才能知道哪些句柄发生了事件。
4. select是水平触发，应用程序如果没有完成对一个已经就绪的文件描述符的IO操作，那么之后每次select调用还是会将这些文件描述符通知进程。

##IO多路复用之epoll

因为select/epoll都是使用的水平触发，所以这里简单学习下水平触发(LT)和边缘触发(ET)。

- 水平触发：只要满足条件就发生一个IO事件
- 边缘触发：每当状态变化时发生一个IO事

用人话简单解释的话大概是这个意思：

- 水平触发：内核告诉你一个文件描述符就绪，然后你就可以对这个描述符进行IO操作。如果你不操作，那么内核就一直给你说这个文件描述符已经就绪了。默认是不能操作描述符的，只有通知了你你才能操作。
- 边缘触发：当描述符从未就绪变成就绪的时候，内核就告诉你。然后内核就假设你已经知道这个描述符就绪，就算你没有对它进行任何操作，内核也再也不会给你说了。默认是可以操作描述符的，因为只会通知你一次，你可以随时去取。

那epoll使用水平触发的有点在哪里呢：

1. 因为select也是使用的epoll，所以当某些系统epoll不可用的时候能优雅的降级到select
2. 水平触发对应用程序更简单（实现），也更适合http这种请求响应的模式（读完就写，不用管写的状态）。

这里有参考文章，里面介绍了epoll的实现机理。[高并发网络编程之epoll详解](http://www.cricode.com/3499.html)但是我觉得这些东西了解就行了，至于怎样才能让他更高效，这应该是内核开发人员的事情。

所以简要介绍epoll，这里选取了来自知乎的答案[ epoll 或者 kqueue 的原理是什么？](http://www.zhihu.com/question/20122137)，如下

首先我们来定义流的概念，一个流可以是文件，socket，pipe等等可以进行I/O操作的内核对象。
不管是文件，还是套接字，还是管道，我们都可以把他们看作流。
之后我们来讨论I/O的操作，通过read，我们可以从流中读入数据；通过write，我们可以往流写入数据。现在假定一个情形，我们需要从流中读数据，但是流中还没有数据，（典型的例子为，客户端要从socket读如数据，但是服务器还没有把数据传回来），这时候该怎么办？

- 阻塞。阻塞是个什么概念呢？比如某个时候你在等快递，但是你不知道快递什么时候过来，而且你没有别的事可以干（或者说接下来的事要等快递来了才能做）；那么你可以去睡觉了，因为你知道快递把货送来时一定会给你打个电话（假定一定能叫醒你）。
- 非阻塞忙轮询。接着上面等快递的例子，如果用忙轮询的方法，那么你需要知道快递员的手机号，然后每分钟给他挂个电话：“你到了没？”

很明显一般人不会用第二种做法，不仅显很无脑，浪费话费不说，还占用了快递员大量的时间。
大部分程序也不会用第二种做法，因为第一种方法经济而简单，经济是指消耗很少的CPU时间，如果线程睡眠了，就掉出了系统的调度队列，暂时不会去瓜分CPU宝贵的时间片了。

为了了解阻塞是如何进行的，我们来讨论缓冲区，以及内核缓冲区，最终把I/O事件解释清楚。缓冲区的引入是为了减少频繁I/O操作而引起频繁的系统调用（你知道它很慢的），当你操作一个流时，更多的是以缓冲区为单位进行操作，这是相对于用户空间而言。对于内核来说，也需要缓冲区。
假设有一个管道，进程A为管道的写入方，Ｂ为管道的读出方。

- 假设一开始内核缓冲区是空的，B作为读出方，被阻塞着。然后首先A往管道写入，这时候内核缓冲区由空的状态变到非空状态，内核就会产生一个事件告诉Ｂ该醒来了，这个事件姑且称之为“缓冲区非空”。
- 但是“缓冲区非空”事件通知B后，B却还没有读出数据；且内核许诺了不能把写入管道中的数据丢掉这个时候，Ａ写入的数据会滞留在内核缓冲区中，如果内核也缓冲区满了，B仍未开始读数据，最终内核缓冲区会被填满，这个时候会产生一个I/O事件，告诉进程A，你该等等（阻塞）了，我们把这个事件定义为“缓冲区满”。
- 假设后来Ｂ终于开始读数据了，于是内核的缓冲区空了出来，这时候内核会告诉A，内核缓冲区有空位了，你可以从长眠中醒来了，继续写数据了，我们把这个事件叫做“缓冲区非满”
- 也许事件Y1已经通知了A，但是A也没有数据写入了，而Ｂ继续读出数据，知道内核缓冲区空了。这个时候内核就告诉B，你需要阻塞了！，我们把这个时间定为“缓冲区空”。

这四个情形涵盖了四个I/O事件，缓冲区满，缓冲区空，缓冲区非空，缓冲区非满（注都是说的内核缓冲区，且这四个术语都是我生造的，仅为解释其原理而造）。这四个I/O事件是进行阻塞同步的根本。（如果不能理解“同步”是什么概念，请学习操作系统的锁，信号量，条件变量等任务同步方面的相关知识）。

然后我们来说说阻塞I/O的缺点。但是阻塞I/O模式下，一个线程只能处理一个流的I/O事件。如果想要同时处理多个流，要么多进程(fork)，要么多线程(pthread_create)，很不幸这两种方法效率都不高。
于是再来考虑非阻塞忙轮询的I/O方式，我们发现我们可以同时处理多个流了（把一个流从阻塞模式切换到非阻塞模式再此不予讨论）：

```c
while true {
    for i in stream[]{
        if i has data
        read until unavailable;
    }
}
```

我们只要不停的把所有流从头到尾问一遍，又从头开始。这样就可以处理多个流了，但这样的做法显然不好，因为如果所有的流都没有数据，那么只会白白浪费CPU。这里要补充一点，阻塞模式下，内核对于I/O事件的处理是阻塞或者唤醒，而非阻塞模式下则把I/O事件交给其他对象（后文介绍的select以及epoll）处理甚至直接忽略。

为了避免CPU空转，可以引进了一个代理（一开始有一位叫做select的代理，后来又有一位叫做poll的代理，不过两者的本质是一样的）。这个代理比较厉害，可以同时观察许多流的I/O事件，在空闲的时候，会把当前线程阻塞掉，当有一个或多个流有I/O事件时，就从阻塞态中醒来，于是我们的程序就会轮询一遍所有的流（于是我们可以把“忙”字去掉了）。代码长这样:

```c
while true {
    select(streams[]);
    for i in streams[] {
        if i has data
        read until unavailable;
    }
}
```

于是，如果没有I/O事件产生，我们的程序就会阻塞在select处。但是依然有个问题，我们从select那里仅仅知道了，有I/O事件发生了，但却并不知道是那几个流（可能有一个，多个，甚至全部），我们只能无差别轮询所有流，找出能读出数据，或者写入数据的流，对他们进行操作。
但是使用select，我们有O(n)的无差别轮询复杂度，同时处理的流越多，每一次无差别轮询时间就越长。再次
说了这么多，终于能好好解释epoll了
epoll可以理解为event poll，不同于忙轮询和无差别轮询，epoll之会把哪个流发生了怎样的I/O事件通知我们。此时我们对这些流的操作都是有意义的。（复杂度降低到了O(k)，k为产生I/O事件的流的个数）
在讨论epoll的实现细节之前，先把epoll的相关操作列出：


    epoll_create 创建一个epoll对象，一般epollfd = epoll_create()
    epoll_ctl （epoll_add/epoll_del的合体），往epoll对象中增加/删除某一个流的某一个事件
    比如
    epoll_ctl(epollfd, EPOLL_CTL_ADD, socket, EPOLLIN);//有缓冲区内有数据时epoll_wait返回
    epoll_ctl(epollfd, EPOLL_CTL_DEL, socket, EPOLLOUT);//缓冲区可写入时epoll_wait返回
    epoll_wait(epollfd,...)等待直到注册的事件发生


（注：当对一个非阻塞流的读写发生缓冲区满或缓冲区空，write/read会返回-1，并设置errno=EAGAIN。而epoll只关心缓冲区非满和缓冲区非空事件）。
一个epoll模式的代码大概的样子是：

```c
while true {
    active_stream[] = epoll_wait(epollfd);
    for i in active_stream[] {
        read or write till unavailable
    }
}
```

### python中使用epoll

这里只使用了水平触发的方式写做示例。如果使用边缘触发，那程序就需要在每次调用epoll.poll()之前处理完当前事件，这样就需要加入多个for循环，不过也不难理解。

更多的示例请参见[python-epoll-howto](http://scotdoyle.com/python-epoll-howto.html)

```python
import socket, select  # select模块中已经集成了epoll

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('0.0.0.0', 8080))
serversocket.listen(1)
serversocket.setblocking(0)  # socket默认是阻塞的，我们需要手动设置成非阻塞

epoll = select.epoll()  # 建立一个epoll对象
epoll.register(serversocket.fileno(), select.EPOLLIN)  #注册服务器socket，监听读取事件，服务器socket收到一个连接时，产生一个读取事件

try:
    connections = {}; requests = {}; responses = {}  # connections存储网络连接的文件描述符(file descripors, 整型)
    while True:
        events = epoll.poll(1)  # epoll对象查询是否有感兴趣对象产生， 参数1表示最多等1秒。如果有事件发生，立即返回事件列表。
        for fileno, event in events:
            if fileno == serversocket.fileno():  # 如果是服务器socket事件，就新建一个连接
                connection, address = serversocket.accept()
                connection.setblocking(0)  # 设置成非阻塞模式
                epoll.register(connection.fileno(), select.EPOLLIN)  # 注册socket的read事件，等待从客户端读
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = response
            elif event & select.EPOLLIN:  # 如果read事件发生，就从客户端读取事件
                requests[fileno] += connections[fileno].recv(1024)
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:  # 分片读取，如果http请求结束，取消注册读取，并注册写回
                    epoll.modify(fileno, select.EPOLLOUT)
                    print('-'*40 + '\n' + requests[fileno].decode()[:-2])
            elif event & select.EPOLLOUT:  # 如果是写回，发送数据给客户端
                byteswritten = connections[fileno].send(responses[fileno])
                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:  # 每次发送一部分数据，直到结束。取消注册的写回事件，
                    epoll.modify(fileno, 0)
                    connections[fileno].shutdown(socket.SHUT_RDWR)  # 关闭连接（可选）
            elif event & select.EPOLLHUP:  # 客户端断开连接
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
finally:  # 可选，因为socket会主动关闭连接
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()
```