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
    # 或者查找符号表
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