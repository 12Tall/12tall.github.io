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