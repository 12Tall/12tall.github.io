
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'expressionADD DIV INT LPAREN MUL RPAREN SUBempty :factor : INT\n              | LPAREN expression RPARENterm : factor empty\n            | term MUL term\n            | term DIV termsign : term empty  \n            | ADD sign  \n            | SUB signexpression : sign empty\n                  | expression ADD expression\n                  | expression SUB expression'
    
_lr_action_items = {'ADD':([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23,],[3,9,-1,3,3,-1,-1,-2,3,3,3,-10,-8,-9,-7,-4,9,9,9,-5,-6,-3,]),'SUB':([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23,],[4,10,-1,4,4,-1,-1,-2,4,4,4,-10,-8,-9,-7,-4,10,10,10,-5,-6,-3,]),'INT':([0,3,4,8,9,10,15,16,],[7,7,7,7,7,7,7,7,]),'LPAREN':([0,3,4,8,9,10,15,16,],[8,8,8,8,8,8,8,8,]),'$end':([1,2,5,6,7,11,12,13,14,17,19,20,21,22,23,],[0,-1,-1,-1,-2,-10,-8,-9,-7,-4,-11,-12,-5,-6,-3,]),'RPAREN':([2,5,6,7,11,12,13,14,17,18,19,20,21,22,23,],[-1,-1,-1,-2,-10,-8,-9,-7,-4,23,-11,-12,-5,-6,-3,]),'MUL':([5,6,7,17,21,22,23,],[15,-1,-2,-4,15,15,-3,]),'DIV':([5,6,7,17,21,22,23,],[16,-1,-2,-4,16,16,-3,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,8,9,10,],[1,18,19,20,]),'sign':([0,3,4,8,9,10,],[2,12,13,2,2,2,]),'term':([0,3,4,8,9,10,15,16,],[5,5,5,5,5,5,21,22,]),'factor':([0,3,4,8,9,10,15,16,],[6,6,6,6,6,6,6,6,]),'empty':([2,5,6,],[11,14,17,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('empty -> <empty>','empty',0,'p_empty','my_parser.py',40),
  ('factor -> INT','factor',1,'p_factor','my_parser.py',45),
  ('factor -> LPAREN expression RPAREN','factor',3,'p_factor','my_parser.py',46),
  ('term -> factor empty','term',2,'p_term','my_parser.py',54),
  ('term -> term MUL term','term',3,'p_term','my_parser.py',55),
  ('term -> term DIV term','term',3,'p_term','my_parser.py',56),
  ('sign -> term empty','sign',2,'p_sign','my_parser.py',64),
  ('sign -> ADD sign','sign',2,'p_sign','my_parser.py',65),
  ('sign -> SUB sign','sign',2,'p_sign','my_parser.py',66),
  ('expression -> sign empty','expression',2,'p_expression_add','my_parser.py',74),
  ('expression -> expression ADD expression','expression',3,'p_expression_add','my_parser.py',75),
  ('expression -> expression SUB expression','expression',3,'p_expression_add','my_parser.py',76),
]