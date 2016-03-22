---
layout: post
title: 好看的长微博
description: 长微博是怎么生成的
category: blog
---

在做有料道的时候，有一个需求是长微博的分享功能。Xu 说我们有很大程度上会靠长微博进行推广，所以我们这个功能必须要做好。于是，一不小心就在 Xu 的带领下做成了目所能及中最漂亮的长微博。

首先一个问题是如何生成长微博？逛了挺久，没有啥成熟的方案或者分享。要自己写一个工具基本是不可能的，没那个技术也没那么多时间。于是就从 git 上面找工具，经过一番测试之后，找到了两款还算舒服的工具

- [wkhtmltoimage](https://github.com/wkhtmltopdf/wkhtmltopdf)
- [phantomjs](https://github.com/ariya/phantomjs)

经过一番测试之后，选择了前者，前者安装使用较为简单，并且功能也够全。

接下来就是生成规则了。开始Xu希望点击分享按钮的时候生成一张长微博，这样的逻辑当然是最简单的。但是可想而知，如果一个问答或者料图片比较多，那这个生成长微博的时间就会很长。

于是有了初步的改进方案，只在第一次点击分享的时候才去生成图片，每次点击分享的时候都先检查七牛上这张图片的状态。

于是又遇到一个问题，改如何给图片命名才能唯一并且可辨认呢？

一个简单的办法就是随机命名，直接记录入数据库，但我是这样浪费的人吗？就为了记录一点东西就多加个字段或者多加表，多么浪费呀！而且使用分享功能的人并不会有很多，反正我看了那么多年知乎也没分享几个。

于是乎，要让前端后端都能知道一个问答的长微博名叫啥，那还不简单么？直接用 updated_at 时间戳加上问题 ID 就行了嘛。于是乎有这么玩儿了一会儿。。

但是，就这样我就会满足了吗？为了减轻前端的负担，我决定不这样做。首先，可以把检测图片状态的工作交给后端来做，反正我们也是异步的。可是，生成长微博是同步的啊，吓尿了好么，随便弄点账户来不停的修改一些问题或者一些料，那我后端就忙不迭的去生成长微博。那还得了，每个生成两秒钟，我不就直接卡死了么。

然后我就自己测了一下自己。恩，想都不用想，同步怎么能扛得住嘛！

还是改吧，把生成长微博写成后台任务，开些进程来跑。

但是工具始终是会出差错的，比如网络出错什么的，都会导致长微博生成失败，虽然概率小，但是还是会有。于是在省城长微博的函数上加了个 retry ，七牛上传自己都会 retry ，不用管了。可是 retry 也不能太多了，两三次顶天了，不然你叫后面的同学怎么办。

所以在 retry 之后，还多加了个 crontab 来定时检查图片生成情况，就每小时检查一次吧，检查最近有没有生成图片出问题的。

视觉才是关键，真是被 Xu 的像素眼给虐哭了。样式啥的还好，关键是字体，周末被 Xu 追杀一番后还真弄出来不少东西。

英文字体没啥好说的，真真好不好看在于中文字体。恩，现在我要说的才刚刚开始，都是一些前端的知识。Xu 在 html 全局，和 div 内部的两次 font-family 声明引发了我对字体的兴趣

font-family 大发好。

首先，我曾经常常声明字体的方法是很 low 逼的

```
font-family: Arial, "宋体", "微软雅黑";

font-family: Helvetica, Arial, "华文细黑", "微软雅黑";
```

然后，font-family 没有继承功能，也就是说，div 中生命的 font-family 没有找到适用的话，会自动调用系统字体，而不会去砍 html 全局 font-family 设置。

一般情况下，我们都会看到`sans-serif`、`sans`这样的声明会放在 font-family 的最后。这是字体簇的非衬线和衬线，至于是什么，google 一下就知道。

我们需要注意的是，中文字体也是有英文名字的，比如`微软雅黑`的英文名叫`Microsoft YaHei`，而`宋体`的英文名叫`SimSun`，写代码的时候要注意把中英文名字都给搞上去。因为有的系统不认识中文。。。。

说到系统，我们还应该注意不同的系统，比如英文字体，我们就该在最前面放上 **Helvetica（mac特有）, Tahoma（win特有）, Arial（大家都有）** ，多了解点字体对web开发没啥坏处。

然后，建议将英文名写在前面，中文名写在后面，这是为了统一。。

绝大多数的中文字体都支持英文，但是英文字体就不一定支持中文了。将适当地英文字体放在最前面，渲染的时候就会先找到这个英文字体，在没有找到的时候才会去中文字体里面乞讨英文字体。

中英文混排比较常见，于是不要忘了在最前面先把你漂亮的英文字体搞上去。

然后，到了这里。我们是不是该结束了呢？too young

我们的服务器是linux系统，尽管它很棒，但是对于正常人的日常需求 linux 就会显得很奇葩。比如 qq 啊，游戏啊啥的。

于是字体当然也奇葩啦，不过爽的是，我们可以很快的排错。

字体设置:

首先，将你的字体放到 `/user/share/fonts` 中（其实放入字体配置文件`/etc/fonts/fonts.conf`中`<!-- Font directory list -->`字段下的任何一个文件夹内都可以）

然后执行`fc-cache -v`加载字体，其实不执行好像也没啥问题。

然后用`fc-list` 查看你的字体是否加载出来了，还能根据这个看你可以在 css 中怎么引用字体名字。

fc-cache 加载是有顺序的，所以不要随便到哪里去下载一个乱起八糟的字体。不仅能让你变丑，还有中度的危险。

至于服务器上，在 font-family 没找到的时候调用系统默认字体，测试机上中英文分开渲染，然而服务器上却是统一渲染。。。至今没搞懂为毛

命名查看默认字体的时候都是一样的嘛`fc-match sans`

最后，字体跨平台之后的表现不一定会好，比如把 mac 上的字体放到 win 上，不见得就好看。

最后的最后，美和丑都是相对的，你说人家的丑，可能是你眼睛出了问题。