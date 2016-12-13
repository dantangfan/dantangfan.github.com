## select 模型
#### 原理
网络通信被unix抽象为文件读写，由底层的设备驱动程序来决定自身数据是否可用。支持阻塞操作的设备驱动通常会实现一个自身的等待队列，
如读写队列用于上层的block/non-block操作。设备文件资源如果可用，则会通知进程，反之进程睡眠。

这些设备的文件描述符被放在一个数组中，调用select的时候会遍历这个数组，如果文件描述符可读，就提取出来，并在后续处理。
如果没有则进程继续睡眠。每次遍历都是线性的，因此在描述符过多的时候效率降低，并且描述符的数量还受到系统的限制。

#### 实例

```
#!/usr/bin/env python
# coding:utf-8

import select
import socket

HOST = "localhost"
PORT = 8888
BUFFER_SIZE = 1024

server = socket.socket()
server.bind((HOST,PORT))
server.listen(5)

inputs = [server]
outputs = []
timeout = 20


while True:
    try:
        # 在超时时间之后返回，如果不设置超时时间，则一直等待
        readable, writeable, exceptionable = select.select(inputs, outputs, [], timeout)
    except select.error, e:
        break
    for sock in readable:
        if sock == server:
            conn, addr = sock.accept()
            print "connection from ", addr
            inputs.append(conn)
        else:
            try:
                data = sock.recv(BUFFER_SIZE)
                if data:
                    sock.send(data)
                    print "get data ", data, " from ", sock.getpeername()
                    if data.endswith('\r\n\r\n'):
                        inputs.remove(sock)
                        sock.close()
                else:
                    inputs.remove(sock)
                    sock.close()
            except socket.error, e:
                inputs.remove(sock)
server.close()
```

## epoll 模型
#### 原理
[学习资源](http://scotdoyle.com/python-epoll-howto.html)

#### 实例

```
#!/usr/bin/env python
# coding:utf-8

import socket
import select

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

# 创建套接字对象并绑定监听端口
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 设置端口复用，这样就能防止一个进程关闭时候，占用的端口出现time_wait状态
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('0.0.0.0', 8080))
serversocket.listen(1)
serversocket.setblocking(0)

# 创建epoll对象，并注册socket对象的 epoll可读事件
epoll = select.epoll()
epoll.register(serversocket.fileno(), select.EPOLLIN)

try:
    connections = {}
    requests = {}
    responses = {}
    while True:
        # 主循环，epoll的系统调用，一旦有网络IO事件发生，poll调用返回。这是和select系统调用的关键区别
        events = epoll.poll(1)
        # 通过事件通知获得监听的文件描述符，进而处理
        for fileno, event in events:
            # 注册监听的socket对象可读，获取连接，并注册连接的可读事件
            if fileno == serversocket.fileno():
                connection, address = serversocket.accept()
                connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = response
            elif event & select.EPOLLIN:
                # 连接对象可读，处理客户端发生的信息，并注册连接对象可写
                requests[fileno] += connections[fileno].recv(1024)
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                    epoll.modify(fileno, select.EPOLLOUT)
                    print('-' * 40 + '\n' + requests[fileno].decode()[:-2])
            elif event & select.EPOLLOUT:
                # 连接对象可写事件发生，发送数据到客户端
                byteswritten = connections[fileno].send(responses[fileno])
                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:
                    epoll.modify(fileno, 0)
                    connections[fileno].shutdown(socket.SHUT_RDWR)
            elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
finally:
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()
```