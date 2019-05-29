from parser import lark_parse, DefinitionResolver
from etree import build_etree
from reductor import BasicReductor
from encoding import DecodeException, decode_numeral
source = '''
    ZERO: ^f.^x.x;
    SUCC: ^n.^f.^x.f(nfx);
    ADD: ^m.^n.^f.^x. (mf)(nfx);
    THREE: SUCC(SUCC(SUCC(ZERO)));
    FOUR: SUCC(THREE);
    
    ADD THREE FOUR;
'''

parse_tree = DefinitionResolver(lark_parse(source)).resolve()

evaluations = [e.children[0] for e in parse_tree.find_data('evaluation')]

for e in evaluations:
    etree = build_etree(e)
    result = BasicReductor(etree).reduce()

    print(result.write())

    try: print(f'(Church numeral {decode_numeral(result)})')
    except DecodeException: pass
