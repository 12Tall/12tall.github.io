from my_parser import parser


# data = """(1+2)*3+4
# *5"""

data = "1-1+1"
# lexer.input(data)

res = parser.parse(data)

print(res)

# BinaryNode:(
#   `-`:
#       <IntNode:(1),
#       BinaryNode:(
#           `+`:
#               <BinaryNode:(
#                   `*`:
#                       <IntNode:(2),
#                        IntNode:(3)>),
#               UnaryNode:(
#                   `-`:<IntNode:(1)>
#               )
#           >)
#       >)