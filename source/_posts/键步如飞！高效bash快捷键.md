---
title: "键步如飞！高效bash快捷键"
date: "2016-04-12 15:30:41"
updated: "2016-04-23 12:17:14"
tags:
-  bash
-  mac技巧
---


程序员们每天面对最多的就是自己的terminal了，所以一定要把terminal配置的高效起来，这样不但提高工作效率，而且令人身心舒畅。

[](/notename/ "bash hotkey")

[toc]

![iTerm2][1]

首先打开你的 iterm2 的 `Preferences` ，点击 `profile` 选项卡，再点击一下 `key` 子选项卡，把里面的 `Left option acts as` 设置成 +Esc 。这样按 `option` 键就不会出现奇奇怪怪的字符了。

下面，介绍几个用的比较爽的快捷键：

## 按单词移动光标

- `option+b` ：前移一个单词
- `option+f` ：后移一个单词

其中 b 和 f 分别是 backward 和 forward 的意思，这样是不是比较容易背了。

## 移动到行首行尾

- `fn+left` ：移动到行首
- `fn+right` ：移动到行尾
- `control+a` ：移动到行首
- `control+e` ：移动到行尾

fn+left 和 fn+right 其实是 Mac 自带的功能，分别对应大键盘上的 Home 和 End 键，此外 fn+up 和 fn+down 对应 PgUp 和 PgDown。

a 和 e 可以记忆为 `第一个字母` 和 `end` :)

## 删除命令

- `control+w` ：删除一个单词
- `control+u` ：删除一行
- `control+l` ：清屏

w 可以认为是word

## 其他

使用 `control+r` 可以搜索最近使用的命令。另外，bash中也可以配置autojump。

```bash
brew install autojump
echo '[[ -s $(brew --prefix)/etc/profile.d/autojump.sh ]] && . $(brew --prefix)/etc/profile.d/autojump.sh' >> ~/.bash_profile
```

重启下 terminal 现在可以使用命令 `j xxx` 了。autojump使用一个数据库，记录你最常使用的目录，你只需要打目录名字的一部分就可以 `jump` 到目录。

  [1]: http://static.zybuluo.com/zwh8800/bqid4nhf69zl7c8e8qq19359/QQ20160412-1@2x.png
