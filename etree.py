import lark
from parser import die
from typing import Union, List

_variable_names = 'xyzvabcdefghijklmnopqrstuw'


class Node:
    """base class for tree nodes"""
    def __init__(self, children):
        self.children: List[Node] = children
        self.parent = None
        for c in self.children:
            c.parent = self

    def __str__(self):
        return self.__class__.__name__

    def _write(self, depth: int) -> str:
        raise NotImplementedError

    def write(self):
        return self._write(0)

    def pretty(self, spacing=0):
        return '\n'.join([f'{spacing*"| "}{str(self)}'] + [child.pretty(spacing+1) for child in self.children])

    def replace(self, new):  # dirty hack for assigning by reference
        self.__class__ = new.__class__
        for field in new.__dict__.keys():
            v = getattr(new, field)
            if v is not None:
                setattr(self, field, v)


class Abstraction(Node):
    """abstraction node. one children, the body"""
    def __init__(self, children):
        super().__init__(children)
        assert len(self.children) == 1

    def _write(self, depth: int) -> str:
        child = self.children[0]._write(depth + 1)
        if depth >= len(_variable_names):  # fall back to De Bruijn indexing if no names are left
            return f'(^@.{child})'
        else: return f'(^{_variable_names[depth]}.{child})'


class Application(Node):
    """application node. two children, left and right operand"""
    def __init__(self, children):
        super().__init__(children)
        assert len(self.children) == 2

    def _write(self, depth: int) -> str:
        left = self.children[0]._write(depth)
        right = self.children[1]._write(depth)
        return f'({left} {right})'


class Variable(Node):
    """variable reference node. special 'up' field with De Bruijn index of the variable. no children."""
    def __init__(self, children, up=0):
        super().__init__(children)
        assert len(self.children) == 0
        self.up = up

    def _write(self, depth: int) -> str:
        index = depth-self.up-1
        return _variable_names[index] if index < len(_variable_names) else f'@{self.up}'

    def __str__(self):
        return super().__str__() + f'({self.up})'


class DFS:
    def __init__(self, tree: Node):
        self.tree = tree

    def go(self, **kwargs):
        return self._dfs(self.tree, 0, **kwargs)

    def variable(self, node: Variable, depth: int, **kwargs):
        return node

    def abstraction(self, node: Abstraction, depth: int, **kwargs):
        return Abstraction([
            self._dfs(node.children[0], depth + 1)])

    def application(self, node: Application, depth: int, **kwargs):
        return Application([
            self._dfs(node.children[0], depth),
            self._dfs(node.children[1], depth)])

    def _dfs(self, node: Node, depth: int, **kwargs) -> Node:
        if isinstance(node, Variable):
            return self.variable(node, depth, **kwargs)
        elif isinstance(node, Abstraction):
            return self.abstraction(node, depth, **kwargs)
        elif isinstance(node, Application):
            return self.application(node, depth, **kwargs)


def build_etree(lark_tree: lark.Tree) -> Node:
    """builds an expression tree from parse tree of evaluation"""

    def dfs(lark_tree_node: Union[lark.Tree, lark.Token], variables: List[str]):
        """depth-first search to traverse the parse tree. `variables` is a list of variable names from abstraction
        heads on the path from root to the current node, used for De Bruijn indexing."""

        if isinstance(lark_tree_node, lark.Token):  # it's a token, so it must be a variable
            name = str(lark_tree_node)
            try:
                index = variables.index(name)
                return Variable([], up=index)
            except ValueError:
                die(lark_tree_node, f'unresolved variable name {name}')

        assert isinstance(lark_tree_node, lark.Tree)  # if it's not a token, it should be a normal tree node.

        if lark_tree_node.data == 'application':
            return Application([
                dfs(lark_tree_node.children[0], variables),
                dfs(lark_tree_node.children[1], variables)
            ])
        elif lark_tree_node.data == 'abstraction':
            variable_name = str(lark_tree_node.children[0])
            return Abstraction([
                dfs(lark_tree_node.children[1], [variable_name] + variables)
            ])
        die(lark_tree_node, f'parsing error: unknown node type: {lark_tree_node.data}')

    return dfs(lark_tree, [])