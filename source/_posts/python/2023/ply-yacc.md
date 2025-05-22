---
title: ply-yacc 学习笔记  
date: 2023-04-09
tags:   
    - python    
    - ply
    - 语法分析  
---    

> 在使用yacc 导入token 时，会自动引入lex 的规则，所以不需要在`app.py` 中重复导包  
<!-- more -->
在`yacc` 模块中，可以直接以铁路图的形式定义语法规则，如下：  
```python  
def p_binary_operators(p):
    '''expression : expression '+' term
                  | expression '-' term
       term       : term '*' factor
                  | term '/' factor'''
    # yacc 会根据上面的文档信息和lex 中定义的token 的`value`来自动解析
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]
```
上面代码中`p[0]` 是返回到上层节点的，而`p[n]` 则是词法分析器中获取到的`token` 的值。而**yacc 并不会自动构造AST**，所以需要自己定义一些语法树的节点，并将其赋值给`p[0]`。  

一个简单的例子如下：  
```python
from ply import yacc
from my_lexer import tokens
# 在导入token 时，会自动应用词法分析的规则


## 因为yacc 默认不会构造语法树， 需要手工设置节点信息，并将其传递给p[0] ##
class Node():
    def __init__(self):
        pass

#####  语法树节点类  ######
# 可以单独定义在一个文件中 #  
##########################
class IntNode(Node):
    def __init__(self, token):
        self.token = token

    def __str__(self) -> str:
        return f"InitNode:({self.token})"


class BinaryNode(Node):
    def __init__(self, left, op, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"BinaryNode:(`{self.op}`:<{self.left},{self.right}>)"


#####  语法规则  #####
def p_factor_int(p):
    'factor : INT'
    p[0] = IntNode(p[1])

def p_term_mul(p):
    'term : factor MUL factor'
    p[0] = BinaryNode(p[1], p[2], p[3])

def p_expression_add(p):
    'expression : term ADD term'
    p[0] = BinaryNode(p[1], p[2], p[3])

def p_error(p):
    print('syntax error')


# 创建解释器，并指定入口规则
parser = yacc.yacc(start='expression')  


#####  调试  #####
from my_parser import parser

data = "1*1+1*1"
res = parser.parse(data)
print(res)
# BinaryNode:(`+`:<BinaryNode:(`*`:<InitNode:(1),InitNode:(1)>),BinaryNode:(`*`:<InitNode:(1),InitNode:(1)>)>)
```

在定义语法规则时一开始可以将规则分的非常细，因为如果一开始就合并一些语法规则的话，可能会引入一些语法二义性的问题，比如运算优先级的问题。如果一开始定义语法规则时比较细，然后按优先级进行合并，则可以较好的避免这个问题。    

## 空规则  
空规则可以在匹配可选的规则时比较有用：  
```python  
# 定义空规则  
def p_empty(p):  
    'empty :'  
    pass    

# 使用空规则  
def p_term(p):  
    '''term : factor empty
            | MUL factor
            | DIV factor'''
    ...  
```

## 递归  
似乎`yacc` 的模块介绍时只有简单的的规则，不包含无限长的可能性，这样可以通过组合简单的语法来构造语法树。下面就是一个支持括号的四则运算的语法规则，不包括负号的解析：  
```python  
def p_empty(p):
    'empty :'
    pass


def p_factor(p):
    '''factor : INT
              | LPAREN expression RPAREN'''
    if p[1] == "(":
        p[0] = p[2]
    else:
        p[0] = IntNode(p[1])


def p_term(p):
    '''term : factor empty
            | term MUL term
            | term DIV term'''
    if p[2] in ['*', '/']:
        p[0] = BinaryNode(p[1], p[2], p[3])
    else:
        p[0] = p[1]


def p_expression_add(p):
    '''expression : term empty
                  | expression ADD expression
                  | expression SUB expression'''
    if p[2] in ['+', '-']:
        p[0] = BinaryNode(p[1], p[2], p[3])
    else:
        p[0] = p[1]
```

## 处理符号  
因为正负号的优先级是介于乘法和加法运算之间的，所以可以通过新增一条符号运算的规则来进行解析：  
```python  
# 单目运算符类
class UnaryNode(Node):
    def __init__(self, sign, token):
        self.sign = sign
        self.token = token

    def __str__(self) -> str:
        return f"UnaryNode:(`{self.sign}`:<{self.token}>)"

def p_sign(p):
    '''sign : term empty  
            | ADD term  
            | SUB term'''
    # 如果替换为下面这个规则，就可以处理`1------------1` 这种表达式了       
    # '''sign : term empty  
    #         | ADD sign  
    #         | SUB sign'''
    if p[1] in ['-', '+']:
        p[0] = UnaryNode(p[1], p[2])
    else:
        p[0] = p[1]


def p_expression_add(p):
    '''expression : sign empty
                  | expression ADD expression
                  | expression SUB expression'''
    if p[2] in ['+', '-']:
        p[0] = BinaryNode(p[1], p[2], p[3])
    else:
        p[0] = p[1]
```

`yacc` 在运行时会生成`parser.out` 和`parsetab.py` 文件，可以帮助对照检查一些可能的错误。其实语法分析阶段蛮考验递归的思维能力的。有或没有、一个或多个该怎么去描述。  

## 行号  
- `p.lineno(num)`返回第num个符号的行号
- `p.lexpos(num)`返回第num个符号的词法位置偏移

> 同样优先级的运算，总是向右结合。例如`1+1-1` 会先构造右边，和习惯上不一样:)