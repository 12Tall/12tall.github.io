---
title: 前缀树 Trie   
date: 2022-10-07    
timeLine: true
sidebar: false  
icon: nodeJS  
category:  
    - 算法与数据结构    
tag:  
    - tree    
    - Javascript    
---

因为水平有限，本文暂不讨论复杂度相关的东西。

## 什么是前缀树    
前缀树`Trie`，又叫做字典树，是一种哈希树的变种。一般用于保存、匹配大量的字符串，最典型的应用应该就是`输入预测`和`路由统计`了。顾名思义，前缀树是一个树形数据结构，其大致形状如下：  
```
0 |1 |2 |3   深度

  ,i--e (tie)
 /
t
 \  ,-e--e (tree)
  `r
    `-i--e (trie)
```

一般来说，前缀树的主要操作有：  
1. `insert(string)` 插入  
2. `search(string)` 查找  
3. `remove(string)` 删除（比较少用） 
4. `beginWith(string)` 查找以参数开头的字符串  

## 实现  
为简单以及后续扩展需要，仅实现`insert()` 和`search()` 方法  
### 类型定义  
```js
class Trie {
    constructor() {
        this.root = new TrieNode();
        this.end = Symbol('end');  // 用于表示字符串结尾
    }

    insert(str) {
        // 将字符串切分为子串，在某些情况下，TrieNode 节点保存的并不一定是单个字符
        let arr = str.split("");  
        if (arr[arr.length - 1] !== "") {
            // 对于分隔符结尾的字符串，例如"a/"，跳过结尾的空字符。
            arr.pop();
        }
        let node = this.root;
        for (let i = 0, len = arr.length; i < len; i++) {  // 逐层遍历trie
            if (!node.children[arr[i]]) {
                // 如果子节点不存在则创建新的子节点
                node.children[arr[i]] = new TrieNode(arr[i]);  
            }
            node = node.children[arr[i]];  // 如果子节点存在则进入子节点继续遍历
        }
        node.children[this.end] = true;  // 添加结束标志
    }
    search(str) {  // 查找的方法类似于插入，也是逐级遍历
        let arr = str.split("");
        let node = this.root;
        for (let i = 0, len = arr.length; i < len; i++) {
            if (!node.children[arr[i]]) {  // 如果没有对应子节点，则直接返回失败
                return false;
            }
            node = node.children[arr[i]];
        }
        // 如果完全匹配到目标则返回失败；如果要匹配开头的话，直接返回true 即可
        return !!node.children[this.end];  
    }
}

class TrieNode {
    constructor(content = "") {
        this.children = {};  // 这里可以选择用数组或者hashMap，显然后者更简单一些  

        this.content = content;
    }
}
let trie = new Trie();
trie.insert("tie");
trie.insert("tree");
trie.insert("trie");
console.log(JSON.stringify(trie));  // 简单查看数据结构
console.log(trie.search("ti"));  // 查找字串，false
console.log(trie.search("tie"));  // 查找，true
```  

### 扩展一 分隔符  
使用指定地分隔符来切分字符串，而不是单纯的拆分为单个字符。以基本类型做修改  
```diff
class Trie {
-   constructor() {
+   constructor(delimiter="") {  //用于指定分隔符
+       this.delimiter=delimiter;
        ...
    }

    insert(str) {
-       let arr = str.split(""); 
+       let arr = str.split(this.delimiter); 
        ...
    }
    search(str) {  
-       let arr = str.split(""); 
+       let arr = str.split(this.delimiter); 
        ...
    }
}

- let trie = new Trie();
- trie.insert("tie");
- trie.insert("tree");
- trie.insert("trie");
- console.log(JSON.stringify(trie)); 
- console.log(trie.search("ti"));
- console.log(trie.search("tie"));
+ let trie = new Trie("/");
+ trie.insert("tie");
+ trie.insert("tr/ee");
+ trie.insert("tr/ie");
+ console.log(JSON.stringify(trie));  // 简单查看数据结构
+ console.log(trie.search("trie"));  // false
+ console.log(trie.search("tr/ie"));  // true
```

### 扩展二 函数   
可以给字符串指定函数，此函数还可用来充当`end` 结束标识，用以在匹配成功之后运行，比如：路由处理  
```diff
class Trie {
    ...
-   insert(str) {
+   insert(str,handler= false) {
        ...
-       node.children[this.end] = true;
+       node.children[this.end] = handler;
    }
    search(str) {
        ...
-       return !!node.children[this.end];  
+       return node.children[this.end];  
    }
}

...
+ trie.search("tr/ie")();  // (｡･∀･)ﾉﾞ嗨
```

### 扩展三 通配符   
通配符只要用来匹配`RESTful` 类型的路由，关于匹配优先级的判断稍微有些复杂，例如：对于字符串`n1/n2/n3` 来说，会优先匹配到下面拿一条规则？  
1. `:i/:j/n3`  
2. `n1/:j/:k`  

在这里约定，我们的前缀树会最大限度地匹配静态值，例如：`n1`；然后再去匹配通配符，例如：`:i`。最终，还需要获取到通配符所对应的值。  

#### 小技巧  
- 因为字符串的长度和内容都是随机的，所以要求我们需要将通配符单独存储  
- 节点结束标识应该提升到节点下，而不是在`children` 中   
- 因为在匹配过程中，可能会有多条（疑似）满足的字符串，这就要求我们的函数可以进行`递归`地遍历（新增一个`parse()` 函数）  
- 最终的参数会放进一个临时的`Map`，并且有可能的话，会传递给[扩展二](#扩展二-函数) 中定义的函数    

#### 详细代码
按照上述要求修改代码  
```js
const END = symbol("end");  // 结束标识提升至全局

/**
* 首先，我们需要先修改一下TrieNode 添加一个wildcards 属性
* 用来存放本节点下的通配符 
*/
class TrieNode {
    constructor(content = "") {
        this.children = {};
        this.wildcards = {};  // 和children 功能一样，用来存放子节点
        this.content = content;
        this[END] = false;  // 因为
    }
}



class Trie {
    constructor(delimiter = "") {
        this.delimiter = delimiter;
        this.root = new TrieNode();
    }

    /**
    * 然后修改`Trie` 中的`insert()` 方法，使其能够识别并存储通配符 
    */
    insert(str, handler = false) {
        let node = this.root;
        let arr = str.split(this.delimiter);
        // 对于分隔符结尾的字符串，例如"a/"，跳过结尾的空字符。           
        if (arr[arr.length - 1] === "") { arr.pop(); }

        for (let i = 0, len = arr.length; i < len; i++) {
            if (arr[i][0] === ":") {
                // 解析通配符
                let wildcard = arr[i].split(":")[1];
                if (wildcard === "") {
                    throw "需要给参数指定名字"
                }
                if (!node.wildcards[wildcard]) {
                    node.wildcards[wildcard] = new TrieNode(wildcard);
                }
                node = node.wildcards[wildcard];
            } else {
                // 静态值
                if (!node.children[arr[i]]) {
                    node.children[arr[i]] = new TrieNode(arr[i]);
                }
                node = node.children[arr[i]];
            }
        }
        node.children[this.end] = handler;
    }


    /**
     * 递归地匹配路由节点
     * @param {Array} arr 节点数组
     * @param {Number} index 当前节点指针
     * @param {TrieNode} node 当前节点，注意引用传值的问题
     * @param {Object} params 通配符表示的参数
     */
    parse(arr = [""], index = 0, node = this.root, params = {}) {
        if (index >= arr.length) {
            return node[END] ? node[END] : false;  // 结尾判断
        }

        let result = false;
        if (node.children[arr[index]]) {
            // 优先匹配静态值
            // node = node.children[arr[index]] // 这种写法会污染node 变量
            if (result = this.parse(arr, index + 1, node.children[arr[index]], params)) {
                return result;
            }
        }

        // 因为通配符的关系，只能对所有通配符都进行匹配，
        for (let key of Object.keys(node.wildcards)) {
            result = false;
            // 只要有一个符合的，且到达结尾，就立刻退出循环  
            if (result = this.parse(arr, index + 1, node.wildcards[key], params)) {
                params[key] = arr[index];
                return result;
            }
        }
        // 否则返回失败
        return result;
    }


    search(str) {
        let node = this.root;
        let arr = str.split(this.delimiter);
        // 对于分隔符结尾的字符串，例如"a/"，跳过结尾的空字符。           
        if (arr[arr.length - 1] === "") { arr.pop(); }

        let params = {};
        return [this.parse(arr, 0, node, params), params];
    }
}

//==================测试===================//  
let trie = new Trie("/");
trie.insert(":a/:b/c", () => { });
trie.insert("a/b/c", () => { });

// 测试
console.log(trie.search("a/b"));  // [ false, {} ]
console.log(trie.search("a/c"));  // [ false, {} ]
console.log(trie.search("a/b/c"));  // [ [Function], {} ]
console.log(trie.search("a/d/c"));  // [ [Function], { b: 'd', a: 'a' } ]
```
## 总结  
第一遍写的时候，在递归的地方纠结了一下午。这次复习时，有了之前版本的对照，思路更加清晰了，更能专注地去梳理函数之间的配合，而不去想想要什么的功能。递归中两次用到了函数引用传值`this.parse(arr, index + 1, node.children[arr[index]], params))`：  
- `params` 利用引用传值来更新属性  
- `node.children[arr[index]]` 避免引用传值污染变量

