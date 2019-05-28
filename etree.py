import lark
from parser import die
from typing import Union, List


class Node:
    """base class for tree nodes"""
    def __init__(self, children):
        self.children = children

    def __str__(self):
        return self.__class__.__name__

    def pretty(self, spacing=0):
        return '\n'.join([f'{spacing*" "}{str(self)}'] + [child.pretty(spacing+1) for child in self.children])


class Abstraction(Node):
    """abstraction node. one children, the body"""
    def __init__(self, children):
        super().__init__(children)
        assert len(self.children) == 1


class Application(Node):
    """application node. two children, left and right operand"""
    def __init__(self, children):
        super().__init__(children)
        assert len(self.children) == 2


class Variable(Node):
    """variable reference node. special 'up' field with De Bruijn index of the variable. no children."""
    def __init__(self, children, up=0):
        super().__init__(children)
        assert len(self.children) == 0
        self.up = up

    def __str__(self):
        return super().__str__() + f'({self.up})'


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