import ply.lex as lex

reserved = {}

tokens = ["INT", "ADD", "SUB", "MUL", "DIV", "LPAREN", "RPAREN"]

# t_ignore 必须是变量的形式定义
t_ignore = r' \t'


def t_error(t: lex.LexToken):
    print(f"Illegal character `{t.value}`, at({t.lineno},{t.lexpos})")
    t.lexer.skip(1)


def t_newline(t: lex.LexToken):
    r'\n+'
    # LEX 不会自动更新行和列信息
    # 读取到换行时需要手动调整行号增加
    # 可以在其他规则里面添加记录列号的功能
    # t.lexer.col += len(t.value)  
    # t.lexer.col = 0
    t.lexer.lineno += len(t.value)

def t_INT(t: lex.LexToken):
    r'\d+'
    t.type = "INT"
    t.value = int(t.value)
    return t


def t_ADD(t: lex.LexToken):
    r'\+'
    return t


def t_SUB(t: lex.LexToken):
    r'\-'
    return t


def t_MUL(t: lex.LexToken):
    r'\*'
    return t


def t_DIV(t: lex.LexToken):
    r'/'
    return t


def t_LPAREN(t: lex.LexToken):
    r'\('
    return t


def t_RPAREN(t: lex.LexToken):
    r'\)'
    return t


lexer = lex.lex()
