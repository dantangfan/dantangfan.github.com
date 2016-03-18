---
layout: post
title: tornado 异步数据库
description: 在使用 tornado 的时候，我们总是希望所有的操作都能够异步，如果其中某些必须操作没有异步，那整个框架都会被阻塞。
category: blog
---

在使用 tornado 的时候，我们总是希望所有的操作都能够异步，如果其中某些必须操作没有异步，那整个框架都会被阻塞。

而 tornado 自带的 torndb 是以 MySQLdb 为核心，并不支持异步处理，而在实际开发过程中，我们总是希望我们的服务器是全异步的，这时候，就需要用到异步的 mysql 了。

当然，你我都不是第一个遇到这个问题的童鞋，已经有人帮我们实现了这份代码 [tornado-mysql](https://github.com/PyMySQL/Tornado-MySQL) ，代码能够很好的进行异步。

然而，好景不长，这个库是基于 pymysql 的，是纯 python 实现的。虽然实现了异步，但实际效率跟 torndb 比起来，不升反降。原因很简单，python 的函数调用太过昂贵，过多的函数调用，耗时远超过了网路 IO。

用一份简单的代码做了个性能测试

```
from tornado.gen import coroutine
import tornado.ioloop
import torndb
import pymysql
import asynctorndb # tornado-mysql 一样的
import time
import cProfile
import StringIO
import contextlib
import pstats


import random
def get_sql():
    offset = random.randint(0, 300)
    limit = random.randint(offset, 300) - offset
    sql = "SELECT * FROM user limit %s, %s" % (offset, limit)
    return sql


@contextlib.contextmanager
def profiled(dbapi):
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    pr.dump_stats("profile.stats")
    s = StringIO.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print "DBAPI:  %s" % dbapi
    print s.getvalue()


@contextlib.contextmanager
def timeonly(dbapi):
    now = time.time()
    try:
        yield
    finally:
        total = time.time() - now
        print "DBAPI:  %s, total seconds %f" % (dbapi, total)


def torndb_test(ctx, count=500):
    conn = torndb.Connection(host="localhost:3306", user="yld", password="yld@6874#~", database="yld")
    with ctx('torndb'):
        for i in range(count):
            conn.query(get_sql())


def pymysql_test(ctx, count=500):
    conn = pymysql.connect(host="localhost", port=3306, user="yld", passwd="yld@6874#~", database="yld")
    with ctx('pymysql'):
        for i in range(count):
            with conn as cursor:
                cursor.execute(get_sql())


def asynctorndb_test(ctx, count=500):
    conn = asynctorndb.Connect(host="localhost", port=3306, user="yld", passwd="yld@6874#~", database="yld")
    with ctx('asynctorndb'):

        @coroutine
        def get():
            yield conn.connect()
            for i in range(count):
                res = yield conn.query(get_sql())
        tornado.ioloop.IOLoop.current().run_sync(get)

if __name__ == "__main__":
    #torndb_test(timeonly)
    #pymysql_test(timeonly)
    #asynctorndb_test(timeonly)
    torndb_test(profiled, 500)
    pymysql_test(profiled, 500)
    asynctorndb_test(profiled, 500)
```

在我的 mac 上测试结果如下

- time-only

    ```
    DBAPI:  torndb, total seconds 1.641382
    DBAPI:  pymysql, total seconds 2.726989
    DBAPI:  asynctorndb, total seconds 5.655147
    ```

- profiled

    ```
    DBAPI:  torndb
             2348270 function calls in 2.159 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
          500    0.082    0.000    2.153    0.004 /Library/Python/2.7/site-packages/torndb.py:132(query)
          500    0.001    0.000    2.061    0.004 /Library/Python/2.7/site-packages/torndb.py:232(_execute)
          500    0.002    0.000    2.061    0.004 /Library/Python/2.7/site-packages/MySQLdb/cursors.py:164(execute)
          500    0.001    0.000    2.055    0.004 /Library/Python/2.7/site-packages/MySQLdb/cursors.py:353(_query)
          500    0.002    0.000    1.828    0.004 /Library/Python/2.7/site-packages/MySQLdb/cursors.py:358(_post_get_result)
          500    0.001    0.000    1.827    0.004 /Library/Python/2.7/site-packages/MySQLdb/cursors.py:324(_fetch_row)
          500    0.297    0.001    1.826    0.004 {built-in method fetch_row}
       476860    0.153    0.000    0.793    0.000 /Library/Python/2.7/site-packages/MySQLdb/connections.py:212(string_decoder)
       103828    0.636    0.000    0.736    0.000 /Library/Python/2.7/site-packages/MySQLdb/times.py:44(DateTime_or_None)
       476860    0.227    0.000    0.640    0.000 {method 'decode' of 'str' objects}
       476860    0.148    0.000    0.413    0.000 /usr/local/Cellar/python/2.7.10_2/Frameworks/Python.framework/Versions/2.7/lib/python2.7/encodings/utf_8.py:15(decode)
       476860    0.265    0.000    0.265    0.000 {_codecs.utf_8_decode}
          500    0.002    0.000    0.226    0.000 /Library/Python/2.7/site-packages/MySQLdb/cursors.py:315(_do_query)
          500    0.174    0.000    0.174    0.000 {method 'query' of '_mysql.connection' objects}
    ```

    ```
    DBAPI:  pymysql
             6967998 function calls in 4.259 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
          500    0.001    0.000    4.155    0.008 /usr/local/lib/python2.7/site-packages/pymysql/cursors.py:139(execute)
          500    0.001    0.000    4.149    0.008 /usr/local/lib/python2.7/site-packages/pymysql/cursors.py:293(_query)
          500    0.002    0.000    4.147    0.008 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:810(query)
          500    0.002    0.000    4.133    0.008 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:990(_read_query_result)
          500    0.002    0.000    4.130    0.008 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:1283(read)
          500    0.002    0.000    3.907    0.008 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:1344(_read_result_packet)
          500    0.068    0.000    3.499    0.007 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:1377(_read_rowdata_packet)
        36274    0.572    0.000    3.090    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:1390(_read_row_from_packet)
       824754    0.477    0.000    1.765    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:347(read_length_coded_string)
        48774    0.143    0.000    0.938    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:939(_read_packet)
       102446    0.705    0.000    0.813    0.000 /usr/local/lib/python2.7/site-packages/pymysql/converters.py:148(convert_datetime)
       826254    0.325    0.000    0.785    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:329(read_length_encoded_integer)
       781251    0.438    0.000    0.506    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:242(read)
        97548    0.069    0.000    0.467    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:968(_read_bytes)
       826254    0.389    0.000    0.460    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:291(read_uint8)
          500    0.026    0.000    0.405    0.001 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:1403(_get_descriptions)
        97548    0.118    0.000    0.389    0.000 {method 'read' of '_io.BufferedReader' objects}
         1611    0.006    0.000    0.270    0.000 /usr/local/lib/python2.7/site-packages/pymysql/_socketio.py:45(readinto)
        10500    0.012    0.000    0.267    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:407(__init__)
         1611    0.260    0.000    0.260    0.000 {method 'recv_into' of '_socket.socket' objects}
        10500    0.046    0.000    0.252    0.000 /usr/local/lib/python2.7/site-packages/pymysql/connections.py:411(__parse_field_descriptor)
       307338    0.108    0.000    0.108    0.000 {method 'split' of 'str' objects}
       829528    0.098    0.000    0.098    0.000 {method 'append' of 'list' objects}
    ```
    
    ```
    DBAPI:  asynctorndb
             15177734 function calls (14905240 primitive calls) in 9.751 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000    9.751    9.751 /usr/local/lib/python2.7/site-packages/tornado/ioloop.py:400(run_sync)
            1    0.031    0.031    9.751    9.751 /usr/local/lib/python2.7/site-packages/tornado/ioloop.py:746(start)
         5012    0.008    0.000    9.634    0.002 /usr/local/lib/python2.7/site-packages/tornado/stack_context.py:271(null_wrapper)
         4508    0.005    0.000    9.599    0.002 /usr/local/lib/python2.7/site-packages/tornado/ioloop.py:594(_run_callback)
         4506    0.008    0.000    9.586    0.002 /usr/local/lib/python2.7/site-packages/tornado/gen.py:1097(<lambda>)
    39510/4507    0.468    0.000    9.579    0.002 /usr/local/lib/python2.7/site-packages/tornado/gen.py:990(run)
    134987/5509    0.052    0.000    9.493    0.002 {method 'send' of 'generator' objects}
    38507/1003    0.121    0.000    9.260    0.009 /usr/local/lib/python2.7/site-packages/tornado/gen.py:257(wrapper)
    38507/5006    0.134    0.000    9.156    0.002 /usr/local/lib/python2.7/site-packages/tornado/gen.py:938(__init__)
         1500    0.002    0.000    9.113    0.006 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:1202(read)
         1500    0.002    0.000    9.032    0.006 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:1250(_read_result_packet)
        73474    0.217    0.000    5.866    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:1286(_read_rowdata_packet)
        35987    1.014    0.000    4.018    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:1318(_read_row_from_packet)
    38509/1504    0.017    0.000    2.470    0.002 {next}
        11500    0.030    0.000    2.134    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:1342(_get_descriptions)
       818727    0.510    0.000    2.102    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:353(read_length_coded_string)
        95978    0.222    0.000    1.992    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:294(read_bytes)
        23000    0.037    0.000    1.797    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:952(_read_packet)
        95978    0.127    0.000    1.347    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:688(_try_inline_read)
        21000    0.027    0.000    1.334    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:403(recv_packet)
       819227    0.494    0.000    1.102    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:335(read_length_encoded_integer)
        95978    0.088    0.000    1.096    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:762(_read_from_buffer)
      1648034    0.926    0.000    1.058    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:287(read)
       134987    0.269    0.000    1.053    0.000 /usr/local/lib/python2.7/site-packages/tornado/gen.py:1051(handle_yield)
        95978    0.172    0.000    1.008    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:669(_run_read_callback)
       101287    0.732    0.000    0.853    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/converters.py:100(convert_datetime)
        95978    0.118    0.000    0.616    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:876(_consume)
        34506    0.044    0.000    0.561    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:260(recv_packet)
       134988    0.132    0.000    0.531    0.000 /usr/local/lib/python2.7/site-packages/singledispatch.py:209(wrapper)
       885933    0.305    0.000    0.527    0.000 {isinstance}
        96980    0.388    0.000    0.490    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:1510(_merge_prefix)
        10500    0.091    0.000    0.395    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:408(__parse_field_descriptor)
         1000    0.096    0.000    0.360    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:746(query)
       134988    0.104    0.000    0.235    0.000 /usr/local/lib/python2.7/site-packages/tornado/gen.py:1200(convert_yielded)
          502    0.015    0.000    0.225    0.000 call_graph.py:65(get)
       134487    0.126    0.000    0.221    0.000 /usr/local/Cellar/python/2.7.10_2/Frameworks/Python.framework/Versions/2.7/lib/python2.7/abc.py:128(__instancecheck__)
      2131830    0.182    0.000    0.182    0.000 {len}
        95978    0.092    0.000    0.181    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:660(_set_read_callback)
         1000    0.004    0.000    0.178    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/cursors.py:105(execute)
       134987    0.093    0.000    0.178    0.000 /usr/local/lib/python2.7/site-packages/tornado/gen.py:621(_contains_yieldpoint)
    134989/134988    0.075    0.000    0.172    0.000 /usr/local/lib/python2.7/site-packages/tornado/concurrent.py:264(set_result)
       134988    0.107    0.000    0.165    0.000 /usr/local/lib/python2.7/site-packages/singledispatch.py:173(dispatch)
         1000    0.002    0.000    0.163    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/cursors.py:276(_query)
         1500    0.002    0.000    0.139    0.000 build/bdist.macosx-10.11-x86_64/egg/asynctorndb/connection.py:845(execute_query)
       134989    0.088    0.000    0.135    0.000 /usr/local/lib/python2.7/site-packages/tornado/concurrent.py:220(result)
       992354    0.133    0.000    0.133    0.000 {method 'append' of 'list' objects}
       134989    0.123    0.000    0.123    0.000 /usr/local/lib/python2.7/site-packages/tornado/concurrent.py:163(__init__)
       303861    0.122    0.000    0.122    0.000 {method 'split' of 'str' objects}
        96479    0.096    0.000    0.114    0.000 /usr/local/lib/python2.7/site-packages/tornado/iostream.py:887(_maybe_add_error_listener)
    ```

上面的 profile 测试只是部分截图，能看出来哪些哪些函数调用很多。

从上面 timeonly 测试的对比可以看出，torndb 的性能是最好的， pymysql 相比差得多，而 torando-mysql 就差的不是一点半点了。

从 profile 测试对比看出，torndb 调用函数 200w+ 次，pymysql 调用 600w+ 次，tornado-mysql 调用 1500w+ 。对比简直太明显了。

然后就想到了曲径通幽，用 celery 做异步，用 thread 做异步，实际效果都跟 tornado-mysql 差不多。

看来，不想怪招是不行了。

前面，我们看到 torndb 和 pymysql 的性能差距是两倍左右，仅仅是因为一个是 C 实现，一个是 python 实现。那我们能不能想个办法用 torndb，并在 C 层面上实现异步呢？

找了好久解决方案，发现豆瓣已经帮我们把这个功能实现了。 ## 这真是一家神奇的公司，开源产品一个接一个的屌啊

于是找到了豆瓣的 [greenify-douban](https://github.com/douban/greenify)

greenify 这个库可以将 c-based-socket 通过 elf-hook 实现 c 层面的异步，进而于 gevent 一起使用。

虽然不太会写 C，但是浏览代码之后，发现只有 pyx 文件里面的内容才是跟 gevent 有关的，那要实现最终目标，只需要在 pyx 里面跟 tornado 做适配就行了。

### gevent 简介

我们知道，使用 gevent ，我们可以使用同步的方式写异步代码。 gevent 基础是 greenlet 和 libev 。简单的说， greenlet 就是通过对栈空间的切换来实现协成，不过，我们需要手动控制这个切换。 libev 是 C 语言实现的高效的事件循环。

我们也都知道， gevent 不能跟非 python 实现 socket 配合使用（而不是不能和非纯 python 配合），因为 gevent 底层是 libev ，它从其之上再造了一个 socket 模块，具有跟标准库 socket 兼容的接口。 gevent.monkey.patch_all() 会用它的 socket 替代掉标准库里的 socket。所以当你的代码 import socket ，等价于 import gevent.socket；
time/thread/threading/queue/... 等模块也是同样的道理。

当一个库的代码是纯 Python 的时候，加上 monkey patch 技法，那么这个库使用的就是 gevent.socket 了，从而不需要任何更改就能够获得 gevent 的同步代码异步执行能力。

其实不仅仅是 socket，gevent.monkey.patch_all() 里面参数所指的所有 module 都必须是用原生 python 实现的才能 patch 成功

但想要跟 tornado 一起使用还有一个小问题，就是 tornado 有自己的 io 循环， gevent 也有自己的 io 循环。明显，我们需要拆掉 greenify 中 genven 的 io 循环，并加上 tornado 的循环。

### greenify

我们先看看 greenify 怎么玩儿：

对于 greenify 库，只需要使用两个函数 `greenify.patch_lib(lib_path)` 和 `greenify.grennify()`

patch_lib 函数实现了对 C 实现的 Socket 的异步化，需要 elf 格式文件的知识，不太懂。

我们这里需要关心的只有 greenify() 这个函数干了啥

从 .pyx 文件中我们可以看到

```
def greenify():
    greenify_set_wait_callback(wait_gevent)
```

然后在 libgreenify.c 中有这个函数

```
void greenify_set_wait_callback(greenify_wait_callback_func_t callback)
{
    g_wait_callback = callback;
}
```

意思就是把 .pyx 中的 wait_gevent 函数当成了 greenify 的全局回调函数

那我们随便找一个地方看，啥时候这个回调函数会被执行，比如说就找 connect 的时候吧。

在 libgreenify.c 中国的 green_connect() 函数就是创建 socket 连接的函数。

```
int
green_connect(int socket, const struct sockaddr *address, socklen_t address_len)
{
    int flags, s_err, retval;

    debug("Enter green_connect\n");

    if (g_wait_callback == NULL || !set_nonblock(socket, &flags)) { //将socket设置成飞阻塞
        retval = connect(socket, address, address_len);
        return retval;
    }

    retval = connect(socket, address, address_len); //连接
    s_err = errno;
    if (retval < 0 && (s_err == EWOULDBLOCK || s_err == EALREADY || s_err == EINPROGRESS)) {  //链接失败
        callback_single_watcher(socket, EVENT_WRITE, 0);
        getsockopt(socket, SOL_SOCKET, SO_ERROR, &s_err, &address_len);
        retval = s_err ? -1 : 0;
    }

    restore_flags(socket, flags);
    errno = s_err;
    return retval;
}
```

代码中我们可以看到，如果创建连接成功，就会直接 restore_flags() 保存现场然后直接异步返回了，并没有看到回调函数哪里使用了。但是我们再看创建失败的时候，比如说 patch 没成功，被阻塞、重复创建等都会触发回调函数的使用。 `callback_single_watcher(socket, EVENT_WRITE, 0);` 表示这里已经有一个就绪的 socket 了，放到 eventloop 中等待事件.

```
int callback_single_watcher(int fd, int events, int timeout)
{
    struct greenify_watcher watchers[1];
    int retval;

    assert(g_wait_callback != NULL);

    watchers[0].fd = fd;
    watchers[0].events = events;
    retval = g_wait_callback(watchers, 1, timeout);
    return retval;
```

这个时候才调用了全局的回调函数。好叻，搞清楚逻辑了，那我们再来看看这个回调函数里面都干了些啥

```
cdef int wait_gevent(greenify_watcher* watchers, int nwatchers, int timeout_in_ms) with gil:
    cdef int fd, event
    cdef float timeout_in_s
    cdef int i

    hub = get_hub()
    watchers_list = []
    for i in range(nwatchers):
        fd = watchers[i].fd
        event = watchers[i].events
        watcher = hub.loop.io(fd, event)
        watchers_list.append(watcher)

    if timeout_in_ms != 0:
        timeout_in_s = timeout_in_ms / 1000.0
        t = Timeout.start_new(timeout_in_s)
        try:
            wait(watchers_list)
            return 0
        except Timeout:
            return -1
        finally:
            t.cancel()
    else:
        wait(watchers_list)
        return 0
```

一边看一遍解释。 get_hub() 函数获取了 gevent 的全局 ioloop(Hub) 。 gevnet 对 libev 进行了包装，所有的事件都被统称为 watcher ，包括 io , timer 等。

跟 greenlet 不易样，greenlet 里面，生成的每个 greenlet 都需要指定一个 parent ，当子 greenlet 完成之后会回到父 greenlet ，默认情况下， parent 就是主协成。

gevent 将所有的 parent 都指向了 Hub ，并将其作为 threadlocal 的一个属性。这样，所有的协程操作都由 Hub 管理。

上面函数 hub.loop.io() 其实就是将输入的文件描述符和 event 创建一个 io 事件， socket 、 select 、 poll 中在注册的都是 io 事件，直接看 timeout_in_ms=0 的情况，
直接执行了 wait() 函数。

```
def wait(watchers):
    waiter = Waiter()
    switch = waiter.switch
    unique = object()
    try:
        count = len(watchers)
        for watcher in watchers:
            watcher.start(switch, unique)
        result = waiter.get()
        assert result is unique, 'Invalid switch into %s: %r' % (getcurrent(), result)
        waiter.clear()
        return result
    finally:
        for watcher in watchers:
            watcher.stop()
```

Waiter() 类是 gevent 的简单实现，waiter 对象可以理解为 gevent 封装的协程之间的协作工具，具体的协程之间的切换都由 waiter 来做，避免让用户自己的代码涉及到 switch 操作，因为这样子很容易出错。

waiter.switch 方法调度 greenlet 的执行，这个方法只能在 hub 的 loop 里面执行。然后 watcher.start(switch, unique) 这里执行了 watcher 事件，并将 switch 作为回调函数.

然后调用了 waiter.get 方法，get 方法保存当前执行的协程，然后切换到 hub 的执行，对于 switch 方法，将会切换回刚开始的协程的执行(所以 wiater.switch 只能在 hub 中调用)。

当 watcher.start() 超时的时候将会调用 waiter 的 switch 方法，对于 assert result is unique ，因为正常肯定是 hub.loop 调用 waiter.switch(unique) ，那么 waiter.get() 获取的肯定是 unique 。

到这里，greenify 就算分析完了。

这里没有处理比如 socket.read 没有读完的情况，因为在 libgreenify.c 中定义的所有 read 、 write 、 recv 等函数中都有自己处理。

### 把 greenify 和 tornado 结合起来

实际上，我们只需要把所有用到 gevent 的地方改成 tornado 实现就行了。

首先，我们要实现 watcher ，而且只需要 start 和 stop 函数（因为只用到了这两个函数）

这里的 start 函数只需要有一个功能，就是在在这里注册一个描述符(fd)，等待 event 的发生，然后调用这个回调函数，stop 就是清除这个

```
class Watcher(object):
    """
    这里传递过来的都是一些就绪的事件
    watcher 用来替换 libev 中的 watcher
    直接实例化一个 Watcher(fd, event) 对象，可以替换 greenify.pyx.wait_gevent 中的 hub.loop.io(fd, event)
    """
    def __init__(self, fd, event):
        self._fd = fd
        self._event = tornado.ioloop.IOLoop.READ if event == 1 else tornado.ioloop.IOLoop.WRITE  # 因为 greenify 中 libgreenify.c 只定义了两种事件
        self._greenlet = greenlet.getcurrent()
        self._parent = self._greenlet.parent
        self._ioloop = tornado.ioloop.IOLoop.current()
        self._callback = None
        self._args = None
        self._kwargs = None

    def start(self, callback, *args, **kwargs):
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
        self._ioloop.add_handler(self._fd, self._handle_event, self._event)

    def _handle_event(self, *args, **kwargs):
        self._callback(*self._args, **self._kwargs)

    def stop(self):
        # 到此为止，处理完一个io事件
        self._ioloop.remove_handler(self._fd)
```

然后还要实现 waiter 

```
class Waiter(object):
    def __init__(self):
        self._greenlet = greenlet.getcurrent()
        self._parent = self._greenlet.parent

    def switch(self, unique):
        # 把控制权限交给当前这个写程
        # 这个函数往往作为回调函数使用
        # 在gevent中，只有hub有资格调用这个函数
        # 在这里随便谁都可调用(其实也只有注册在tornado.ioloop中的callback可用调用)
        self._greenlet.switch(unique)

    def get(self):
        # 这里仅仅需要将控制权交给父协程
        # 当前协程就在本函数调用的地方开始挂起
        # 实际挂起时间是在return之前
        # 挂起之后，事件循环(这里指的是tornado的ioloop)会监听watcher中指定的描述符
        # 一旦可用描述符被执行完毕，会调用Watcher._handler_event，而正好，这里的callback参数就是Watier.switch
        # Waiter.switch会直接返回unique(其实会返回所有传入的参数，见greenlet.greenlet.switch注释)
        # 这个return值会直接返回到父greenlet中，而不管是否当前greenlet是否已经执行完。也就是直接返回到了get挂起的地方
        return self._parent.switch()

    def clear(self):
        self._greenlet = None
        self._parent = None
```

最后，再实现 spawn 实现就行了

```
class TorGreenlet(greenlet.greenlet):
    def __init__(self, run=None, *args, **kwargs):
        super(TorGreenlet, self).__init__()
        self._run = run
        self._args = args
        self._kwargs = kwargs
        self._future = tornado.gen.Future()

    def run(self):
        try:
            result = self._run(*self._args, **self._kwargs)
            self._future.set_result(result)
        except:
            exex_info = sys.exc_info()
            self._future.set_exc_info(exex_info)

    @classmethod
    def spawn(cls, callable_obj, *args, **kwargs):
        g = TorGreenlet(callable_obj, *args, **kwargs)
        # 调用switch，开始执行这个 greenlet
        # 在这个c-based-socket协程的执行中，如果遇到IOblock，会让出权限给root-greenlet，也就是主程序
        g.switch()
        return g._future


def spawn(callable_obj, *args, **kwargs):
    # 首先生成一个TorGreenlet对象g，然后执行其start函数
    # start函数会执行这里的 callable_obj ，这里我们的callable_obj会是一个C-based-Socket对象（因为本库也只对这个起作用）
    # greenify获取到这个socket，然后开始执行patch过的socket
    # 最终返回一个 Future 对象，让给 yield 解析
    return TorGreenlet.spawn(callable_obj, *args, **kwargs)
```

调用的时候，也跟 greenify 大同小异

```
import greenify
greenify.greenify()
from greenify import spawn
assert greenify.patch_lib("/usr/lib64/mysql/libmysqlclient_r.so")
c = yield spawn(Connect, args, kwargs)
```

项目地址在 [tornado-greenify](https://github.com/dantangfan/greenify)
