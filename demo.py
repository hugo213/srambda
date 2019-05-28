from parser import lark_parse, DefinitionResolver
from etree import build_etree
from reductor import BasicReductor

source = '''
    ZERO: ^f.^x.x;
    SUCC: ^n.^f.^x.f(nfx);
    SUCC ( SUCC ( SUCC ZERO ) );
'''

parse_tree = DefinitionResolver(lark_parse(source)).resolve()

evaluations = [e.children[0] for e in parse_tree.find_data('evaluation')]

for e in evaluations:
    print(e.pretty())
    etree = build_etree(e)
    tree2 = BasicReductor(etree).reduce()
    print('RESULT', tree2.pretty())