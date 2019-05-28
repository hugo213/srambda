from parser import lark_parse, DefinitionResolver
from etree import build_etree

source = '''
    ZERO: ^f.^x.x;
    SUCC: ^n.^f.^x.f(nfx);
    ADD: ^n.^m.^f.^x.mf(nfx);
    ONE: SUCC ZERO;
    THREE: SUCC SUCC ONE;
    
    ADD ONE THREE;
'''

parse_tree = DefinitionResolver(lark_parse(source)).resolve()

evaluations = [e.children[0] for e in parse_tree.find_data('evaluation')]

for e in evaluations:
    print(e.pretty())
    etree = build_etree(e)
    print(etree.pretty())
