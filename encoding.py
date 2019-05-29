from etree import Node, Abstraction, Application, Variable
from typing import Union


class DecodeException(Exception): pass


def decode_numeral(tree : Node) -> int:

    def _assert(e):
        if not e: raise DecodeException

    _assert(isinstance(tree, Abstraction))
    _assert(isinstance(tree.children[0], Abstraction))

    tree = tree.children[0].children[0]

    result = 0

    while isinstance(tree, Application):
        left, right = tree.children
        _assert(isinstance(left, Variable) and left.up == 1)
        result += 1
        tree = right

    _assert(isinstance(tree, Variable) and tree.up == 0)
    return result