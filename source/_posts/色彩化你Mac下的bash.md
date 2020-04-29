---
title: "色彩化你Mac下的bash"
date: "2016-04-05 13:23:37"
updated: "2016-05-10 03:08:18"
tags:
-  terminal
-  mac技巧
---


## 配置方法

最近发现很多同事使用的terminal还是mac自带的，灰常不人性化，比如不显示git状态也不能多tab。所以在这里给大家分享一下色彩化你的bash的小技巧。首先可以下载一个支持多tab的终端：[iTerm2](https://www.item2.com)。

[](/notename/ "color your bash on mac")

![iTerm2图标][1]

打开你刚刚下载的item2，执行如下命令
```bash
brew install xz coreutils # 把基础命令行工具换成gnu版本
gdircolors --print-database > ~/.dir_colors # 生成ls的色彩数据库
brew install bash bash-completion # 安装bash-completion和最新版bash（mac的bash不支持conpletion）
sudo sh -c 'echo "/usr/local/bin/bash" >> /etc/shells' # 把新版bash安装到系统shell中
chsh -s /usr/local/bin/bash # 切换当前用户的shell为新安装bash
brew link git # 重新配置git，使git的自动完成生效
vim ~/.bash_profile # 打开.bash_profile，进行下一步配置
```

.bash_profile可以如下参考
```bash
# bash补全
if [ -f $(brew --prefix)/etc/bash_completion ]; then
  . $(brew --prefix)/etc/bash_completion;
fi
if [ -f $HOME/.npm_completion ]; then
  . $HOME/.npm_completion;
fi

# ls的颜色
if brew list | grep coreutils > /dev/null ; then
  PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH"
  alias ls='ls -F --show-control-chars --color=auto'
  eval `gdircolors -b $HOME/.dir_colors`
fi

# ls快捷键
alias ll='ls -l'
alias la='ls -A'
alias l='ls -CF'

# 提示符的格式
export GIT_PS1_SHOWDIRTYSTATE=1
export PS1='\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\] \[\033[01;34m\]\w\033[01;33m$(__git_ps1)\033[01;34m\n\$\[\033[00m\] '

# grep高亮
alias grep='grep --color'
alias egrep='egrep --color'
alias fgrep='fgrep --color'

```

最后执行一下 `source ~/.bash_profile` 可以立即看到效果。不行的话关了重新开。

## 效果图
![效果图][2]

## 参考
http://my.oschina.net/tsl0922/blog/178775
http://segmentfault.com/q/1010000000636402
http://linfan.info/blog/2012/02/27/colorful-terminal-in-mac/

  [1]: /images/153964c26e8bc6368ba06f0efc732702.png
  [2]: /images/fedfa200617b7a190459b9a0e8890b70.png
