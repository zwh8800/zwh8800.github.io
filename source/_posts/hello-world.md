---
title: 你好世界
tags:
-  闲扯
---

这里是一只废喵，时隔多年，我又准备写博客了。这次搬家到了 GitHub pages，用上了hexo。整体感觉还不错，简单记录下折腾 hexo 的经历。

## 安装步骤

```bash
npm install hexo-cli -g
hexo init blog
cd blog
npm install
```

这几步是在本机上安装好 hexo，并且生成一个 hexo 项目文件。

<!-- more -->

## 配置主题

默认的主题不太喜欢，换了个叫 [Hacker](https://github.com/CodeDaraW/Hacker) 的。

```
git clone https://github.com/CodeDaraW/Hacker themes/Hacker
rm -rf themes/Hacker/.git
```

这样就安装主题到 theme 目录了，当然也可以下载 zip，手动解压缩。

之后编辑 `_config.yml` 文件，修改成 `theme: Hacker`。

另外，主题本身也有一些配置，放在 `./themes/Hacker/_config.yml` 文件里。我的配置如下，根据自己不同需求做调整。

```yml
menu:
  Home: /
  Archives: /archives
  About: /about
  RSS: /atom.xml

# gitment
gitment: false
gitment_owner:
gitment_repo:
gitment_client_id:
gitment_client_secret:

# gitalk
gitalk: false
gitalk_owner:
gitalk_admin: []
gitalk_repo:
gitalk_client_id:
gitalk_client_secret:

# valine comment
valine: false
leancloud_id:
leancloud_key:

# disqus comment
disqus: true
disqus_shortname: lengzzz

# google analytics
googleTrackId: UA-47471611-1

```

## 配置CI

travis-ci 能帮你在每次 push 时自动部署。基本上按照 https://hexo.io/zh-cn/docs/github-pages.html 这个教程就可以了，但是有个坑是目前 GitHub pages 只支持用 master 分支了，所以写文章的分支就不能是 master 了，我这里用的是 build 分支。相应的，`.travis.yml` 文件也需要修改一下：

```yml
sudo: false
language: node_js
node_js:
  - 10 
cache: npm
branches:
  only:
    - build # 重点：这里分支改成写文章的分支
script:
  - ln theme.config.yml themes/Hacker/_config.yml
  - hexo generate 
deploy:
  provider: pages
  skip-cleanup: true
  github-token: $GH_TOKEN
  keep-history: true
  target_branch: master # 重点：这里新增一个target_branch选项，值设定为 master
  on:
    branch: build # 重点：这里分支改成写文章的分支
  local-dir: public

```

## 域名

Github pages 支持自定义域名，需要将www的域名CNAME设定为 `xxx.github.io`，另外需要把@域名（就是裸的没有任何子域名的，比如本站就是lengzzz.com）的A记录修改为下列IP：

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

都设定好之后，在项目里 source 下新增一个 `CNAME` 文件（全大写），里面写上域名就ok了。

之后在 GitHub 项目的 setting 里，也将 Custom domain 里配置上域名。之后 GitHub 会自动签发域名的 ssl 证书。最好也将 setting 里的 Enforce HTTPS 勾上，这样能强制使用 https。

## 验证

大概等十几分钟后，使用域名 https://lengzzz.com/ 就能访问到了。
