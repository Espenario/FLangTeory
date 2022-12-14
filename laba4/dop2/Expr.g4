grammar Expr;		
prog:	expr EOF ;
expr:  	TERM
    | '('expr')'
    |   expr'?'
    |   expr'*'
    |   expr'+'
    |   expr expr
    | expr '|' expr
    ;
NEWLINE : [\r\n]+ -> skip;
TERM : [A-Z]+ ;