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
