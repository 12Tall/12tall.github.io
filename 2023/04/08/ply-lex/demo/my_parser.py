from ply import yacc
from my_lexer import tokens
# 在导入token 时，会自动应用词法分析的规则


## 因为yacc 默认不会构造语法树， 需要手工设置节点信息，并将其传递给p[0] ##
class Node():
    def __init__(self):
        pass


class IntNode(Node):
    def __init__(self, token):
        self.token = token

    def __str__(self) -> str:
        return f"IntNode:({self.token})"


class BinaryNode(Node):
    def __init__(self, left, op, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"BinaryNode:(`{self.op}`:<{self.left},{self.right}>)"


class UnaryNode(Node):
    def __init__(self, sign, token):
        self.sign = sign
        self.token = token

    def __str__(self) -> str:
        return f"UnaryNode:(`{self.sign}`:<{self.token}>)"


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


def p_sign(p):
    '''sign : term empty  
            | ADD sign  
            | SUB sign'''
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


def p_error(p):
    print('syntax error')


# 创建解释器，并指定入口规则
parser = yacc.yacc(start='expression')
