---  
title: ply-lex 学习笔记  
date: 2023-04-08
timeLine: true
sidebar: false  
icon: python
category:  
    - Python      
    - 编译原理  
tag:   
    - python    
    - ply
    - 词法分析  
---  

> `PLY` 包括两部分：`lex.py` 和`yacc.py` 分别负责词法分析和语法分析工作。因为`python` 的执行效率一般不会高过`C++` 甚至`Javascript`，有一个问题，高效固然很重要，可是编译器的效率有必要非常高吗？能否只关注易用性而通过其他方案解决编译效率的问题？  

`PLY` 不能在`ipython` 中运行！！！  

因为LLVM 的存在，开发者可以将编译器的前端和后端解耦、减少了项目的复杂度。而且前端也有着成熟的解决方案。所以编译器开发的重点工作就到了`AST` 到`LLVM` 的中间表示层`IR` 的翻译工作。而关于词法分析器、语法分析器、语义分析和解释器的原理，在[12Tall/lsbasi_cn](https://github.com/12Tall/lsbasi_cn) 翻译中也有比较详细的解释。   

## Lex  
词法分析器的工作就是将一系列的输入字符串转化为`token` 流，在`ply.lex` 中，主要通过正则表达式来定义`token` 的规则，然后由内部的逻辑机制去自动匹配这些规则。其中，词法分析有两个重要的原则：  
-  最长匹配原则：例如`intI` 会被识别为符号`intI` 而不会被识别为类型`int` 和符号`I`；   
-  最先声明原则：如果要识别`==`，则需要将其定义在`=` 规则之前（函数或变量声明的位置）；    
-  如果一个`token` 同时符合多个规则，则会将其识别为最先声明的。如`break` 会被识别为保留字而不是符号。  

### lex 自动初始化  
通过[PLY 源码阅读之 Lex 篇](https://re-ra.xyz/PLY-%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB%E4%B9%8B-Lex-%E7%AF%87/) 可以看到`lex` 初始化的过程。主要是利用反射机制来通过模块中的全局变量和函数名来构建词法分析器。但是使用了太多的python 技巧会造成程序的可读性变差。
```python
import sys

def get_caller_module_dict(levels):
    f = sys._getframe(levels)
    ldict = f.f_globals.copy()
    if f.f_globals != f.f_locals:
        ldict.update(f.f_locals) 
    return ldict

def lex(module=None):
    if module:
        _items = [(k,getattr(module,k)) for k in dir(module)]
        ldict = dict(_items)
    else:
        ldict = get_caller_module_dict(2)
```  

于是我们也可以将`token` 定义在独立的文件中。例如`lex(module='tokens.py')`。而我们的项目结构也就自然成为以下形式：  
```txt  
+- app.py  
+- tokens.py
```
而`token` 的规则统一定义在`tokens.py`。  

### 词法定义  
以官方的示例代码为例，关于优先级的问题需要在[最后的例子](#词法分析器工程化)中具体实验：  
- 所有的规则都以`t_` 开头  
- 简单`token` 定义为变量，需要特殊处理的定义为函数`t_NUMBER(t)`，其中`t` 应有以下属性：    
  - `type` 字符串，符号类型  
  - `value` 符号值  
  - `lineno` 行号、`lexpos` 列号，可能同时存在于`t` 和`t.lexer` 中
```python    
import ply.lex as lex  

##### 规则定义，重要 #####

# token 列表，必须的变量   
tokens = (
   'NUMBER',   
   # ...
   'RPAREN',
)  

# 简单的token 定义，变量的形式  
t_RPAREN  = r'\)'

# 复杂的token 定义，包含token 值等动作代码
def t_NUMBER(t):
    r'\d+'  # python 函数中的首行字符串或正则表达式会被赋值给
    # func.__doc__ 词法分析器自动初始化时会用到这个属性  
    t.value = int(t.value)
    return t

# 默认规则：新行
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# 默认规则：忽略，空白和tab  
t_ignore  = ' \t'

# 默认规则：非法字符  
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# 构建词法分析器   
lexer = lex.lex()

##### 测试 #####

# 测试输入
data = '''
3 + 4 * 10
  + -20 *2
'''

lexer.input(data)

# 枚举token 并输出
while True:
    tok = lexer.token()
    if not tok:
        break      # 没有更多输入
    print(tok)
```

### 保留字  
对于保留字，有着自己的规则，应该避免使用上面的定义方式：  
```python
reserved = {
   'if' : 'IF',
   'else' : 'ELSE',
   ...
}

tokens = ['LPAREN','RPAREN',...,'ID'] + list(reserved.values())

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # 查找保留字表
    # 或者查找符号表  
    # t.value = (t.value, symbol_lookup(t.value))
    return t
```

### 丢弃token  
可以定义一个无返回值的token，或者通过`ignore_` 前缀来定义：  
```python  
# 第一种方式  
def t_COMMENT(t):
    r'\#.*'
    pass # 注释，无返回值  

# 第二种方式  
t_ignore_COMMENT = r'\#.*'
```   

### 行列信息   
```python  
# 在换行时，将词法分析器的行号增加  
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# 计算列信息：用时再说  
def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1
```  

### 字面字符   
字面字符的优先级始终是**最低**的，可以通过以下规则来定义：  
```python
# 定义  
literals = [ '+','-','*','/' ]  
# 或者  
literals = "+-*/"  

def t_lbrace(t):
    r'\{'
    t.type = '{'      # 可选，设置token 类型
    return t

def t_rbrace(t):
    r'\}'
    t.type = '}'      
    return t
```  

### EOF  
```python 
# EOF handling rule
def t_eof(t):
    # Get more input (Example)
    more = input('... ')
    if more:
        self.lexer.input(more)
        return self.lexer.token()
    return None
```  

### 装饰器  
可以通过装饰器来修饰token 函数：  
```python  
identifier       = r'(' + nondigit + r'(' + digit + r'|' + nondigit + r')*)'

@TOKEN(identifier)
def t_ID(t):
    ...
```  

### 内部状态  
- `lexer.lexpos` 列号  
- `lexer.lineno` 行号  
- `lexer.lexdata` 当前文本  
- `lexer.lexmatch`  

更高级的用法暂不涉及。  

## 词法分析器工程化  
代码参考：[【Python】Ply 简介](https://www.leyeah.com/article/python-introduction-ply-674897)  

```python
import ply.lex as lex

reserved = {  # 保留字表，仅用于查找用
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
}

tokens = ['NUMBER', 'SELFMINUS', 'MINUS', 'ID'] + list(reserved.values())
literals = ['+', '{', '}', '*', '/']  # 只能是单字符
t_ignore = (" ")

# 优先级：
# 1. 保留字 > tokens > literals
# 2. 函数 > 变量
# 3. 先定义 > 后定义
def t_SELFMINUS(t):
    r'\-\-'
    t.type = "SELFMINUS"
    return t

def t_MINUS(t):
    r'\-'
    t.type = "MINUS"
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# 标识符：包括保留字、符号
def t_ID(t):  # 匹配标识符
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID') # 查找保留字表
    # 或者查找符号表（符号表应该在遍历抽象语法树时构建）
    # t.value = (t.value, symbol_lookup(t.value))
    return t

def t_error(t: lex.LexToken) -> lex.LexToken:
    print(f"Illegal character '{t.value}' in {t.lineno}:{t.lexpos}")
    t.lexer.skip(1)
    
    
data = ''' iF1 else---{}"'''

lexer = lex.lex()
lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)

# # 输出：
# LexToken(ID,'iF1',1,1)
# LexToken(ELSE,'else',1,5)
# LexToken(SELFMINUS,'--',1,9)
# LexToken(MINUS,'-',1,11)
# LexToken({,'{',1,12)
# LexToken(},'}',1,13)
# Illegal character '"' in 1:14
```