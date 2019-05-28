import lark
from os import path
from typing import Union
import sys
import networkx
import networkx.exception


def local(p):
    """makes path relative to the __file__ absolute"""
    return path.join(path.dirname(__file__), p)


def die(where: Union[lark.Tree, lark.Token, None], message: str):
    """Prints error message and exits with error code"""
    sys.stderr.write(f'{message}\n')
    try:
        if isinstance(where, lark.Tree): sys.stderr.write(f'(in line {where.meta.line} column {where.meta.column})\n')
        elif isinstance(where, lark.Token): sys.stderr.write(f'(in line {where.line} column {where.column})\n')
    except: pass  # we don't want errors when reporting errors...
    sys.exit(1)


def lark_parse(source) -> lark.Tree:
    """A small wrapper around lark parser. Gets the source code, returns parse tree"""
    parser = lark.Lark(open(local('./grammar.g')).read(), start='program', propagate_positions=True)
    return parser.parse(source)


class DefinitionResolver:

    class DefinitionTransformer(lark.Transformer):
        def __init__(self, name, tree: lark.Tree, *args, **kwargs):
            super().__init__(*args, **kwargs)
            definition = list(tree.find_pred(lambda n: n.data == 'definition' and str(n.children[0]) == name))[0]
            self.body = definition.children[1]
            self.name = str(definition.children[0])

        def reference(self, args):
            return self.body if str(args[0]) == self.name else lark.Tree(data='reference', children=args)

    def __init__(self, tree: lark.Tree):
        self.tree = tree
        self.definitions = list(tree.find_data('definition'))

    def reference_graph(self) -> networkx.DiGraph:

        R = networkx.DiGraph()

        # nodes
        for definition in self.definitions:
            name = str(definition.children[0])
            if name in R.nodes():
                die(definition, f'{name} redeclared')
            R.add_node(name)

        # edges
        for definition in self.definitions:
            name = str(definition.children[0])
            R.add_edges_from(
                [(str(ref.children[0]), name) for ref in definition.find_data('reference')])

        # DAG?
        try:
            cycle = networkx.find_cycle(R)
            history = [e[0] for e in cycle] + [cycle[-1][1]]
            die(None, f'Cyclic reference found. We don\'t do that here.\n{"->".join(history)}')
        except networkx.exception.NetworkXNoCycle: pass

        return R

    def resolve(self) -> lark.Tree:
        R = self.reference_graph()
        tree = self.tree
        for name in networkx.topological_sort(R):
            tree = self.DefinitionTransformer(name, tree).transform(tree)
        return tree
