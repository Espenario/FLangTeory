grammar Expr_art;		
re: TERM | re '|' re | re re | re'?' | re'*' | re'+' EOF;
TERM: [a-zA-Z]+ ;
WS: [ \t\n\r\f]+ -> skip ;