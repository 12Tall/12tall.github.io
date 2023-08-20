---  
title: antlr4 笔记  
date: 2023-08-02
timeLine: true
sidebar: false  
icon: python
category:      
    - 编译原理  
tag:   
    - 词法分析    
    - 语法分析  
    - antlr4  
    - java  
    - python   
---    

## 安装  
- `pip install antlr4`    

### 输入文件（语法）  
输入文件应该与文件内容的语法名相同，大小写敏感，以`Expr.g4` 为例：  
```antlr4  
/**
 * 一个简单的四则运算的语法  
 */
grammar Expr;		
prog:	expr EOF ;  // 语法规则总是小写开头
expr:	expr ('*'|'/') expr
    |	expr ('+'|'-') expr
    |	INT
    |	'(' expr ')'  // 不区分字符和字符串，但是字符串中的正则表达式是无效的
    ;
NEWLINE : [\r\n]+ -> skip; // token 总是大写开头
INT     : [0-9]+ ;  // 当然也支持其他Unicode 字符，但是处理起来稍微麻烦些  
```  

可以看到语法解析和词法分析的规则写在一起了。

### 生成AST  
`antlr4-parse` 命令可以用来生成抽象语法树（结果是字符串的形式）：  
```bash
antlr4-parse Expr.g4 prog -tree .\code  
# 格式：antlr4-parse 语法定义文件 入口规则 显示样式 源文件
antlr4-parse -h # 帮助 
```  

### 生成解析器代码  
`antlr4` 命令可以用来生成词法分析器和语法分析器代码：  
```bash  
antlr4 Expr.g4

# 或者  
antlr4 -Dlanguage=Cpp Expr.g4  
# 可选的目标语言还包括：JavaScript，Go，Python2，Python3 等  
# Python 教程：https://github.com/antlr/antlr4/blob/master/doc/python-target.md
```  

这里简单记一下`anltr4` 这个工具，详细用法可以参考[The Definitive ANTLR 4 Reference](http://amzn.com/1934356999)  

另外，有一个语法仓库，包含了很多语言的语法规则，感觉还是蛮有用的：[antlr/grammars-v4](https://github.com/antlr/grammars-v4)  

## 标准语法  
```antlr4
/** JavaDoc 风格的注释 */
grammar Name;  // 语法名同文件名
/**
* 也可以写作单独的语法分析或词法分析器的样子  
* parser grammer Name;  
* lexer grammar Name;  // lexer 语法可以包含model 模块
*/

// actions： 用于编写一段函数，用于执行一些自定义的功能  
// 一般函数内容与目标语言有关，以Java 为例：
@header {  // header 表示在antlr4 生成代码类之前注入代码  
    // package foo;   
}
@member {  // member 表示将代码作为生成语法分析器类或词法分析器类的属性或方法注入
    // int count = 0;
}

@after {
    System.out.println(count + " ints"); 
}


options {...}
import ... ;
 	
tokens {
    /**
    * tokens 指定token 名，并不是必须的，可以用来表示一般词法规则无法
    * 解析的token。一般用来放置action 需要用到的token。  
     */   
    
}
channels {
    // 只有词法分析器可以包含channels 
    // 常用的CHENNEL 还有skip
    WHITESPACE_CHANNEL,  
    COMMENTS_CHANNEL
} 
@actionName {...}

// 词法分析与语法分析的规则，可能相互混杂存在
INT: [0-9]+ ;
WS: [ \r\t\n]+ -> channel(WHITESPACE_CHANNEL); 
// 匿名规则，用于统计整数的个数
: INT {count++;} (',' INT {count++;})*;  // 如果花括号是平衡的，则无需转义。否则的话需要用转义字符串标记：\{ 或\}。  

retstat : 'return' expr ';' #Return; // # 后表示语法标签名
ruleN
```

## Import 语法  
通过`import` 语法，可以将一个大的语法文件分解为若干个模块，效果类似于`C` 语言中的`include` 指令：  
```antlr4
// MyElang.g4
grammar MyElang;  
import Elang;  
expr: INT | ID;  // 覆盖了前面的定义
INT : [0-9]+;   

// Elang.g4  
grammar Elang;  
stat: (expr ';')+;  
expr: INT;  
WS: [\r\t\n]+ -> skip;  // 跳过空白字符  
ID: [a-z]+;

// 最终效果 
grammar MyElang;  
stat: (expr ';')+;  
expr: INT | ID;
INT: [0-9]+;  
WS: [\r\t\n]+ -> skip; 
ID: [a-z]+;
```  
`import` 指令依照深度有限的策略处理命名冲突，也就是说如果存在两个同名的规则，则会优先使用嵌套深度最大的那个。  


-----  

因为距离上次阅读说明文档过去太久了。此笔记暂停，待后续重新整理。