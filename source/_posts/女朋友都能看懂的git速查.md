---
title: "女朋友都能看懂的 git 速查"
date: "2016-08-11 06:19:56"
updated: "2017-06-27 08:41:00"
tags:
-  git
-  速查
---


为女朋友总结了一些常用的 git 操作。这个速查默认：以 master 为主分支，开发新功能创建新分支。

[](/notename/ "girlfriend readable git quick")

![atlassian-getting-git-right.jpg-94.4kB][1]

<!-- more -->

## 1. 开发一个功能

```bash
# 首先确保自己在 master 且代码是最新的
git checkout master
git pull

# 在最新的代码上建一个分支
git checkout -b xxx

# 在本地进行开发
do something
git commit -m "zzz"

do something
git commit -m "yyy"

do something
git commit -m "www"

# 开发完成，push开发分支
git push -u origin xxx

# 在代码审核工具上创建 pull request

# 根据别人的审核意见，修改代码
do something
git commit -m "yyy"

do something
git commit -m "bbb"

# 将修改后的代码push
git push

# 审核通过，按按钮合并 pr

```

## 2. 审核过了之后有冲突

```bash
# 首先把 master 上的代码更新一下
git checkout master
git pull

# 然后把开发分支的代码 rebase 到最新的代码之上
git checkout xxx
git rebase master

# 这时，会出现冲突，打开文件，手动把文件修改正确

# 然后执行这个：
git add .
git rebase --continue

# 这时，开发分支 xxx 已经和 master 没有冲突了，push 上去
git push

# 在代码审核工具上，按按钮合并

```

## 3. 开发了一半的功能，不想 commit 也不想丢掉

```bash
# 把修改暂存起来
git add .
git stash

# 可以查看刚刚暂存的信息
git stash list

# 现在需要继续开发，把暂存的东西 pop 出来
git stash pop

# 现在再看暂存列表，已经清空了
git stash list

```

## 4. 只提交某几个文件，其他几个文件暂存起来

```bash
# 只提交这几个文件
git add 1.go 2.go 3.go
git commit -m "zzz"
# 看一下，剩下的文件确实未提交
git status
# 暂存
git add .
git stash

```

## 5. 只提交某几行，其余行暂存

打开 sourcetree 

![image_1aps6uir211qg14423s41qjq85g9.png-47.5kB][2]

选中像提交的行，点按钮暂存行

然后：

```bash
# 只提交某几行
git commit -m "zzz"
# 看一下，剩下的行确实没提交
git status
# 暂存
git add .
git stash

```

> 已暂存的修改，叫做 `stashed changes` 

## 6. 已经 git add 的文件，想变回未 add 的状态

```bash
git reset HEAD 1.go

# 如果想把所有文件都未 add 的状态
git reset HEAD .
```

> 已经被 add 的修改，叫做 `staged changes`；未 add 的叫做 `unstaged changes` 

## 7. 已经修改，但未 add 的文件，想变回未修改的状态
```bash
git checkout -- 1.go

# 如果想把所有文件都变回未修改的状态
git checkout -- .
```

## 8. 已经 commit 了，但是不想要了，想回到上一个 commit 重新写

```bash
# 回到上一个 commit，把这个 commit 的修改变成 unstaged changes
git reset HEAD^
# 把 unstaged changes 变回未修改的状态
git checkout -- .

# 重新写
```

## 9. 已经 commit，并且 push 了，但是不想要了，想回到上一个 commit 重新写

```bash
# 同上，但是最后再push的时候需要加 -f

git push -f

```

## 9. 上个方法太暴力了

```bash
# 创建一个和上个提交完全相反的提交
git revert HEAD
git push
```

  [1]: /images/56a0d8728d3325d70ca114f659975936.jpg
  [2]: /images/40fd3596ffd1775197277b3916aa77ed.png
