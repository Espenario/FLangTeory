grammar Expr;		
prog:	expr EOF ;
expr:   expr '|' expr
    |	NONTERM
    |   expr'*'
    |   expr'+'
    |   expr'?'
    |   '('expr')'
    |   expr expr
    ;
NEWLINE : [\r\n]+ -> skip;
NONTERM : [A-Z]+ ;