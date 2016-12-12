---
layout: post
title: 一次蛋疼的代码调试
description: 撸代码关一定要对语言特性十分熟悉啊，不然蛋碎得一地
category: blog
---

起因是这样的：公司的新游戏不久后就要上线了，做了一个疯狂的估计，那就是如果实时在线人数达到 50w 活动系统还能扛得住吗？

我们的实时活动系统，实际上也是一个日志收集系统。用户的日志（登录、购买、捐赠等日志）通过游戏服务器发送到实时活动系统，实时活动系统存储日志，并根据配置来把日志分发到相应的实时活动进程。缓存会每 3 分钟同步到数据库一次。

实时活动的大致流程是：日志进入 --> 读取当前用户缓存 --> 处理日志 --> 达成条件后发奖 --> 更新用户数据

50w 在线，假如平均在线时长 15 分钟，那么每分钟就有 50w / 900 大约 550 人登录；再者，如果产生日志的频率非常高，每个人 3 秒就产生一次日志，那美妙就有超过 15w 的日质量；其中，其中，任何一种日志都不可能超过总日志的 1/4 ，也就是 4w 左右，所以，每个实时活动进程每秒钟需要处理好 4w 条日志。

经过一些列的假设之后，我就开始对当前系统进行压力测试了。一开始测，马上就遇到问题了。现有的日志实时活动系统最多每秒钟也只能处理 1k（现有游戏高峰期实时在线也就万级别），这跟理想差距太大。并且这时候的内存、CPU 都不是很高，明显，应该就是代码的某个地方出问题了。

这个问题很容易就发现了，日志进入的时候会读取当前用户的缓存，如果缓存不存在就会去读取数据库，而我的开发机每秒也就只能查询 6k  次，同时，数据还在不断的写入，这样读取速度自然还会受影响。就算 0.3ms 读一次数据，代码普通逻辑运行 0.1ms(根本不可能运行那么久) 也至少应该有 2k+ 的处理速度，跟 1k/s 还有两倍的差距。不过，这里确实需要先优化，优化手段也很明显，就是读数据异步就行了：读缓存，把如果不存在，就把当前日志发送给读数据库的进程，进程读取完毕后，再把日志发回给实时活动进程。

一番折腾之后，把读数据多个一起读（mongodb 的 $in 查询），效果提高不少，读缓存成功的日志的平均处理时长达到了理想的 0.02ms 算下来，5w/s 的处理速度指日可待。又来一番测试之后，结果差强人意，在每秒日质量小的时候，可以处理大概 3k/s（这里记录的是每秒处理的日质量，而不是靠平均处理时长来反推），但是当日志量上去之后，比如每秒 1w 日志，处理速度居然降下来了。不仅如此，数据库的读写都越来越慢，前面还能 8k 次每秒的写数据，到后来居然每秒只能写几十个了，真是让人菊花一紧啊！于是就愤愤的以为是数据库出了问题。

我们知道，mongodb 处理数据更新的方式是先将数据写到内存，在一定情况下，才会将内存中的数据写入文件（sync操作）。读取也是，每次从文件中读取一块数据，如果查询的数据在内存中的命中率低，那就会不断的换出，影响查询速度。经过 iotop, top, mongostat, mongotop 的一番观察，发现在 sync 的时候，写数据缺失会骤降，甚至降到 0，虽然知道 sync 的时候会卡住，但是降到 0 还是挺惊悚的。于是，为了减少数据库操作，我又把写数据组合了一下，根据[这里](https://docs.mongodb.com/manual/reference/command/update/#dbcmd.update)，这样，原来的缓存写到数据库的每秒钟能写 6k 条，现在可以写 15k 左右。快是快了很多，但是问题依然没有解决，数据库操作还是会越来越慢，当时就懵逼了。

中途请假回了一趟四川，花了几天时间。回来蜗牛就开始催了，于是继续搞。终于发现，缓存写入数据库的进程变慢是由于消息堆积造成的，其实刚开始也想过，但并不觉得这是问题的所在点，因为数据库操作是同步耗时的，所以觉得是数据库操作变慢才造成的消息堆积。于是，将接受消息用[pobox](https://github.com/ferd/pobox)，问题终于得到了解决。数据库写入在 mongodb 自身不处于 sync 的情况下，总是能保持在 10k 以上，至此，每秒钟处理 4w 条日志的目标实现。

问题虽然处理好了，但是原因还是没搞清楚。于是继续想，我们知道在 erlang 按照优先级 receive 消息的时候，可能会造成消息堆积，因为消息队列中无法处理的消息将一直在队列中，那每次 receive 消息的时候都会遍历到这些无法处理的消息，所以消息越多自然就越卡了。但是。但是，这好像跟我的问题关系不大，因为我的进程是在运行中越来越慢，消息都还在 mailbox 里，根本没 receive 。

然后几番波折，终于发现忽略了一个小问题！忽略了数据库操作也是一个独立的 Genserver 进程，由于是从 Elixir 中慢慢的理解 erlang，概念不熟，才造成了这个问题。然后就去看了 OPT 的 [代码](https://github.com/erlang/otp/blob/maint-19/lib/stdlib/src/gen_server.erl#L365)，这里的 GenServer 的主循环中并没有出现 selective receive ，所以 Genserver 接收消息是不存在问题的。然后我们再看看调用呢，从 [这里](https://github.com/erlang/otp/blob/maint-19/lib/stdlib/src/gen_server.erl#L199) 进入到 [这里](https://github.com/erlang/otp/blob/maint-19/lib/stdlib/src/gen.erl#L155)，哈哈，始作俑者就在这里！首先，客户端进程不断的向 Server 发送 cast 请求，而 Server 这时候还卡在数据库处理，然后 mailbox 就变得很大；同时，Server 对数据库调用，等待 receive，这个 receive 是 selective receive，他需要遍历进程的 mailbox，然而这时候的 mailbox 非常大，所以整个进程都被拖慢了。

至此，整个问题解决。


在找 bug 的过程中，被一个 [stackoverflow上的一个问题](http://stackoverflow.com/questions/36216246/in-erlang-when-a-processs-mailbox-growth-bigger-it-runs-slower-why) 给误导了很久，一直以为我的问题跟这个类似。然而，这个问题我还是没有搞明白，这个问题的处理函数中，没有任何其他调用，都是普通的函数语句，为什么也会出现这种 mailbox 严重拖延处理时长的问题呢(虽然不如我那个问题严重)，然后用代码简单测试了一下

```elixir
defmodule Test do
  use GenServer
  require Record
  Record.defrecordp :state, [
    update_set: nil
  ]
  @table Test

  def sync(pid), do: GenServer.cast(pid, :sync)

  def send_message(_, 0), do: nil
  def send_message(pid, time) do
    do_send(pid)
    send_message(pid, time - 1)
  end

  def do_send(pid) do
    GenServer.cast(pid, {:msg, :hahahah})
  end

  def start_link() do
    GenServer.start_link(__MODULE__, [])
  end

  def init(_opts) do
    :ets.new(@table, [:set, :public, :named_table])
    update_set = Enum.reduce(1..100000, :sets.new(), fn i, acc ->
      :ets.insert(@table, {to_string(i), i})
      :sets.add_element(i, acc)
    end)
    {:ok, state(update_set: update_set)}
  end

  def handle_cast({:msg, msg}, state(update_set: update_set)) do
    update_set = :sets.add_element(msg, update_set)
    {:noreply, state(state, update_set: update_set)}
  end

  def handle_cast(:sync, state) do
    st = :erlang.system_time
    do_sync(state)
    et = :erlang.system_time
    IO.inspect("total time: #{(et-st)/1000000000}")
    {:noreply, state}
  end

  def do_sync(state(update_set: update_set)) do
    st = :erlang.system_time
    :sets.fold(fn i, {data, count} ->
      if count > 100 do
        :timer.sleep 10
        {[], 0}
      else
        {[i| data], count+1}
      end
    end, {[], 0}, update_set)
    et = :erlang.system_time
    IO.inspect((et-st)/1000000000)
  end
end
```

当堆积的消息从 10w 涨到 100w+ 的时候，do_sync 的时长明显增加。说明 mailbox 的增长确实对进程运行有影响，最终从 [这篇 Paper](http://www.fantasi.se/publications/ISMM02.pdf) 中找到了原因。在 section 3 中有说明 **每个进程有自己的 PCB，堆和栈。消息发送的时候，总是从一个进程把消息复制到另一个进程的堆中，然后会造成大量的内存碎片**

- High memory fragmentation – A process cannot utilize the memory (e.g., the heap) of another process even if there are large amounts of unused space in that memory area. This typically implies that processes can allocate only a small amount of memory by default. This in turn usually results in a larger number of calls to the garbage collector


至此，经历了一次十倍性能提升的优化。优化方案并不困难，但是在解决问题却花了很多时间，这一切都是由于对 Erlang 本身语言特性不够了解。从写 Elixir 开始了解 Erlang，在没有大量并发的时候几乎遇不到任何大问题，而且 Elixir 语法比起 Erlang 本身来说简直不能更舒爽。看来啊，Erlang 的坑还是得跳才行。。
