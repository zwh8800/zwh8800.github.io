---
title: "用 elasticsearch 给博客加上了搜索"
date: "2016-05-25 14:21:11"
updated: "2017-08-20 07:21:20"
tags:
-  elasticsearch
-  golang
-  搜索引擎
---


博客从 Wordpress 迁移过来之后一直缺少一个搜索功能，这个博客我是当做笔记性质的，有时候脑子里突然想不起某个东西的时候就上来查一下。没有搜索还是很不方便的，所以费了点时间研究了下大名鼎鼎的 elasticsearch 配合 golang 给博客加上了搜索功能。

[](/notename/ "add internal search to your blog using elasticsearch")

## elasticsearch 介绍

elasticsearch 是一个 java 编写的搜索和分析引擎，功能十分强大。但是并不意味着你的程序必须使用 java 开发，elasticsearch 是一个独立运行的程序，它会开放一个 RESTful 的接口供人调用，所以使用起来十分方便，甚至使用 curl 就能对它进行访问。另外，elasticsearch 的可伸缩性也很吸引我，使用 elasticsearch 组建一个集群十分方便，只需要把几个 elasticsearch 放到同一个局域网内就可以了，不用做任何配置你就能跑起来一个集群。这样，当你的数据量或者并发量增大的时候，只需要简单的购买几台新服务器就能解决性能问题。

我是通过 [Elasticsearch 权威指南（中文版）](http://es.xiaoleilu.com/) 这本书来学习的，也推荐大家看一看，比我讲的好。

### 一些概念

elasticsearch 中有几个基本概念，大概可以和数据库的这几个概念对应起来（如下表）。但是有一点需要注意，elasticsearch 中不会限制数据必须存在一个二维表中，你可以保存一个对象，一个数组，一个字符串，或者一个整数，就像一个 JSON 一样，十分灵活。事实上，elasticsearch 的通讯协议确实是使用 JSON 的。

| 数据库 | elasticsearch |
|  |  |
| Databases | 索引（Indices） |
| Tables | 类型（Types） |
| Rows | 文档（Documents） |
| Columns | 字段（Fields） |
| schema | Mapping |

在 elasticsearch 中保存的每条记录叫一个 `document` ，它可以是一个包含很多字段的对象，默认情况下每个字段都能被搜索。

### 基本操作

使用 curl 就可以对 elasticsearch 进行操作，但是我还是推荐一个 chrome 应用 [`postman`](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop "postman 的下载链接") ，有 JSON 语法高亮和检测，还可以保存历史记录。

![90.pic_hd.jpg-1070kB][1]

#### 索引一条记录

在 elasticsearch 中存储数据的行为叫做 `索引（index）` 。使用 HTTP 协议的 PUT 动词可以存储数据。

```
PUT http://localhost:9200/mdblog/note/23432
{
    "id": 23,
    "notename": "golang-china-download-mirror",
    "title": "做了个 golang 安装包的镜像",
    "content": "做了个 golang 安装包的镜像 闲扯 golang\n        \n        2016-05-25 16:04 PM\n    鉴于国情，国内下载 golang 安装包还是挺蛋疼的，就算使用代理速度也比较感人。虽然现在 docker 镜像是个比较好的选择，但还是有很多场景需要原始的 golang 环境的。所以抽空做了个 mirror ，定时拉取 golang 官网的安装包到我的服务器上。地址在这里：https://lengzzz.com/download/golang/包含了 golang 1.5 之后的所有版本，所有平台的安装包和源码包都放在里面，自行 control + f 搜一下吧。新版本的 golang release 之后，应该在一两天内可以拉取过来。欢迎使用。",
    "timestamp": "2016-05-25T08:04:53Z",
    "lastModified": "2016-05-25T09:01:42.923822162Z",
    "tagList": [
      "golang",
      "闲扯"
    ]
  }

```

如上，把要存储的数据写成一个 JSON 对象，放到 HTTP 的 Body 中传送给 elasticsearch 即可存储数据。

我们可以看到 url 中包含了 4 部分的信息。

| 名字 | 信息 |
|  |  |
| localhost:9200 | Elasticsearch 的 url |
| mdblog | 索引名（Index） |
| note | 类型名（Type） |
| 23432 | 文档ID（Document ID） |

很方便吧。

#### 获取一条记录

大家应当已经想到了，使用 GET 动词。

```
GET http://localhost:9200/mdblog/note/23432
```

返回的信息会多一些 metadata 。

```json
{
  "_index": "mdblog",
  "_type": "note",
  "_id": "389344",
  "_version": 1,
  "found": true,
  "_source": {
    "id": 23,
    "notename": "golang-china-download-mirror",
    "title": "做了个 golang 安装包的镜像",
    "content": "做了个 golang 安装包的镜像 闲扯 golang\n        \n        2016-05-25 16:04 PM\n    鉴于国情，国内下载 golang 安装包还是挺蛋疼的，就算使用代理速度也比较感人。虽然现在 docker 镜像是个比较好的选择，但还是有很多场景需要原始的 golang 环境的。所以抽空做了个 mirror ，定时拉取 golang 官网的安装包到我的服务器上。地址在这里：https://lengzzz.com/download/golang/包含了 golang 1.5 之后的所有版本，所有平台的安装包和源码包都放在里面，自行 control + f 搜一下吧。新版本的 golang release 之后，应该在一两天内可以拉取过来。欢迎使用。",
    "timestamp": "2016-05-25T08:04:53Z",
    "lastModified": "2016-05-25T09:01:42.923822162Z",
    "tagList": [
      "golang",
      "闲扯"
    ]
  }
}
```

#### 搜索

搜索的话可以使用 `查询 DSL` 进行，说是 DSL（领域特定语言） 听起来很吓人，实际上就是几个 JSON 对象的组合而已。

调用搜索接口需要在 url 后面加一个 `_search` 。

```
GET http://localhost:9200/mdblog/note/_search
{
    "query" : {
        "match" : {
            "title" : "linux"
        }
    }
}

```

这样，就可以使用 match 查询进行查询了。

结果：

```json
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 5,
    "successful": 5,
    "failed": 0
  },
  "hits": {
    "total": 3,
    "max_score": 0.6609862,
    "hits": [
      {
        "_index": "mdblog",
        "_type": "note",
        "_id": "340165",
        "_score": 0.6609862,
        "_source": {
          "id": 11,
          "notename": "add-swap-on-linux",
          "title": "在Linux下设置swap",
          "content": "在Linux下设置swap linux\n        \n        2016-04-10 15:53 PM\n    今早起来发现博客的数据库挂了，赶紧用手机上的ConnectBot连上去把mysql启动。看了下日志大概是因为内存不够用且没设置swap，所以mysql进程申请不到内存挂了（小内存服务器桑不起）所以赶紧把swap搞上，这样至少能让服务不轻易挂掉。这里记录一下，以备遗忘。大概分三步\n生成一个空文件\n把文件格式化成swap格式\n挂载\n",
          "timestamp": "2016-04-10T07:53:58Z",
          "lastModified": "2016-05-24T05:27:01.435772194Z",
          "tagList": [
            "linux"
          ]
        }
      }
    ]
  }
}
```

另外，我们可以为搜索加上高亮：

```
GET http://localhost:9200/mdblog/note/_search
{
    "query" : {
        "match" : {
            "title" : "linux"
        }
    },
    "highlight": {
        "pre_tags" : ["<b>"],
        "post_tags" : ["</b>"],
        "fields" : {
            "title" : {}
        }
    }
}

```

这样的话，在 hit 中会有一个 `highlight` 字段，所有关键字会用 `<b></b>` 扩起来。

#### 创建 mapping

默认情况下 elasticsearch 是不需要“建表”操作的。mapping（类似数据库的表结构）会在第一次 index 的时候建立。但是提前建立 mapping 有助于查询。建立 mapping 也是使用 PUT 动词。

```
PUT http://localhost:9200/mdblog/note/_mapping
{
	"note": {
		"properties": {
			"id": {
				"type": "long"
			},
			"title": {
				"type": "string",
				"term_vector": "with_positions_offsets",
				"analyzer": "ik_syno",
				"search_analyzer": "ik_syno"
			},
			"content": {
				"type": "string",
				"term_vector": "with_positions_offsets",
				"analyzer": "ik_syno",
				"search_analyzer": "ik_syno"
			},
			"notename": {
				"type": "string"
			},
			"tagList": {
				"type": "string",
				"term_vector": "with_positions_offsets",
				"analyzer": "ik_syno",
				"search_analyzer": "ik_syno"
			},
			"timestamp": {
				"type": "date",
				"index": "not_analyzed"
			},
			"lastModified": {
				"type": "date",
				"index": "not_analyzed"
			}
		}
	}
}
```

如上，建立一个 mapping 。主要是设置一下数据类型和查询方式。

## 在 golang 中使用

在 golang 中有方便的 package 来操纵 elasticsearch。我使用的是 [`gopkg.in/olivere/elastic.v3`](https://github.com/olivere/elastic) 还不错的一个包，所有操作都是链式调用，很有 linq 的感觉。

使用 elastic 需要先创建一个客户端：

```golang
func InitElasticSearch() (err error) {
	esClient, err = elastic.NewClient(
	    elastic.SetURL("http://localhost:9200"))
	if err != nil {
		return err
	}
	return nil
}
```

然后，就可以用 client 进行操作了。

```golang
noteDetail := model.NoteDetail{
	Id:           note.Id,
	Notename:     note.Notename,
	Title:        note.Title,
	Content:      note.ContentText(),
	Timestamp:    note.Timestamp,
	LastModified: note.LastModified,
	TagList:      tagNameList,
}

// 首先调用 Index 函数，代表这是一次索引（Index）操作
// 接着提供各种参数
_, err := esClient.Index().
	Index(MdBlogIndexName).
	Type(NoteTypeName).
	Id(strconv.FormatInt(note.UniqueId, 10)).
	BodyJson(noteDetail).
	Do()
if err != nil {
	return err
}
```

索引一条记录

```golang
func IsNoteDocumentExist(uniqueId int64) (bool, error) {
	return esClient.Exists().
		Index(MdBlogIndexName).
		Type(NoteTypeName).
		Id(strconv.FormatInt(uniqueId, 10)).
		Do()
}
```
判断是否存在

```golang
func SearchNoteByKeyword(keyword string, 
    page, limit int64) ([]*model.SearchedNote, int64, error) {
	page-- //数据库层的页数从0开始数
	offset := page * limit

	query := elastic.NewMultiMatchQuery(keyword).
		FieldWithBoost("notename", 1).
		FieldWithBoost("tagList", 2).
		FieldWithBoost("content", 4).
		FieldWithBoost("title", 4)
	highlight := elastic.NewHighlight().
		Field("content").
		Field("title").
		Field("tagList")

	result, err := esClient.Search().
		Index(MdBlogIndexName).
		Type(NoteTypeName).
		Query(query).
		Highlight(highlight).
		From(int(offset)).
		Size(int(limit)).
		Do()
	if err != nil {
		return nil, 0, err
	}

	if result.Hits == nil {
		return nil, 0, nil
	}
	maxPage := (result.TotalHits()-1)/limit + 1

	noteList := make([]*model.SearchedNote, 0, len(result.Hits.Hits))
	for _, hit := range result.Hits.Hits {
		note := model.NewSearchedNote()
		err := json.Unmarshal(*hit.Source, note)
		if err != nil {
			return nil, 0, err
		}
		note.FillHighlight(hit.Highlight)

		noteList = append(noteList, note)
	}

	return noteList, maxPage, nil
}
```

搜索记录

##  (´ ・ω・｀)

总的来说，elasticsearch 还是很方便强大的，好评。

  [1]: /images/e1cb8a757d384d5cc83ac6945bdeef0e.jpg
