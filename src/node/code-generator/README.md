---
title: 基于Node JS 的代码生成工具   
date: 2024-01-20    
timeLine: true
sidebar: false  
icon: nodeJS  
category:  
    - 开发  
    - Javascript  
tag:  
    - JavaScript  
    - postgresql      
    - art-template
---   

> 之前见过一个用Jinja2 生成C 代码的例子，联想到刚入职时师傅介绍的CodeSmith，又结合当下在用Art-Template 生成前端页面。瞬间有一种实现自己的代码生成器的冲动。  
> 于是考虑从postgresql 生成对应的数据模型，重要的SQL 语句只有两条：  
> - `SELECT * from information_schema.tables WHERE table_schema = 'public'` 选取数据表  
> - `select * from information_schema.columns where table_name = :table_name;` 选取每个数据表的字段。这里用到了`yesql` 库  


## 初始化可执行Node 项目  
除了`git init`，`npm init` 外。我们还要额外进行两项配置：  
1. 在`package.json` 的根节点中添加记录`"bin": "index.js"`  
2. 在入口文件（一般为`index.js`）头部添加`#!/usr/bin/env node`。很重要   

然后在项目根目录执行`npm i -g .`，即可将项目全局安装，输入项目名就可以运行了。  

### 设置命令行参数  
我们通过`commander` 库来实现命令行参数的解析：  
```js
const { program } = require('commander');

program.name('db2class')
    .description("CLI tools to generate JS class from postgresql")
    .version('0.0.1')

// 参数的缩写，全称 [是否可选]，描述以及默认值
program.option('-s, --config [config.json]', "sql connection parameter", 'config.json')
program.option('-t, --table [data_table]', "target table name", '*')

program.parse()
const option = program.opts()

// 效果如下：
// > db2class -h       
// Usage: db2class [options]

// CLI tools to generate JS class from postgresql

// Options:
//   -V, --version               output the version number
//   -s, --config [config.json]  sql connection parameter (default: "config.json")
//   -t, --table [data_table]    target table name (default: "*")
//   -h, --help                  display help for command
```

### 通过Art-Template 生成代码  
```js{2-3}  
var template = require('art-template');
require.extensions['.art'] = template.extension;  // 指定通过art-template 加载模板文件

// 一个按路径加载依赖的骚操作  
const conn_config = require(path.resolve(option.config))  


const class_tmpl = require('./templates/class.art');
const { writeFile } = require('fs/promises');
// 自己利用yesql 封装的query 方法，不是重点
// ...
    const data_tables = await query(sql_get_tables, { table_name })  // 获取数据表
    for (let dt in data_tables) {
        let table_name = data_tables[dt].table_name
        const dt_fields = await query(`select column_name from information_schema.columns where table_name = :table_name;`, { table_name });
        
        let html = class_tmpl({  // 根据模板生成代码
            table_name,
            dt_fields
        })
        
        await writeFile(`./output/${table_name}.js`, html)  // 保存
    }
// ...
```

下面是模板文件的样子，`{{}}` 代表模板变量或者方法：  
```js  
class {{ table_name }} {
    constructor(obj){
        {{each dt_fields }}this.{{$value.column_name}} = null;
        {{/each}}
        Object.assign(this, obj)
    }
}

module.exports = {
    {{table_name}}
}
```

通过Node 真的可以很方便的开发一些自用的小工具！但是发现自己写的代码距离实用还是差距蛮大的  
o.O

-----  
2024-01-20 Tokyo  

## 参考资料  
1. [10分钟开发一个npm全局依赖包（上）](https://cloud.tencent.com/developer/article/1720509)  