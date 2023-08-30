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

> 在第一次学习`antlr4` 时，其实对这个工具的工作机制并不清晰，于是笔记越记越混乱。由于回国准备婚礼中断了学习过程，于是想着从头学习，尽量将笔记做得条理清晰些吧。   

## 写在最前面  
`antlr4` 是一个编译器前端工具，由Java 语言开发，可以完成词法分析和语法分析，最终生成抽象语法树（AST）。虽然`antlr4` 起于Java，但是其支持多种目标语言，例如：C++, Python, JavaScript 等。  
现在使用`antlr4` 也并不一定需要安装Java，官方提供了基于Python3 的工具包：`pip install antlr4-tools`。该工具包包含两个命令：  
- `antlr4` 生成器主程序（首次运行时可能会提示安装jre 环境）。关键参数：  
  - `-Dlanguage=[Cpp|JavaScript|Python3|Python2]` 目标语言，默认会生成Java 语言的解析器代码。这个目标语言要与语法规则文件中内嵌的`action` 等语言一致；      
- `antlr4-parse` 可以用来验证语法规则、并生成可视化的预览。关键参数：  
  - `-gui` 生成可视化AST 预览  
  - `ctrl-D/ctrl-Z` 快捷键退出程序      

另外，如果要运行生成的Python 目标代码的话，还需要安装运行环境：`pip install antlr4-python3-runtime`。

## ANTLR4 语法  
`antlr4` 的描述语法基本上派生于C 语言，会有少量的扩展。  

### 注释  
同C 语言一样，`antlr4` 支持两种注释风格：`//` 和`/**/`。    

### 标识符  
- `token` 要求首字母大写，表示词法规则；  
- `grammar` 要求首字母小写，表示语法规则；  
- 特殊的，可以使用`Unicode` 作为标识符，但是需要嵌入目标语言代码特殊处理。    

### 文本  
`antlr4` 中不区分字符和字符串，所有的内容都包含在单引号中，包括转义字符和`Unicode`。如：`'\''`, `'\uXXXX'` 等。  

### 动作  
动作（Action）是一个用花括号`{}` 包裹的由目标语言写的代码块，在存在嵌套花括号时，要注意转义。  
```antlr4  
grammar Count;

// action @header: 在文件头引入包
@header {
    pacakage foo;  
}

// action @member: 在文件中定义变量count  
@members{
    int count = 0;
}

// action @after：使用变量，执行到花括号时打印count，并依次自增两次。    
list @after{System.out.println(count+"ints");} : INT {count++;} (',' INT {count++})*;

INT: [0-9]+;
```  

### 保留字  
`antlr4` 有一些保留字：  
```txt  
import, fragment, lexer, parser, grammar, returns,
locals, throws, catch, finally, mode, options, tokens
```

## 语法结构  
语法文件的结构，一般如下所示：  
```antlr4  
/** Optional javadoc style comment */
grammar Name; 
options {...}
import ... ;
 	
tokens {...}
channels {...} // lexer only
@actionName {...}
 	 
rule1 // parser and lexer rules, possibly intermingled
...
ruleN
```  

- 文件名：文件名必须与`grammar` 的`Name` 相同，文件的后缀名为`.g4`  
- `token`，`import`，`options` 元素的顺序可以任意，每种元素每个文件可以有零个或一个    
- `rule` 规则应至少有一个，如果不在`grammar Name;` 前声明规则类型，那么该文件可以同时包含语法规则和词法规则  
- `mode` 只有`lexer grammar` 中存在  
- `channel` 也只在`lexer grammar` 中存在     
```antlr4  
channels {
  WHITESPACE_CHANNEL,
  COMMENTS_CHANNEL
}

WS : [ \r\t\n]+ -> channel(WHITESPACE_CHANNEL) ;
```  

### Import  
通过`import` 指令，可以让语法描述文件拆分成可重用的小块。修改起来也比较方便。主文件会集成源文件所有的规则，并且会覆盖掉源文件中的同名规则。  

### Token   
`token` 节用来定义没有相关的词法规则的词素。  
```antlr4  
// explicitly define keyword token types to avoid implicit definition warnings
tokens { BEGIN, END, IF, THEN, WHILE }
 
@lexer::members { // keywords map used in lexer to assign token types
Map<String,Integer> keywords = new HashMap<String,Integer>() {{
	put("begin", KeywordsParser.BEGIN);
	put("end", KeywordsParser.END);
	...
}};
}
```

-----  

## 解析器语法  
`antlr4` 的语法基本有以下两种形式：  
```antlr4  
/** name : body */
retstat : 'return' expr ';' ;  

/** 或者通过 `|` 表示或操作 */
operator:
 	stat: retstat  // 在规则中定义子规则，新手尽量不要这样用
 	| 'break' ';'
 	| 'continue' ';'
 	;
```
`antlr4` 会为每条规则都生成一个对象，可以通过`=` 为规则添加标签，这样在生成的代码上下文中会添加字段。参考[ANTLR4学习笔记](https://yijun1171.github.io/2015/03/30/ANTLR4%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0-%E8%AF%AD%E6%B3%95%E5%AD%97%E5%85%B8-Grammar-Lexicon/)  

`?+*` 在规则中同样适用。  

### 异常处理  
异常处理的形式如下，需要在规则结束后定义：
```antlr4  
r : ...
  ;
  catch[RecognitionException e] { throw e; }
  finally { System.out.println("exit rule r"); }
```  
异常列表：  
- `RecognitionException`  
- `NoViableAltException`  
- `LexerNoViableAltException`  
- `InputMismatchException`  
- `FailedPredicateException`    

### 规则的属性  
暂不涉及。  
```antlr4  
// 解析1+2*3，同样新手尽量不要用
expr[int pr] : id
               ( {4 >= $pr}? '*' expr[5]
               | {3 >= $pr}? '+' expr[4]
               | {2 >= $pr}? '(' expr[0] ')'
               )*
             ;
```

### 入口规则和EOF  
需要记住的是`EOF` 表示文件结尾就是了：  
```antlr4  
file : element* EOF; // don't stop early. must match all input
```  

一般来说，由上面的只是就能写一个不错的前端了。

-----  

## Action 和 Attribute  
在前文我们看到了Action 的基本用法，下面的例子会讲到如何在Action 里面访问语法规则的上下文：  
```antlr4  
decl: type ID ';'
      // 通过规则名访问上下文  
      {System.out.println("var "+$ID.text+":"+$type.text+";");}

    | t=ID id=ID ';'
      // 通过label 标签访问规则上下文 
      {System.out.println("var "+$id.text+":"+$t.text+";");}

    ;
```  

### token 属性  
而一条规则全部的属性有以下几种，如无特殊说明，均为`int` 类型：  
- `text`: 字符串  
- `type` token 类型  
- `line` 行号  
- `pos` 列号  
- `index` 所在序号  
- `channel`  
- `int` token 的整数值  

### 语法属性  
同样的，在Action 中可以访问到以下语法规则的上下文：  
- `text`: `String`  
- `start`: `Token`  
- `stop`: `Token`  
- `ctx`: `ParserRuleContext`  
- `parser`: `parser`     

### 动态作用域属性  
暂不涉及。  

## 词法分析    
需要注意的是`mode` 允许按上下文对词法规则进行分组，看起来还挺抽象的。并且在组合语法中不允许使用`mode`。  

此外，还有一些常用的词法规则：  
- `T`: token 名    
- `'literal'`: 文本    
- `[char set]`: 或运算    
- `'x'..'y'`: 类似于`[a-z]`   
- `.`: 任意一个字符串      
- `~x`: 不包含运算符    

并且词法分析是支持递归的！  

### 词法分析器的命令  
- `skip`: 跳过当前的token  
- `push/popMode`，`mode()`，`more()`：用于操作模式栈  
    ```antlr4  
    // Default "mode": Everything OUTSIDE of a tag
    COMMENT : '<!--' .*? '-->' ;
    CDATA   : '<![CDATA[' .*? ']]>' ;
    OPEN : '<' -> pushMode(INSIDE) ;
    ...
    XMLDeclOpen : '<?xml' S -> pushMode(INSIDE) ;
    SPECIAL_OPEN: '<?' Name -> more, pushMode(PROC_INSTR) ;
    // ----------------- Everything INSIDE of a tag ---------------------
    mode INSIDE;
    CLOSE        : '>' -> popMode ;
    SPECIAL_CLOSE: '?>' -> popMode ; // close <?xml...?>
    SLASH_CLOSE  : '/>' -> popMode ;
    ```
- `type()`：似乎是指定token 内容的类型？  
- `channel()`：用于指定channel，但是如何定义channel 呢？

通过`option` 指令还可以设置是否大小写敏感，具体可以参考[Option](https://github.com/antlr/antlr4/blob/master/doc/options.md)。  

-----   

## 解释编译  
虽然看起来花里胡哨的用法很多，但是初学者能用到的东西其实很少，最重要的还是语法图部分。以及，如何将`antlr4` 生成的结果解释并运行，否则写前端就没有了任何意义。  

以[]() 中的代码为例，`#` 后面的标签可以用来生成`listener` 和`visitor`：  
```antlr4  
grammar Calc;

prog
    : stat+
    ;

stat
    : expr                   # printExpr
    | ID '=' expr            # assign
    ;

expr
    : expr op=(MUL|DIV) expr # MulDiv
    | expr op=(ADD|SUB) expr # AddSub
    | INT                    # int
    | ID                     # id
    | '(' expr ')'           # parens
    ;

MUL : '*' ;

DIV : '/' ;

ADD : '+' ;

SUB : '-' ;

ID  : [a-zA-Z]+ ;

INT : [0-9]+ ;

WS  : [ \t\r\n]+ -> skip ;    // toss out whitespace
```

其中`visitor` 可以用来实现解释器：  
```bash
# 为所有标签声明一个visitor 接口
antlr -no-listener -visitor Calc.g4  
```
而在`listener` 模式下，我们可以开发编译型的语言。同样的，是通过实现相应的接口方法实现的：  
- `enterXX()`  
- `exitXX()`  

下面是python 中执行`listener` 的代码：  
```python  
import sys
from antlr4 import *
from CalcLexer import CalcLexer
from CalcParser import CalcParser
from CalcListener import CalcListener 
 
def main():
    input_stream = InputStream('4+5')
    lexer = CalcLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CalcParser(stream)
    tree = parser.prog()  # 起始规则
    # 需要预先实现Listener 内的方法  
    printer = CalcListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

main()
# https://stackoverflow.com/a/53817040 关于antlr4 不能直接读取字符串输入  
```
所以说，`antlr4` 不仅可以做前端用，甚至还为后端设计了一套模板。好帅啊~~~

另外，有一个语法仓库，包含了很多语言的语法规则，感觉还是蛮有用的：[antlr/grammars-v4](https://github.com/antlr/grammars-v4)    

## 参考资料   
1. [ANTLR 4 Documentation](https://github.com/antlr/antlr4/blob/master/doc/index.md)  
2. [ANTLR 4简明教程](https://wizardforcel.gitbooks.io/antlr4-short-course/content/)  
3. [ANTLR4学习笔记](https://yijun1171.github.io/2015/03/30/ANTLR4%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0-%E8%AF%AD%E6%B3%95%E5%AD%97%E5%85%B8-Grammar-Lexicon/)