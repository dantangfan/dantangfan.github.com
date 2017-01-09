---
layout: post
title: Elixir 宏里使用 bind_quoted 的坑
description: nil
category: blog
---

<!-- more -->

今天看 sf 的时候逛到这么个问题 [stackoverflow](http://stackoverflow.com/questions/34889369/elixir-macros-and-bind-quoted)，想起自己以前写宏代码生成的时候也遇到过奇葩的问题，具体怎样记不清了，或多或少跟这个有些相似。于是，我也很不建议在代码中随意使用 bind_quoted 操作。

bind_quoted 实际上做的工作很简单，比如代码

```
quote bind_quoted: [foo: foo] do
  IO.inspect foo
end
```

就直接搞成了

```
quote do
  foo = unquote(foo)
  IO.inspect foo
end
```

但是如果 foo 是个表达式的话，就会在这一步直接执行了，所以才会有你上面写的 Macro.escape，让表达式在bind_quoted中不执行。

那么，如果我有以下代码要生成

```elixir
defmodule Q do
  defmacro gen_func([do: code]) do
    quote do
      def new_fun() do
        unquote(code)
      end
    end
  end
end
defmodule T do
  require Q
  Q.gen_func do
    IO.inspect "hahahah"
  end
end
```

这个时候，需要 unquote 的是一段代码，于是就不能简单 bind_quoted, 一个可能的姿势是这样

```elixir
  defmacro gen_func([do: code]) do
    code = Macre.escape(code)
    quote bind_quoted: [code: code] do
      def new_fun() do
        unquote(code)
      end
    end
  end
```

但是我认为这样不太好，因为代码中的 code 是从 do: code, 中取出来的，此时的 code 已经是一个合法的 AST。经过 escape 然后 bind_quoted ，实际上什么都没变，所以如果要在 quote 中生成的函数里使用 code 代码，实际上还是需要再 unquote 一次，因为 def 生成函数的过程中，又进入了一块新的 AST，code 数据对他来说又是外部数据，所以也必须使用 unquote。

其次， bind_quoted 有个规则是默认关闭在 quote 中使用 unquote，除非设置 unquote: true。如果不加这个选项，就要一次性 unquote 出来所有需要的变量数据，然而混合使用感觉更不爽，特别是需要 unquote 数据比较多的时候，一些提前 unquote 了，一些又在中途 unquote，感觉更是奇怪。

大量的数据一次行就 bind_quoted 了，而不是在使用的时候再 unquote，还可能造成调试时候的 tracback 位置不对。

再次，bind_quoted 之后，quote 代码的中间产生的值不能对那些名字进行再绑定，原因不用解释。

而且，bind_quoted 还有些奇怪的行为。比如

```elixir
    defmodule Q do
      defmacro __using__([name: name]) do
        quote bind_quoted: [fun_name: name] do
          a = 1
          def fun_name do
            IO.inspect unquote(name)
          end
        end
      end
      defmacro mod(name) do
        quote bind_quoted: [name: name] do
          defmodule name do
            IO.inspect __MODULE__
          end
        end
      end
    end
    defmodule T do
      use Q, name: :fffffffffff
      require Q
      Q.mod Test
    end
```

上面的代码，生成 function 的bind_quoted没有生效，而生成module的bind_quoted 生效了的。

暂时就想到这么多
