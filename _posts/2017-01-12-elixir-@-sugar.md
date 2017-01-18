---
layout: post
title: 用 Elixir 写一个装饰器
description: nil
category: blog
---

用多了 Python，始终觉得任何语言都该有装饰器这种便捷的语法糖。实际上 Elixir 也可以利用宏实现类似的功能，虽然并不那么常用。在实际工作中用到一些类似的功能，比如： cache、profile、log 等，都可以用 “装饰器” 的形式来实现，下面就简单的讲讲实现方法。

<!-- more -->

Elixir 模块属性有很多可以对编译代码做 trick。

#### @after_compile
会在当前模块编译之后调用，他接收一个 module 或者一个 {module, function atom} 形式的 tuple，如果只提供了一个 module ，那 function atom 就会默认为 `__after_compile__/2`，这个 function 会接收两个参数：env 和 bytecode，如下例子

```elixir
      defmodule M do
        @after_compile __MODULE__
        def __after_compile__(env, _bytecode) do
          IO.inspect env
        end
      end
```

#### @before_compie
会在当前模块编译之前调用，他接收一个 module 或者一个 {module, function/macro atom} 形式的 tuple，如果只提供了一个 module ，那 function/macro atom 就会默认为 `__before_compile__/1`。如果是个 macro，那么这个宏产生的数据就会被注入到当前模块的最后。

跟 after_compile 不一样的是，这里的 function/macro 必须在别的模块中。原因很简单：这个时候当前模块还么被编译，还不存在任何 function/macro。如下例子

```elixir
      defmodule A do
        defmacro __before_compile__(_env) do
          quote do
            def hello, do: "world"
          end
        end
      end
      defmodule B do
        @before_compile A
      end
```

#### @external_resource
有时候，我们需要根据外部文件数据来生成代码，当数据变化的时候，我们的代码就需要重新编译来保证正确性。比如所有 unicode 数据的转换和 MIME 类型的生成

#### @on_definition
会在每个 function/macro 被定义的时候被调用（确切的说，是定义好，但是还没有被放入到当前 module 中，也就是说，这个时候调用 Module.defines? 是会返回 false 的）。他接收一个 module 或者一个 {module, function atom} 形式的 tuple，如果只提供了一个 module ，那 function atom 就会默认为 `__on_definiation__/6`，他接收如下的六个参数

- the module environment
- kind: `:def`, `:defp`, `:defmacro`, or `:defmacrop`
- function/macro name
- list of quoted arguments
- list of quoted guards
- quoted function body

## 写个 "装饰器"

Elixir 代码在编译的时候是自上而下一层一层的将宏扩展开，于是我们要实现类似如下形式的语法，就需要在代码 on definiation 的时候将目标代码注入到 "被装饰" 的函数中。

我们的目标就是实现一个可以打印函数(为了简单，这里只装饰函数)执行时间的 "装饰器"，比如这样

```elixir
@time()
def func(), do: something()
```

首先，我们肯定需要在 on definiation 的时候重新定义当前 function。因为 on_definiation 是函数不是宏，不能生成代码。所以，也需要在 before compile 的时候将我们生成的代码注入到当前模块中。为了要记录我们需要重新生成哪些代码，就需要一个属性来记录我们要修改的内容。

所以 using 中需要有这些

```elixir
  defmacro __using__(_opts) do
    quote do
      import unquote(__MODULE__) # 这里是必要的
      Module.register_attribute(__MODULE__, :timed, accumulate: true)
      @on_definition unquote(__MODULE__)
      @before_compile unquote(__MODULE__)
    end
  end
```

然后需要在 on_definiation 中记录需要装饰的函数

```elixir
  defmodule Timed do
    defstruct [method_name: nil, args: nil, guards: nil, body: nil]
  end
  def __on_definition__(env, _kind, name, args, guards, body) do
    mod = env.module
    info = Module.get_attribute(mod, :time)
    if info do
      Module.put_attribute(mod, :timed,
        %Timed{
          method_name: name,
          args: args,
          guards: guards,
          body: body,
        }
      )
    end
    Module.delete_attribute(mod, :time)
```

后面再 before_compile 的时候就直接取出 :timed 属性中所有需要装饰的函数然后重新定义就行了

```elixir
  defmacro __before_compile__(env) do
    mod = env.module
    timed_methods = Module.get_attribute(mod, :timed)
    |> Enum.reverse()
    |> Enum.map(fn data ->
      Module.make_overridable(mod, [{data.method_name, length(data.args)}])
      body = build_body(cdata)
      if length(data.guards) > 0 do
        quote do
          def unquote(data.method_name)(unquote_splicing(data.args)) when unquote_splicing(data.guards) do
            unquote(body)
          end
        end
      else
        quote do
          def unquote(data.method_name)(unquote_splicing(data.args)) do
            unquote(body)
          end
        end
      end
    end)

    quote do
      unquote_splicing(timed_methods)
    end
  end
```

可以看出，这里就只需要定义一个 build_body 来生成目标函数了

```elixir
  def build_body(%Timed{}=data) do
    quote do
	  time_it() do
        unquote(data.body)
      end
    end
  end

  defmacro time_it(do: block) do
    quote do
      st = :erlang.system_time()
      res = unquote(block)
      et = :erlang.system_time()
      IO.inspect("#{et - st}")
      res
    end
  end
```

至此，就完成了一个简单的 "装饰器"
