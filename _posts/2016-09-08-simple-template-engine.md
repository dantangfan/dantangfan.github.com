---
layout: post
title: 一个简单的模板引擎
description: 一个简单的模板引擎
category: blog
---

接触 python web 框架，就少不了要鼓捣各种模板引擎。大部分 web 框架的 HTML 模板的实现，比如 tornado、flask 等，实现模板引擎的原理都大同小异，都是将模板代码在初始化时编译成可执行的 python 代码，在调用的时候传入相应的变量值，就可以替换掉模板中原有的对应变量。

想自己记录一下从中学到的简单原理只是，奈何书写功底实在太差，辛亏看到了一篇[很棒的文章](http://aosabook.org/en/500L/a-template-engine.html)，它的讲解让理解 HTML 模板变得出奇的简单。又可以 CTC 的搬运工了，下面直接抄重点。

<!-- more -->

{%raw%}

## 目标

文章实现的模板语法是基于 Django 的，实现了如下语法。

1. 数据使用双口号插入

```
    <p>Welcome, {{user_name}}!</p>
```

2. 数据的属性都统一由 `obj.attr` 来提供，不论他是一个函数还是变量

```
    <p>The price is: {{product.price}}, with a {{product.discount}}% discount.</p>
```

3. 可以用管道操符来让过滤函数处理数据

```
    <p>Short name: {{story.subject|slugify|lower}}</p>
```

4. 支持简单 if/for 的逻辑语句

```
    {% if user.is_logged_in %}
        <p>Welcome, {{ user.name }}!</p>
    {% endif %}
    <p>Products:</p>
    <ul>
    {% for product in product_list %}
        <li>{{ product.name }}: {{ product.price|format_price }}</li>
    {% endfor %}
    </ul>
```

5. 最后，可有可无，支持注释语句

```
    {# This is the best template ever! #}
```


## 实现方法

模板引擎主要包含两个阶段：解析模板、渲染模板。

渲染模板又包括

- 管理动态上下文和数据源
- 执行逻辑元素
- 实现点号 `.` 对属性的访问和管道对函数的调用

这里的关键是从解析模板阶段传递到渲染模板阶段的到底是什么东西，并且这个东西是可以渲染的。套用对其他编程语言的说法，这里有解析和编译两种方式。

在一个解释模型中，解析模板的过程产生一个可以表示模板的数据结构。而渲染阶段就会遍历这个数据结构，并根据相应的指令和数据来填充这个数据结构生成最终字符串。Django 的模板引擎就是使用的这种做法。

在一个编译模型中，解析阶段会产生可执行代码，渲染阶段直接传参调用这段代码。Tornado，Jinja2，Mako 都是使用的这种方式。本文要实现的也是编译模型的引擎。

## 编译到 Python

开始撸代码之前，我们先来看下最终效果是怎样。比如下面的 HTML 模板代码

```html
<p>Welcome, {{user_name}}!</p>
<p>Products:</p>
<ul>
{% for product in product_list %}
    <li>{{ product.name }}:
        {{ product.price|format_price }}</li>
{% endfor %}
</ul>
```

会生成如下的 Python 代码

```python
def render_function(context, do_dots):
    c_user_name = context['user_name']
    c_product_list = context['product_list']
    c_format_price = context['format_price']

    result = []
    append_result = result.append
    extend_result = result.extend
    to_str = str

    extend_result([
        '<p>Welcome, ',
        to_str(c_user_name),
        '!</p>\n<p>Products:</p>\n<ul>\n'
    ])
    for c_product in c_product_list:
        extend_result([
            '\n    <li>',
            to_str(do_dots(c_product, 'name')),
            ':\n        ',
            to_str(c_format_price(do_dots(c_product, 'price'))),
            '</li>\n'
        ])
    append_result('\n</ul>\n')
    return ''.join(result)
```

每个模板都会被编译成一个叫 `render_function` 的函数，并且接受一个 context 的数据字典。那些以 `c` 开头的变量就是从数据字典中取出来的代码运行过程中会使用到的属性、方法等，这么做的好处是优化代码的执行。因为每次访问 obj['key'] 的时候总是会先去对象里面查找这个属性然后再返回或者执行这个属性/方法，如果一段代码很多使用到这样的属性，那么预先把他取出来就节省了不少时间， append_result 和 extend_result 和 to_str 同样也是为了优化代码执行。

## 代码实现

### Templite class

模板引擎的核心就是这个 Templite 类（用 lite 表示轻量级、简化版的意思）。

我们可以使用模板代码来初始化一个 Templite 对象，然后使用 render 方法来将特性的上下文（数据字典）渲染到其中，就像下面这样。

```python
# Make a Templite object.
templite = Templite('''
    <h1>Hello {{name|upper}}!</h1>
    {% for topic in topics %}
        <p>You are interested in {{topic}}.</p>
    {% endfor %}
    ''',
    {'upper': str.upper},
)

# Later, use it to render some data.
text = templite.render({
    'name': "Ned",
    'topics': ['Python', 'Geometry', 'Juggling'],
})
```

可以看到，对象的构造函数也可以接受除了模板代码的其他参数。可以传入一些不会变动的数据、方法，这样动态渲染的时候就不用重复的传入相同的数据了。

在实现 Templite 类之前，我们需要实现一个辅助类 CodeBuilder

### CodeBuilder

我们的模板引擎是解析模板代码并生成 Python 代码，CodeBuilder 类的作用是记录代码生成的中间过程，并记录管理代码缩进。几句话不容易解释清楚，看代码就能一目了然。

一个 CodeBuilder 管理一个 Python 代码块，他可以是一个函数、一段for语句、一条赋值语句、甚至是一个嵌套的 CodeBuilder。每个 CodeBuilder 对象最终都可以输出一段代码，将这些代码按顺序组织在一起就是我们最终的 render_function。

初始化的时候，我们只需要知道他当前的缩进级别就行

```python
class CodeBuilder(object):
    """Build source code conveniently."""

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent
```

加入一行代码的时候，会自动的加入缩进和换行

```python

    def add_line(self, line):
        """Add a line of source to the code.

        Indentation and newline will be added for you, don't provide them.

        """
        self.code.extend([" " * self.indent_level, line, "\n"])
```

可以管理缩进级别

```python
    INDENT_STEP = 4      # PEP8 says so!

    def indent(self):
        """Increase the current indent for following lines."""
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        """Decrease the current indent for following lines."""
        self.indent_level -= self.INDENT_STEP
```

add_line 用于增加普通代码行，而 add_section 可以用来嵌套 CodeBuilder 对象(也就是嵌套代码块)

```python
    def add_section(self):
        """Add a section, a sub-CodeBuilder."""
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section
```

重载 `__str__` 方法让我们在输出代码的时候更简单（让普通的字符串和 CodeBuilder 有同样的输出字符串字面值的方法）

```python
    def __str__(self):
        return "".join(str(c) for c in self.code)
```

get_globals 产生最终的代码，他得到代码的字符串，并且编译出最终结果

```python
    def get_globals(self):
        """Execute the code, and return a dict of globals it defines."""
        # A check that the caller really finished all the blocks they started.
        assert self.indent_level == 0
        # Get the Python source as a single string.
        python_source = str(self)
        # Execute the source, defining globals, and return them.
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace
```

这里的 `exec` 是不那么常用的函数，它的作用是执行一段字符串形式的 Python 代码，并将所得到的全局变量放入到第二个参数中。例如

```python
python_source = """\
SEVENTEEN = 17

def three():
    return 3
"""
global_namespace = {}
exec(python_source, global_namespace)
```

然后 global_namespace['SEVENTEEN'] 就是 17，global_namespace['three'] 就是一个名为 three 的函数。

接下来就该是我们的 Templite 类了。

### Templite 的实现

编译和渲染工作都是在 Templite 里实现的

#### 编译

首先初始化模板，并保存初始化的上下文

```python
    def __init__(self, text, *contexts):
        """Construct a Templite with the given `text`.

        `contexts` are dictionaries of values to use for future renderings.
        These are good for filters and global values.

        """
        self.context = {}
        for context in contexts:
            self.context.update(context)
```

使用了 `*context` 进行传参，这样就可以传递多个 context 字典。于是下面几种写法都是有效的

```python
t = Templite(template_text)
t = Templite(template_text, context1)
t = Templite(template_text, context1, context2)
```

为了让代码执行速度尽可能的快，我们会吧编译后使用到的上下文环境变量在生成代码初期就取出来，同时，也需要跟踪生成代码的局部变量，比如循环变量。

```python
        self.all_vars = set()
        self.loop_vars = set()
```

稍后我们会看到，`all_vars - loop_vars` 就是我们需要从 context 中取出的变量。

生成代码过程中，首先，初始化用刚刚实现的 CodeBuilder 对象

```python
        code = CodeBuilder()

        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")
```

上面我们定义了函数名、增加了缩进，vars_code 用来站位，在遍历模板代码后，用于填充 `all_vars - loop_vars`。后面四句不用解释。

接下来，我们定义一个内部函数来帮我们输出每个代码块缓存的字符串

```python
        buffered = []
        def flush_output():
            """Force `buffered` to the code builder."""
            if len(buffered) == 1:
                code.add_line("append_result(%s)" % buffered[0])
            elif len(buffered) > 1:
                code.add_line("extend_result([%s])" % ", ".join(buffered))
            del buffered[:]
```

在模板代码遍历过程中，我们会把字符串存入到 buffer 中，当遇到各种标识符（比如 if 语句的开始和结束）都需要将当前 buffer 中的数据输出到 code 中。剩下的代码就是如何添加字符串到 buffer 中，何时将 buffer 中的字符串输出到 code。

理所当然的，我们需要一个栈来记录控制符（就像我们要实现一个简单计算器一样）

```python
        ops_stack = []
```

例如当我们碰到一个 `{\% if .. \%}` 标签，我们将 `if` 压入堆栈。当我们碰到一个 `{\% endif \%}` 标签时，我们再将之前的 `if` 弹出堆栈。如果栈顶没有 `if` 则报告错误。

初始化了那么久，下面才开始真正的解析模板。用一个牛逼的正则表达式来将模板的各个块划分

```python
tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)
```

比如一个下面这样的字符串

```bash
<p>Topics for {{name}}: {% for t in topics %}{{t}}, {% endfor %}</p>
```

会被划分成这样几个部分

```python
[
    '<p>Topics for ',               # literal
    '{{name}}',                     # expression
    ': ',                           # literal
    '{% for t in topics %}',        # tag
    '',                             # literal (empty)
    '{{t}}',                        # expression
    ', ',                           # literal
    '{% endfor %}',                 # tag
    '</p>'                          # literal
]
```

这正是我们想要的！！

然后我们就可以一次遍历每个 token，然后按条件处理了

```python
        for token in tokens:
            if token.startswith('{#'):
                # Comment: ignore it and move on.
                continue
            elif token.startswith('{{'):
                # An expression to evaluate.
                expr = self._expr_code(token[2:-2].strip())
                buffered.append("to_str(%s)" % expr)
```

上面，注释语句可以直接扔掉，然后 `{{` 开头的表达式，会传递给 `_expr_code` 处理，比如处理点操作符和管道操作符等，留到后面讲解。

```python
            elif token.startswith('{%'):
                # Action tag: split into words and parse further.
                flush_output()
                words = token[2:-2].strip().split()
```

这里我们就遇到了逻辑操作，遇到逻辑操作就要先将 buffer 中的数据 flush 出来。

```python
                if words[0] == 'if':
                    # An if statement: evaluate the expression to determine if.
                    if len(words) != 2:
                        self._syntax_error("Don't understand if", token)
                    ops_stack.append('if')
                    code.add_line("if %s:" % self._expr_code(words[1]))
                    code.indent()
```

如果是 if 语句，只会严格的包含两个参数（格式要求严），并且将操作 if 入栈，便于后续判断。

```python
                elif words[0] == 'for':
                    # A loop: iterate over expression result.
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error("Don't understand for", token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars)
                    code.add_line(
                        "for c_%s in %s:" % (
                            words[1],
                            self._expr_code(words[3])
                        )
                    )
                    code.indent()
```

如果是 for 操作，会稍微复杂点，`_variable` 方法会检查变量的合法性，并将其加入到对应的变量集合中。然后再代码中增加 for 循环并且提升缩进。

```python
                elif words[0].startswith('end'):
                    # Endsomething.  Pop the ops stack.
                    if len(words) != 1:
                        self._syntax_error("Don't understand end", token)
                    end_what = words[0][3:]
                    if not ops_stack:
                        self._syntax_error("Too many ends", token)
                    start_what = ops_stack.pop()
                    if start_what != end_what:
                        self._syntax_error("Mismatched end tag", end_what)
                    code.dedent()
```

如果遇到的是结束操作符，这里只有最后一行才有用（减少代码缩进），其他的都是检查代码错误的。

于是最后就只剩下普通的字符串了

```python
            else:
                # Literal content.  If it isn't empty, output it.
                if token:
                    buffered.append(repr(token))
```

这里使用 `repr` 实现了对字符串的引用，防止在生成的代码中出现未定义变量的问题（比如本该生成 append('pre')，结果生成了 append(pre)）。

这样，编译阶段的主干大部分代码就是如此。

```python
        if ops_stack:
            self._syntax_error("Unmatched action tag", ops_stack[-1])

        flush_output()
```

在代码的开始，我们创建了 vars_code 这个 section，也说明了这是用于后续取出 context 变量作文本地变量，比如

```html
<p>Welcome, {{user_name}}!</p>
<p>Products:</p>
<ul>
{% for product in product_list %}
    <li>{{ product.name }}:
        {{ product.price|format_price }}</li>
{% endfor %}
</ul>
```

这里就有 user_name、product 两个变量，他们都位于 `{{}}` 中，所以都在 all_vars 中，但是只有 user_name 会从 context 中取出，因为 product 也存在于 loop_vars 中。所以要有以下语句

```python
        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line("c_%s = context[%r]" % (var_name, var_name))
```

最后，就可以关闭代码了。

```python
        code.add_line("return ''.join(result)")
        code.dedent()
```

这时候，我们可以简单的获取到生成的函数

```python
		self._render_function = code.get_globals()['render_function']
```

#### 编译表达式

上面还有一个重要的方法 `_expr_code` 没有说到，它的作用是将括号中的表达式编译成 python 表达式。我们的模板表达式可能只是一个名字

```python
	{{user_name}}
```

也可能是一个复杂的序列包含属性访问和过滤器：

```python
{{user.name.localized|upper|escape}}
```

于是这个函数就需要处理好所有情况。我们知道一个通用的规则：大表达式都是由小表达式组成的。这里，一个完整的表达式由管道符分隔，其中第一部分是由逗号分隔的，后面只有管道，这样，我们就能用一个循环/递归处理。

```python
    def _expr_code(self, expr):
        """Generate a Python expression for `expr`."""
        if "|" in expr:
            pipes = expr.split("|")
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = "c_%s(%s)" % (func, code)
```

一共就只有两种情况，第一种是包含管道的表达式，这种表达式除了第一项之外，其他的都是函数，只需要分两步处理。第二种是不包含管道的，如果包含点号，那就把第一部分单独处理，后面的每个部分都作为第一个部分的对象属性处理，也就是 do_dots。

```python
        else:
            self._variable(expr, self.all_vars)
            code = "c_%s" % expr
        return code
```

最后再处理简单的没有任何操作的表达式。


### 渲染

渲染代码的过程，实际上就是执行生成的函数的过程

```python
    def render(self, context=None):
        """Render this template by applying it to `context`.

        `context` is a dictionary of values to use in this rendering.

        """
        # Make the complete context we'll use.
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)
```

这时候我们发现需要自己处理 `_do_dots` 函数

```python
    def _do_dots(self, value, *dots):
        """Evaluate dotted expressions at runtime."""
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value
```

在编译期间，一个模板表达式如x.y.z被转换为do_dots(x, 'y', 'z')。这个函数循环每个点后的名称，对每一个它先尝试是否是一个属性，不是的话再看它是否是一个字典的键。

实际上我们也可以直接将 do_dots 函数打包到生成的函数中而不用每次都传入。

## 结语

此时，一个简单的模板引擎就结束了，它还有很多地方需要完善

- 模板继承和包含
- 自定义标签
- 自动转码
- 复合逻辑 if/else
- 多个变量的循环

他们将有待于逐步完善

[代码地址](https://github.com/aosabook/500lines/blob/master/template-engine/code/templite.py)

{%endraw%}
