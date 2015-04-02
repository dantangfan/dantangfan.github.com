---
layout: post
title: Python Tornado学习
description: 这篇文章是对tornado官方入门文档的简单翻译，语句不通顺，但是至少还是可以读的。
category: blog
---

Tornado User Guide
---
#简介
Tornado是使用python编写的一个强大的，异步的web服务器，最初是由FriendFeed开发，在被Facebook收购之后得以开源。通过使用非阻塞模式，tornado可以接受巨大规模的连接（C10k问题，现在应该叫c10M问题了吧），这使得tornado非常适合长轮询、WebSockte、以及其他需要对每个用户保持长连接的应用。
Tornado可以简单的分为以下四个主要组件：
- 一个web框架（包含`RequestHandler`类，由它创建的子类可以建立web应用也可以作为web应用的支持类）
- HTTP的C/S模型实现（包含`HTTPServer`和`AsyncHTTPClient`等类）
- 一个用于构建HTTP协议或者其他协议异步网络库（`IOLoop`和`IOStream`）
- 一个取代链式调用从而能让异步代码更直观的携程库（`tornado.gen`）
Tornado的web框架和HTTP服务器为WSGI提供了一个完备的替代方案。虽然你也可以用tornado的web框架搭配其他的WSGI容器或者将其他WSGI的web框架放入tornado的HTTP服务器，但只有将tornado的web框架和HTTP服务器结合起来才能把tornado的威力发挥到极致。

#异步和非阻塞I/O
实时的web应用（如webQQ）都需要为每个用户提供一个多数时间被闲置的长连接。在传统的web服务器中，这就意味着要为每个用户提供一个线程，但对于成千上万的用户来说，这样的代价是十分昂贵的。
为了尽量减少并发所带来的成本，Tornado采用了单线程事件循环的方式。这就意味着在同一时间只能有进行一个操作，因此所有应用程序的代码都要采用异步和非阻塞的方式。

异步和非阻塞是非常相关的，我们也经常将两种术语互换使用，但实际上他们并不相同。
###阻塞
简单说就是：当一个进程在处理一个请求时，这个进程就会被挂起直到请求完成。阻塞的原因有很多：网络I/O、磁盘I/O、互斥等。实际上每个进程在运行和使用CPU的时候或多或少都会有一段时间的阻塞（举个极端的例子来说明为什么对待CPU阻塞要和对待一般阻塞一样的严肃：诸如`bcrypt`的密码散列函数需要消耗几百毫秒的CPU时间，这已经远远超过了一般的网络或磁盘访问时间。）
一个程序在不同的时候可以阻塞或者非阻塞。比如说`tornado.httpclient`默认在DNS解析的时候阻塞，在其他时候不阻塞。这里我们只考虑Tornado环境下网络I/O的阻塞过程，Tornado已经把各种阻塞都最小化了。
###异步
异步函数在结束之前就会返回，通常在出发下一个程序之前会在后台执行一些工作（传统的同步程序总是在返回之前就做完了所有工作）。这里列举几种不同类型的异步接口：
- 回调参数（Callback argument）
- 返回一个站位符（Return a placeholder）
- 发送到一个队列（Deliver to a queue）
- 回调注册表（Callback registry）
无论是何种类型的接口，异步函数顾名思义跟他的调用者在交互方面有所不同；也没有一种对调用者透明的方式让非阻塞函数变得阻塞（虽然如gevent等使用轻量级线程的系统性能可以与异步系统媲美，但实际上它并没有将事情异步化）。

###例子

一个简单的同步函数

```pyhon
from tornado.httpclient import HTTPClient
def synchronous_fetch(url):
    http_client = HTTPClient()
    response = http_client.fetch(url)
    reponse.body
```

把上面例子写成回调参数类型的异步函数如下

```python
from tornado.httpclient import AsyncHTTPClient
def asynchronous_fetch(url, callback):
    http_client = AsyncHTTPClient()
    def handle_response(response):
        callback(response.body)
    http_client.fetch(url, callback=handle_response)
```

写成带`Future`的异步函数如下

```python
from tornado.concurrent import Future
def async_fetch_future(url):
    http_client = AsyncHTTPClient()
    my_future = Future()
    fetch_future = http_client.fetch(url)
    fetch_future.add_done_callback(
        lambda f: my_future.set_result(f.result()))
    return my_future
```

`Future`版本的明显更复杂也更难理解，但它却是Tornado中推荐的写法，因为它有两个明显的优势。首先，错误处理比较一致，因为`Future.result`可以抛出异常；其次，`Futures`很适合跟协程一起使用。后面将会详细讨论协程的用法，这里给出上面例子的协程版本

```python
from tornado import gen
@gen.coroutine
def fetch_coroutine(url):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    return response.body
```

#协程
Tornado推荐使用协程来写异步代码，协程通过使用`python`的*`yield`*关键字来代替链式调用从而挂起和恢复进程。用协程方式写的代码就跟同步代码一样简单但却没有像同步一样浪费一个线程，通过减少上下文切换，协程更使得并发更加容易。
比如
```python
from tornado import gen
@gen.coroutine
def fetch_coroutine(url):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    return response.body
```

###代码是如何工作的呢
包含*`yield`*关键字的函数叫生成器。所有的生成器都是异步的；当被调用的时候它们会返回一个生成器对象而不是直接执行完毕。`@gen.coroutine`装饰器通过返回一个`Future`来跟生成器和协程代码的调用者通信，下面是一个协程装饰内部循环的简化版本
```python
# Simplified inner loop of tornado.gen.Runner
def run(self):
    # send(x) makes the current yield return x.
    # It returns when the next yield is reached
    future = self.gen.send(self.next)
    def callback(f):
        self.next = f.result()
        self.run()
    future.add_done_callback(callback)
```

装饰器接收到一个来自生成器的`Future`并等待`Future`执行完毕，然后“解析”这个`Future`并将结果发回给生成器作为*`yield`*表达式的结果。除了需要立即把异步函数返回的`Future`传递给*`yield`*之外，大多数的异步代码不会直接接触到`Future`类。

###协程模式
####与回调相互作用
为了能与使用回调的异步代码相互作用，我们需要把调用包装在一个task中
```python
@gen.coroutine
def call_task():
    # Note that there are no parens on some_function.
    # This will be translated by Task into
    #   some_function(other_args, callback=callback)
    yield gen.Task(some_function, other_args)
```

####调用阻塞函数
最简单的方法就是使用一个能与协程媲美的`ThreadPoolExecutor`，它能返回`Futures`
```python
thread_pool = ThreadPoolExecutor(4)
@gen.coroutine
def call_blocking():
    yield thread_pool.submit(blocking_func, args)
```

####并行
协程装饰器可以识别值为`Future`的list或者dict，并并行的等待他们的完成
```python
@gen.coroutine
def parallel_fetch(url1, url2):
    resp1, resp2 = yield [http_client.fetch(url1),
                          http_client.fetch(url2)]
@gen.coroutine
def parallel_fetch_many(urls):
    responses = yield [http_client.fetch(url) for url in urls]
    # responses is a list of HTTPResponses in the same order
@gen.coroutine
def parallel_fetch_dict(urls):
    responses = yield {url: http_client.fetch(url)
                        for url in urls}
    # responses is a dict {url: HTTPResponse}
```

####Interleavin
有时候暂时保存一个`Future`而非直接yielding它也很有用，这样一来就可以在等待之前启动另一个操作
```python
@gen.coroutine
def get(self):
    fetch_future = self.fetch_next_chunk()
    while True:
        chunk = yield fetch_future
        if chunk is None: break
        self.write(chunk)
        fetch_future = self.fetch_next_chunk()
        yield self.flush()
```

####循环
在协程中使用循环很棘手，因为python没有提供好的办法在for或者while循环中直接使用yield。
```python
import motor
db = motor.MotorClient().test
@gen.coroutine
def loop_example(collection):
    cursor = db.collection.find()
    while (yield cursor.fetch_next):
        doc = cursor.next_object()
```

#Tornado web应用的结构
一个Tornado应用总是会包含一个或多个`RequestHandler`的子类、一个将请求传入Handler的`Application`对象和一个用来启动应用的`main()`函数。
一个最简单的**Hello word**实例如下
```python
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
class HelloHandler(RequestHandler):
    def get(self):
        self.write("Hello, world")
def make_app():
    return Application([
        url(r"/", HelloHandler),
        ])
def main():
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()
```

###`Application`对象
**Application**对象负责全局配置，同时也包含了一个映射请求处理的路由表。
映射请求路由表是以`URLSpec`对象（每个是一个tuple）为元素的list，每个tuple包含一个正则表达式和一个处理请求类。如果正则表达式中包含了捕获组，那么这些组将作为路径参数传递给处理程序的HTTP方法。如果包含一个字典作为`URLSpec`的第三个元素，那么这个字典将作为参数传递给`RequestHandler.initialize`。`URLSpec`也可以有名字，这样它就可以保被`RequestHandler.reverse_url`使用。
在下面这个例子中，根URL被映射到MainHandler，/story/后面接数字的URL被map到StoryHandler，数字会以字符串的形式被`StoryHandler.get`捕获
```python
class MainHandler(RequestHandler):
    def get(self):
        self.write('<a href="%s">link to story 1</a>' %
                   self.reverse_url("story", "1"))
class StoryHandler(RequestHandler):
    def initialize(self, db):
        self.db = db
    def get(self, story_id):
        self.write("this is story %s" % story_id)
app = Application([
    url(r"/", MainHandler),
    url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
    ])
```

`Application`类的构造函数可以接收很多参数用于自定义子类的行为。

###`RequestHandler`的子类
Tornado中，大部分工作是通过这些子类完成的，主要的处理函数是用HTTP方法命名的：**get()/post()**等等，每个类可以定义一个或多个这样的方法来处理不同的HTTP请求，这些方法将根据前面所说的路由表一一对应，并捕获传入的参数。
在一个Handler中，我们通过调用`render()`,`write()`等函数来作为请求的响应。`render()`返回一个template（网页）和一系列相关参数给客户端；`write()`直接返回字符串、字节码、字典（作为JSON数据）。
`RequestHandler`中的许多方法都是被设计来让子类重写以便于应对相应的web应用。常规的做法是定义一个`BaseHandler`类，并在该类中重写诸如`write_error()`,`get_current_user()`等方法，其他的类都继承这个类。
###处理输入请求
请求处理程序可以通过`self.request`访问当前处理请求，详细信息在`HTTPServerRequest`类中。
HTML表单格式的请求可以通过`get_query_argument`/`get_body_argument`访问到。
```python
class MyFormHandler(RequestHandler):
    def get(self):
        self.write('<html><body><form action="/myform" method="POST">'
                   '<input type="text" name="message">'
                   '<input type="submit" value="Submit">'
                   '</form></body></html>')
    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_body_argument("message"))
```

由于HTML编码是不明确的而且不知道出入的参数到底是单个值还是以list，于是`RequestHandler`提供了不同的方法来判定如何处理，利用`get_query_argument`/`get_body_argument`就可以处理list

上传的文件可以以表单的形式通过`self.request.file`访问，它通过名字（在html中<input type='file'>表单的名称）映射到一系列的文件，每个文件有如下的字典形式**{"filename":..., "content_type":..., "body":...}**。`file`对象只有当文件是以form表单形式上传的时候才会存在，如果不是form形式，那么原始的文件列表可以通过`self.request.body`访问到。默认情况下，上传的文件会暂存在内存中，文件过大的情况可以在`stream_request_body`装饰器中看到。

由于HTML怪异的编码格式，tornado并不统一输入参数的格式。特别的是，我们也不会解析JSON请求的主体，需要使用JSON的应用程序会重写`prepare`来解析请求
```python
def prepare(self):
    if self.request.headers["Content-Type"].startswith("application/json"):
        self.json_args = json.loads(self.request.body)
    else:
        self.json_args = None
```

###重写`RequestHandler`的方法
有时候，为了实现更多更复杂的基本HTML方法（get、post等），需要重写某些定义在`RequestHandler`中的函数。对于每个请求，都会顺序的发生以下事件：
1. 每个请求都会产生一个新的`RequestHandler`对象
2. 从`Application`中传入参数到初始化函数`initialize`，通常，初始化函数都值保存传入的参数，而不会有任何诸如`send_error`的输出。
3. 调用`prepare()`.由于任何HTTP方法的使用都需要调用这个函数，所以这个被放在基类中的函数是最有用的。这个函数有可能产生输出；如果它调用了`finish`，那么程序就在这里结束了。
4. 某个HTTP方法被调用（get/post/head）
5. 请求结束时，调用`on_finish()`。在同步的情况下，`get()`方法一旦return就会执行这个过程，异步的时候只有执行`finish()`之后才会执行这个过程

在`RequestHandler`的文档中我们可以看到所有能被重写的方法，其中最常用的几个如下
- `write_error`，输出访问错误页面的HTML
- `on_connection_close`，客户端断开链接的时候调用。应用程序可以选择检测到这种情况并停止处理程序，但并不保证在关闭连接的时候能迅速的检测到。
- `get_current_user`，在用户认证的时候有用
- `get_user_locate`，返回当前用户的`locate`对象
- `set_default_headers`，用于增加额外的返回头信息

###错误处理
如果一个程序抛出一个错误，tornado将调用`RequestHandler.write_error`来调用一个错误页面。`tornado.web.HTTPError`可以用来生成一个指定的状态码，所有其他的错误状态返回500。
默认的错误页面包含在调试模式下的堆栈跟踪和一行错误的说明。为了生成一个错误页面，可以重写`RequestHandler.wriet_error`（可以放在自定义base类中）。通过调用这个方法，可以由如`write()`和`render()`产生正常输出。如果错误是由异常引起的，一个`exc_info`三将传递一个关键字参数（注意，此异常不能保证当前异常的`sys.exc_info`，所以`write_error`必须使用`traceback.format_exc`的如`traceback.format_exception`代替）。
另外，也可以通过调用`set_status`，写一个响应，并返回生成的正规处理方法。
对于404错误，应该使用default_handler_class，这个操作需要重写`prepare`方法而不是`get()`等其他方法，这样一来就可以在任何HTTP请求中调用。我们可以通过抛出`HTTPError(404)`并重写`write_error`或者直接调用`self.set_status(404)`并且直接在`prepare()`中写出处理程序。

###重定向
通常有两种办法可以实现重定向，它们分别是`RequsetHandler.rediret`和`RediretHandler`。你可以在`RequestHandler`类的方法中使用`self.rediret()`把当前用户重定向到任何路径，此外，还有一个可选参数`permanent`用于永久性的重定向，它的默认值是`False`，这将产生一个`302Found`的HTTP状态码，这非常适用于相应post请求。如果`permanent`的值是`True`，将返回`301  Moved Permanently`HTTP状态码，这对把一个对SEO友好的页面重定向到目标页面非常有用（比如说google.com被重定向到google.com.hk）。
`RedirectHandler`可以让你直接在`Application`中配置路由表，如下是一个单一静态重定向
```python
app = tornado.web.Application([
    url(r"/app", tornado.web.RedirectHandler,
        dict(url="http://itunes.apple.com/my-app-id")),
    ])
```

它同样支持正则表达式
```python
app = tornado.web.Application([
    url(r"/photos/(.*)", MyPhotoHandler),
    url(r"/pictures/(.*)", tornado.web.RedirectHandler,
        dict(url=r"/photos/\1")),
    ])
```

跟`redirect()`不一样的是，`RedirectHandler`默认就是使用永久重定向。原因是路由表不会在运行时改变，所以重定向的发生最大可能性就是处理逻辑发生了改变。想要进行非永久性重定向，只需要在`RedirectHandler`的初始化函数中将`permanent=False`就行了。

###异步处理程序
Tornado的处理程序默认都是同步的：当get()/post()返回时，我们就任务请求结束了，于是马上响应客户端。由于在处理器处理一个程序的时候，其他所有的程序都会被阻塞，所以为了能让程序非阻塞的调用某些缓慢的操作，任何长时间运行的程序都应该写成异步的。
让程序异步最简单的方式就是使用`coroutine`装饰器(如前面所说)，但在某些情况下协程可能不是很能胜任，这个时候就需要使用回调的方式，于是`tornado.web.asynchronous`装饰器就可以发挥作用了。如下是一个使用`AsyncHTTPClient`调用FriendFeed API的例子：
```python
class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch("http://friendfeed-api.com/v2/feed/bret",
                   callback=self.on_response)
    def on_response(self, response):
        if response.error: raise tornado.web.HTTPError(500)
        json = tornado.escape.json_decode(response.body)
        self.write("Fetched " + str(len(json["entries"])) + " entries "
                   "from the FriendFeed API")
        self.finish()
```

当get()函数返回的时候，请求并没有结束；当调用on_response()的时候，请求仍在继续。只有在调用了self.finish()之后，请求才真正的结束。
下面将上面代码改写成协程的形式
```python
class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        response = yield http.fetch("http://friendfeed-api.com/v2/feed/bret")
        json = tornado.escape.json_decode(response.body)
        self.write("Fetched " + str(len(json["entries"])) + " entries "
                   "from the FriendFeed API")
```

Tornado源代码实例中**Chat**的那个例子更好的展现了异步调用过程，同时也使用了AJAX和长轮询的推送技术。使用长轮询的用户需要重写`on_connection_close()`方法来进行连接技术之后的善后处理(重写时最好看下文档中的注意事项)。

#模板和UI
Tornado提供了一个简单、快速、灵活的模板语言。下面将简单介绍这套语言和它的相关问题，比如说国际化问题。
Tornado也可以与任何其他模板语言结合使用，但`RequestHandler.render`中并没有提供相应的处理标准。所以我们可以将模板字符串直接传递给`RequestHandler.write`输出。

###配置模板
默认情况下，tornado会在当前文件夹下面虚找模板文件。为了方便，我们可以将模板文件单独存放在一个文件夹，于是我们需要用到`template_path`（如果对不同的处理函数有不同的模板文件夹，就需要重写`RequestHandler.get_template_path`）。如果模板不是来自于当前文件系统的位置，就需要继承`tornado.template.BaseLoader`并传递一个`template_loader`实例给应用程序设置(也就是Application类的初始化参数)。
编译好的模板默认情况下会被缓存，想要实时的看到模板发生的改变就需要关闭缓存，可以在设置中加入`compiled_template_cache=False`或者`debug=True`

###模板语法
模板仅仅是嵌入python控制程序和标志的HTML表达式，因此很简单。
```html
<html>
   <head>
      <title>{{ title }}</title>
   </head>
   <body>
     <ul>
       {% for item in items %}
         <li>{{ escape(item) }}</li>
       {% end %}
     </ul>
   </body>
 </html>
```

将上面代码保存成template.html并放在.py文件的目录下， 通过下面代码就可以调用。
```python
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("template.html", title="My title", items=items)
```

Tornado的模板支持控制语句和表达式：控制语句用**{% statement %}**,表达式用**{{ var }}**。控制语句支持*if*,*for*,*while*,*try*等，每个完整的控制语句最后都需要使用*{% end %}*。同时，tornado也支持`extends`和`block`语句用于模板拓展(`tornado.template`中有详细描述)。
表达式可以是任何的python表达式，连函数调用都可以。
模板代码通常在命名空间中执行，空间中包含了以下对象和函数（适用于`RequestHandler.render`和`render_string`）
 -   escape: alias for tornado.escape.xhtml_escape
 -   xhtml_escape: alias for tornado.escape.xhtml_escape
 -   url_escape: alias for tornado.escape.url_escape
 -   json_encode: alias for tornado.escape.json_encode
 -   squeeze: alias for tornado.escape.squeeze
 -   linkify: alias for tornado.escape.linkify
 -   datetime: the Python datetime module
 -   handler: the current RequestHandler object
 -   request: alias for handler.request
 -   current_user: alias for handler.current_user
 -   locale: alias for handler.locale
 -   _: alias for handler.locale.translate
 -   static_url: alias for handler.static_url
 -   xsrf_form_html: alias for handler.xsrf_form_html
 -   reverse_url: alias for Application.reverse_url
 -   All entries from the ui_methods and ui_modules Application settings
 -   Any keyword arguments passed to render or render_string

编写一个web应用的时候，我们通常需要用到tornado的很多特性，尤其是模板的拓展功能。我么可以在`tornado.template`中查看这些特性(有些特性，比如`UIModules`是在`tornado.web`中实现的)。
所有的输出都是默认转义的（使用`tornado.escape.xhtml_excape`），我们可以在设置的时候使用`autoescape=None`,或者直接在模板文件中使用`{% autoescape=None %}`,对单一语句不转义，可以用`{% raw ...%}`代替`{{ }}`。

###本地化
当前用户(无论是否登录)的语言环境总会作为请求头发送给服务器，并能从`self.location`访问。地点的名称可以通过`locate.name`访问到，可以使用`Locate.translate`来翻译传入的字符串。模板也提供了全局函数`_()`来翻译字符串，它一般有两种调用形式：
直接根据当前语言环境翻译
```python
_("Translate this string")
```

根据传入的第三个参数局定是单数韩式复数
```python
_("A person liked this", "%(num)d people liked this",
  len(people)) % {"num": len(people)}
```

在这个例子中，如果`len(people)`的值是1,就会直接输出第一句话，如果不是就会输出第二句话。最常见的翻译模式就是使用python的站位符(%(num)d)，因为站位符可以在运行时变化。
比如下面有个常见的例子
```html
<html>
   <head>
      <title>FriendFeed - {{ _("Sign in") }}</title>
   </head>
   <body>
     <form action="{{ request.path }}" method="post">
       <div>{{ _("Username") }} <input type="text" name="username"/></div>
       <div>{{ _("Password") }} <input type="password" name="password"/></div>
       <div><input type="submit" value="{{ _("Sign in") }}"/></div>
       {% module xsrf_form_html() %}
     </form>
   </body>
 </html>
```

默认情况下，tornado会通过浏览器发送的请求检测用户的语言环境，当找不到合适的语言的时候会选择英语（**en_US**）。如果让用户自由的定义自己的语言偏好，那么可以重写`RequestHandler.get_user_locate()`函数 
```python
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return self.backend.get_user_by_id(user_id)
    def get_user_locale(self):
        if "locale" not in self.current_user.prefs:
            # Use the Accept-Language header
            return None
        return self.current_user.prefs["locale"]
```

语言偏好之类的不会太常用。需要的时候可以自己查看`tornado.locate`

###UI modules
Tornado支持UI模块，从而让前端代码重用变得可能。比如你正在实现一个博客，你希望能在多个页面上有博客条目功能，那么你就可以实现一个提供显示博客条目功能的模块，并嵌入到这些个页面中。首先，为你的UI modules创建一个python模块（uimodules.py）：
```python
class Entry(tornado.web.UIModule):
    def render(self, entry, show_comments=False):
        return self.render_string(
            "module-entry.html", entry=entry, show_comments=show_comments)
```

接下来只需要在设置中使用UI modules就行了
```python
from . import uimodules
class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY date DESC")
        self.render("home.html", entries=entries)
class EntryHandler(tornado.web.RequestHandler):
    def get(self, entry_id):
        entry = self.db.get("SELECT * FROM entries WHERE id = %s", entry_id)
        if not entry: raise tornado.web.HTTPError(404)
        self.render("entry.html", entry=entry)
settings = {
    "ui_modules": uimodules,
}
application = tornado.web.Application([
    (r"/", HomeHandler),
    (r"/entry/([0-9]+)", EntryHandler),
], **settings)
```

然后在模板中，可以通过`module`来调用模块
```html
{% for entry in entries %}
  {% module Entry(entry) %}
{% end %}
```

通过重写`embedded_css`/`embedded_javascript`/`javascript_files`/`css_files`我么可以在模板中使用css和js
```python
class Entry(tornado.web.UIModule):
    def embedded_css(self):
        return ".entry { margin-bottom: 1em; }"
    def render(self, entry, show_comments=False):
        return self.render_string(
            "module-entry.html", show_comments=show_comments)
```

不过模块被调用多少次，js和css都只会被包含一次，这样就避免了冲突。css通常包含在`<head>`标签中，js通常在`</body>`结束之前。
不用额外的python代码也可以将一个template代码转换称为module，比如前面的例子可以重写成下面module-entry.html代码
```html
{{ set_resources(embedded_css=".entry { margin-bottom: 1em; }") }}
<!-- more template html... -->
```

我们可以使用下面代码调用它
```html
{% module Template("module-entry.html", show_comments=True) %}
```

#认证和安全
###cookie和secure cookie
我们可以在用户的浏览器中通过`set_cookies`设置cookie
```python
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("mycookie"):
            self.set_cookie("mycookie", "myvalue")
            self.write("Your cookie was not set yet!")
        else:
            self.write("Your cookie was set!")
```

普通的cookie并不安全，可以通过浏览器修改。如果想用cookie来确定当前登录的用户，就需要为cookie打标签来防止伪造。Tornado提供了`get_secure_cookie`和`set_secure_cookie`两个方法，只需要在应用的设置中添加`cookie_secret=value`就可以使用了。
```python
application = tornado.web.Application([
    (r"/", MainHandler),
], cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__")
```

签名后的cookie包含有编码后的时间戳和HMAC签名。如果cookie国企或者不匹配，`get_security_cookie`就会返回None。
```python
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("mycookie"):
            self.set_secure_cookie("mycookie", "myvalue")
            self.write("Your cookie was not set yet!")
        else:
            self.write("Your cookie was set!")
```

默认情况下，*Secure_cookie*会保存30天，我们可通过设置`set_secure_cookie()`的`expires_days`参数和`max_age_days`参数来修改默认值。这两个值支队当前的cookie发挥作用，这样一来，我们可以让普通的cookie有效期为30天，而让某些特殊的cookie作用期更短/长。

###用户认证
已经认证过的用户可以通过`self.current_user`访问到，在模板中通过`current_user`访问到，但在默认情况下，`current_user=None`。
为了在你的应用中实现用户认证，你需要重写`get_current_user()`方法来通过cookie等值决定当前用户如下就是简单使用cookie 认证的简单方法
```python
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)
class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')
    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
], cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__")
```

我们可以通过`tornado.web.authenticated`装饰器来保证一个用户已经登录。使用这个装饰器之后，如果一个没有登录的用户要进行该操作，这个用户就会被重定向到登录页面，如下：
```python
class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)
settings = {
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    "login_url": "/login",
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
], **settings)
```

如果post()函数使用了这个装饰器，一旦被没登录的用户调用，就会返回一个`403`的状态码。
我们可以在tornado实例中的`Blog`例子中看到更复杂的使用方法。

###第三方登录认证
`tornado.auth`模块已经实现了一些流行网站的身份认证和授权协议，比如说google、facebook、twitter等（很遗憾，大天朝都不能用），需要自己实现国内认证功能

###防止CSRF
任何Web应用所面临的一个主要安全漏洞是跨站请求伪造，通常被简写为CSRF或XSRF，发音为"sea surf"。这个漏洞利用了浏览器的一个允许恶意攻击者在受害者网站注入脚本使未授权请求代表一个已登录用户的安全漏洞。
有很多预防措施可以防止这种类型的攻击。首先你在开发应用时需要深谋远虑。任何会产生副作用的HTTP请求，比如点击购买按钮、编辑账户设置、改变密码或删除文档，都应该使用HTTP POST方法。但是，这并不足够：一个恶意站点可能会通过其他手段，如HTML表单或XMLHTTPRequest API来向你的应用发送POST请求。保护POST请求需要额外的策略。
为了防范伪造POST请求，我们会要求每个请求包括一个参数值作为令牌来匹配存储在cookie中的对应值。我们的应用将通过一个cookie头和一个隐藏的HTML表单元素向页面提供令牌。当一个合法页面的表单被提交时，它将包括表单值和已存储的cookie。如果两者匹配，我们的应用认定请求有效。
由于第三方站点没有访问cookie数据的权限，他们将不能在请求中包含令牌cookie。这有效地防止了不可信网站发送未授权的请求。tornado通过在设置中加入`xsrf_cookies=True`字段来预防xsrf
```python
settings = {
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    "login_url": "/login",
    "xsrf_cookies": True,
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
], **settings)
```

设置好这个字段之后，tornado的web应用会为每个用户设置`_xsrf`的cookie，并且会拒绝所有不包含正确的_xsrf值的请求(包括post，get，put，delete等)。如果我们设置了这个字段，就需要对所有通过post提交的form表单进行设置，这个设置是通过UI Module中的`xsrf_from_html()`来实现的，这个函数在所有的template中都能访问到。
```html
<form action="/new_message" method="post">
  {% module xsrf_form_html() %}
  <input type="text" name="message"/>
  <input type="submit" value="Post"/>
</form>
```

当使用AJAX进行post方法数据请求时，也需要保证每个javascript都带有正确的_xsrf值，对jQuery来说，可以有如下例子
```javascript
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
        callback(eval("(" + response + ")"));
    }});
};
```

如何建立安全的web应用是一个说不完的话题，但这并不是tornado主要特点，所以我们不多讨论。

#运行和部署
由于tornado本身就能提供web server的功能，所以它跟一般的web框架部署方法有所不同：我们并不需要配置一个专门的WSGI容器，只需要写一个`main()`函数并执行，就能启动这个web服务器。
```python
def main():
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()
if __name__ == '__main__':
    main()
```

###进程和端口
由于python有GIL的限制，要运行多个python进程实例就需要充分利用多核，也就是说每个cpu值跑一个python进程。Tornado有一套内置的多进程模式，只需要稍微修改main函数就能实现
```python
def main():
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(8888)
    server.start(0)  # forks one process per cpu
    IOLoop.current().start()
```

这就是使用多进程共享同一个端口号的最简单的实现方式，但它有一定的缺陷。首先，每个子进程都有自己的IOLoop，在fork之前，不可以触发全局的IOLoop实例；其次，这个实例很难实现零停机时间的更新；最后，由于所有进程共享一个端口，要监视单个进程就变得十分困难。
对更复杂的部署方式，强烈建议每个进程单独启动，并且监听不同的端口。一个好的办法是使用` supervisord `的’进程组‘功能。当每个进程监听不同端口的时候，通常需要一个负载均衡工具（如nginx等）来平衡每个进程上面的请求数量。

###如何在负载均衡器下运行
当使用负载均衡工具的时候，建议传递参数`xheaders=True`给`HTTPServer`的构造函数。这句话的目的是告诉tornado使用类似`X-real-IP`的报头来获取真是的UserIp。下面列表是一个Nginx配置的示例。他类似与FriendFeed的配置，并假设nginx和tornado都运行在同一台机器上面，并且tornado监听了8001-8003几个端口。
```nginx
user nginx;
worker_processes 1;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;
events {
    worker_connections 1024;
    use epoll;
}
http {
    # Enumerate all the Tornado servers here
    upstream frontends {
        server 127.0.0.1:8000;
        server 127.0.0.1:8001;
        server 127.0.0.1:8002;
        server 127.0.0.1:8003;
    }
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    access_log /var/log/nginx/access.log;
    keepalive_timeout 65;
    proxy_read_timeout 200;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    gzip on;
    gzip_min_length 1000;
    gzip_proxied any;
    gzip_types text/plain text/html text/css text/xml
               application/x-javascript application/xml
               application/atom+xml text/javascript;
    # Only retry if there was a communication error, not a timeout
    # on the Tornado server (to avoid propagating "queries of death"
    # to all frontends)
    proxy_next_upstream error;
    server {
        listen 80;
        # Allow file uploads
        client_max_body_size 50M;
        location ^~ /static/ {
            root /var/www;
            if ($query_string) {
                expires max;
            }
        }
        location = /favicon.ico {
            rewrite (.*) /static/favicon.ico;
        }
        location = /robots.txt {
            rewrite (.*) /static/robots.txt;
        }
        location / {
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_pass http://frontends;
        }
    }
}
```

###静态文件和文件缓存
可以使用`static_path`来告诉tornado静态文件的位置
```python
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    "login_url": "/login",
    "xsrf_cookies": True,
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler,
     dict(path=settings['static_path'])),
], **settings)
```

可以这样调用静态文件
```html
<html>
   <head>
      <title>FriendFeed - {{ _("Home") }}</title>
   </head>
   <body>
     <div><img src="{{ static_url("images/logo.png") }}"/></div>
   </body>
 </html>
```

###debug模式和自动重启
传递一个`debug=True`参数给Application类的构造函数就可以进入调试模式，在这个模式下存在多个在开发时很有用的功能。
- **autoreloade=True**当源文件发生改变时自动重新加载文件
- **compiled_template_cache=False**不缓存template文件
- **static_hash_cache=False**静态文件的hash值不会被缓存
- **serve_traceback=True**当RequestHandler抛出错误时，将返回一个错误页面和一个错误栈追踪
autoreload模式并不与`HTTPServer`的多进程相兼容，如果你在多进程下使用autoreload，就只能给`HTTPServer.start`传递参数1。

###WSGI和GAE
tornado不需要WSGI就能运行（有自己的server），但在WSGI环境下（如GAE）就不能呢个使用自己的server。这种环境下tornado的功能就遭到了，如：不支持异步、协程、`@asynchronous`装饰器、`AsyncHTTPClient`、外部认证和webSocket。
可以使用` tornado.wsgi.WSGIAdapter`将一个tornado的应用装配到。下面这个例子，可以配置WSGI容器来包装tornado应用
```python
import tornado.web
import tornado.wsgi
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")
tornado_app = tornado.web.Application([
    (r"/", MainHandler),
])
application = tornado.wsgi.WSGIAdapter(tornado_app)
```

可以在`appengain`这个例子中看到具体实现。
