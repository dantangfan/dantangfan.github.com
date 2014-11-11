---
layout: post
title: learn Git
description: Git简单命令总结，从来都是个人用户，现在工作会团队开发，应该会用到更多的功能
category: blog
---

linux系统都可以直接软件包安装Git，如`apt-get install git`

##初始化配置
首先配置帐号信息

```bash
git config --global user.name dantangfan
git config --global user.email dantangfan@gmail.com

git config --list #查看配置情况
git help × #获取帮助
```

配置密钥

```bash
ssh-keygen -t rsa -C dantangfan@gmail.com #生成密钥
ssh -T git@github.com #测试是否成功
```

##创建仓库

```bash
git init #初始化
git status #查看状态
git add <file>
git commit -m 'msg'
git remote add origin git@github.com:dantangfan/test.git #添加源
git push -u origin master #push同时设置默认跟踪分支

git clone https://github.com/xxx/xxx.git dic
```

##本地操作

```bash
git add * #跟踪更新
rm * & git rm * #从本地和仓库中删除文件
git rm -rf * #删除文件夹
git rm --cached #取消跟踪
git mv filename new name
git log
git commit -m 'msg'
git commit -a #跳过使用暂存区，把所有已跟踪的文件暂存起来一并提交
git commit --amend #修改最后一次提交

git reset HEAD * #撤销已经暂存的文件
git checkout -- file #取消对文件的修改（从暂存区取回file）
git checkout branch|tag|commit -- filename #从仓库中取出file覆盖当前分支
git checkout -- . #从暂存区取出文件覆盖工作区
```

##分支操作

```bash
git branch #列出当前分支
git branch -r #列出远端分支
git branch -a #列出所有分支
git branch -v #查看每个分支最后一次提交的情况
git branch --merge #查看已经合并到当前分支的分支
git branch --no-merge #查看未合并到当前分支的分支

git branch test #新建test分支
git checkout test #切换到test分支
git checkout -b test #注册并切换到test
git checkout -b test dev #基于dev创建test分支

git branch -d test #删除test分支
git branch -D test #强制删除test分支

git merge test #将test分支合并到当前分支
git rebase master #将master分支上超前的分支变基到当前分支
```

##远端操作

```bash
git fetch originname branchname #拉去远端上指定分支
git merge originname branchname #合并远端上指定分支
git push originname branchname #推送到远端上指定分支
git push originname branchname:serverbranch #推送到远端指定分支

git checkout -b test origin/dev #基于远端dev分支创建test分支

git push origin :server #删除远端分支
```

##源管理
服务器上的仓库在本地称之为`remote`，个人开发的时候主要是使用单源。但是git的精华是多源，适合团体开发

```bash
git remote add origin git@github.com:dantangfan/test.git #将本地仓库推送到远程
git remote #显示全部源
git remote -v #显示源和信息
git remote originname newname 
git remote rm originname
git remote show originname
```

##tag

```bash
git tag #显示当前标签
git tag v0.1 #新建标签
git tag -a v0.1 -m 'my version 1.4' #新建带注释的标签

git checkout tagname #切换到标签

git push origin v1.5 #推送到分支源上
git push origin --tags #一次性推送所有分支

git tag -d v0.1 #删除标签
git push origin :refs/tags/v0.1 #删除远程标签
