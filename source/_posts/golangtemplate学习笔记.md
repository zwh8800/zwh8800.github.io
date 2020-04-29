---
title: "golang template 学习笔记"
date: "2016-04-07 07:05:57"
updated: "2016-04-23 12:19:17"
tags:
-  golang
-  template
---


最近几天用golang写自己的博客系统，手贱选用了golang自己的template包做模版系统。发现这个模版里面好多不符合常识的地方，记录一下。（偷懒没直接用pongo2真是败笔

[](/notename/ "learning golang template")

[toc]

首先，golang的template分在两个package里，我一开始只看 `html/template` 包了，一直吐槽为什么文档这么不全，后来发现大部分功能在 `text/template` 里，html包只负责部分html特有的功能。

## Layout

先看两种常见的模版布局方式吧(都是伪代码)：
### 1. include 方式

```html
<!-- content.html -->
{% raw %}{{ include "header.html" }}{% endraw %}
<div class="content">
    <!-- content -->
</div>
{% raw %}{{ include "footer.html" }}{% endraw %}
<!-- end of content.html -->
```

```html
<!-- header.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>
    xxx
    </title>
    <link href="xxx.css" rel="stylesheet" media="screen">
    <script src="xxx.js"></script>
</head>
<body>
<!-- end of header.html -->
```

```html
<!-- footer.html -->
</body>
</html>
<!-- end end of footer.html -->
```

### 2. layout 方式
```html
<!-- layout.html -->
{% raw %}{{ define "layout" }}{% endraw %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>
    xxx
    </title>
    <link href="xxx.css" rel="stylesheet" media="screen">
    <script src="xxx.js"></script>
    {% raw %}{{ template "moreStyles" }}{% endraw %}
</head>
<body>
    {% raw %}{{ template "content" }}{% endraw %}
    {% raw %}{{ template "moreScripts" }}{% endraw %}
</body>
</html>
{% raw %}{{ end }}{% endraw %}
<!-- end of footer.html -->
```
```html
{% raw %}{{ use "layout" }}{% endraw %}
{% raw %}{{ define "content" }}{% endraw %}
    <!-- content -->
{% raw %}{{ end }}{% endraw %}
{% raw %}{{ define "moreScript" }}{% endraw %}
    <script src="you-script.js"></script>
{% raw %}{{ end }}{% endraw %}
```

### 3. 实现

一般我习惯layout方式的模版，这样结构清晰，而且IDE友好。但是golang的template好像没有对layout格式的模版做**特别的**支持。只好找一种折衷的比较优雅的实现方式。

首先，在模版目录下新建一个 `common` 目录，用于存放各种公共的template。之后，在下面创建 `layout.html` 。
```html
{% raw %}{{ define "layout" }}{% endraw %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>
    {% raw %}{{ template "title" .}}{% endraw %}
    </title>
    <link href="common.css" rel="stylesheet">
    {% raw %}{{ template "moreStyles" .}}{% endraw %}
</head>
<body>
    {% raw %}{{ template "content" .}}{% endraw %}
    <script src="common.js"></script>
    {% raw %}{{ template "moreScripts" .}}{% endraw %}
</body>
</html>
{% raw %}{{ end }}{% endraw %}
```
这个文件使用action `define` 定义了一个叫做 `layout` 的模版，这个layout模版分别引用了 `title`、 `moreStyles`、 `content`、 `moreScripts` 这四个模版。

之后，在模版目录下新建真正的view，比如 `note.html`。
```html
{% raw %}{{/* 定义layout所需要的template */}}{% endraw %}
{% raw %}{{ define "title" }}{% endraw %}
{% raw %}{{ .note.Title }} - {{ .site.Name }}{% endraw %}
{% raw %}{{ end }}{% endraw %}
{% raw %}{{ define "moreHeaders" }}{% endraw %}
{% raw %}{{ end }}{% endraw %}
{% raw %}{{ define "moreStyles" }}{% endraw %}
    <link href="/static/css/note.css" rel="stylesheet">
{% raw %}{{ end }}{% endraw %}
{% raw %}{{ define "moreScripts" }}{% endraw %}
    <script src="/static/js/jquery-2.2.2.min.js"></script>
    <script src="/static/js/note.js"></script>
    <script>
        // inline script
    </script>
{% raw %}{{ end }}{% endraw %}
{% raw %}{{ define "content" }}{% endraw %}
    <article class="note">
        {% raw %}{{ .note.UnescapedContent }}{% endraw %}
    </article>
{% raw %}{{ end }}{% endraw %}

{% raw %}{{/* 引用layout，传入scope */}}{% endraw %}
{% raw %}{{ template "layout" . }}{% endraw %}
```

这个需要文件定义所有被layout引用的模版项（为空也要定义），然后最重要的一句是 `{% raw %}{{ template "layout" . }}{% endraw %}` 这里把 `.` 传给了layout，从而能使 `layout` 访问model。

总之golang的template只使用了两个关键字 `template` 和 `define` 完成这个工作，可以算好处也可以算坏处（不够直观）

最后，在代码中这样调用：
```golang
const templateDir = "template"
const commonDir = "common"

type Render struct {
	templateName string
	template     string
	data         interface{}
}

func NewRender(template string, data interface{}) *Render {
	return &Render{
		template,
		path.Join(templateDir, template),
		data,
	}
}

func (r *Render) Render(w http.ResponseWriter) error {
	util.WriteContentType(w, []string{"text/html; charset=utf-8"})
	t := template.New("")
	if _, err := t.ParseGlob(path.Join(templateDir, 
	    commonDir, "*")); err != nil {
		return err
	}
	if _, err := t.ParseFiles(r.template); err != nil {
		return err
	}
	return t.ExecuteTemplate(w, r.templateName, r.data)
}

```

另外，可以在common里定义更多通用的小组件，以便调用，比如 `tag`、`article` 之类的。

## Unescape

golang的escape做的很好，可以区分当前语境（`Contexts`)，把变量放到不同的地方会有不同的输出：

| Context | {% raw %}{{.}}{% endraw %} 的输出 |
| :  | ::  |
| `{% raw %}{{.}}{% endraw %}` | `O'Reilly: How are &lt;i&gt;you&lt;/i&gt;?` |
| `<a title='{% raw %}{{.}}{% endraw %}'>` | `O&#39;Reilly: How are you?` |
| `<a href="/{% raw %}{{.}}{% endraw %}">` | `O&#39;Reilly: How are %3ci%3eyou%3c/i%3e?` |
| `<a href="?q={% raw %}{{.}}{% endraw %}">` | `O&#39;Reilly%3a%20How%20are%3ci%3e...%3f` |
| `<a onx='f("{% raw %}{{.}}{% endraw %}")'>` | `O\x27Reilly: How are \x3ci\x3eyou...?` |
| `<a onx='f({% raw %}{{.}}{% endraw %})'>` | `"O\x27Reilly: How are \x3ci\x3eyou...?"` |
| `<a onx='pattern = /{% raw %}{{.}}{% endraw %}/;'>` | `O\x27Reilly: How are \x3ci\x3eyou...\x3f` |

假如 `{% raw %}{{.}}` 是 `O'Reilly: How are <i>you</i>?`，把 `{{.}}{% endraw %}` 放到不同的地方会有不同的输出。

但是怎么让变量输出它本身的模样呢，`html/template` 提供了几个type来做这件事：

```golang
type (
	CSS string
	HTML string
	JS string
	JSStr string
	URL string
)
```
假如在模版中
```html
<img src="{% raw %}{{ .img.url }}{% endraw %}">
```
是无法直接输出的。需要用到上面的几个类型。
```golang
data := map[string]interface{} {
    url: template.URL(url),
}
```
其他的类似。

## Pipelines

golang起的这个名字有点奇怪，当作是 `expression` （表达式）就好了。有三种使用方法

- 参数
- .method [参数 参数 参数 ...]
- 函数 [参数 参数 参数 ...]

是可以直接调用方法或函数的，不过不需要加小括号。


