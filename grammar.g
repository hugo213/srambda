%import common.WS
%ignore WS

%import common.LCASE_LETTER -> LLETTER
%import common.UCASE_LETTER -> ULETTER

ID: LLETTER

NAME: ULETTER ULETTER+
reference: NAME
abstraction: "^" ID "." expression

?application: atom | application (atom | abstraction)

?atom: "(" expression ")"
    | ID
    | reference

?expression: atom | abstraction | application

definition: NAME ":" expression ";"
evaluation: expression ";"

_instruction: evaluation | definition

program: _instruction*
