from etree import Node, Application, Abstraction, Variable

class Reductor:
    def __init__(self, etree: Node):
        self.etree = etree

    def reduce(self) -> Node:
        raise NotImplementedError


class BasicReductor(Reductor):

    def beta(self, app: Application) -> Node:

        left: Node = app.children[0]
        right: Node = app.children[1]
        assert isinstance(left, Abstraction)

        def dfs(node: Node, depth: int) -> Node:
            if isinstance(node, Variable):
                if isinstance(right, Variable):
                    if depth == node.up:
                        return Variable([], up=right.up+depth)
                    elif depth < node.up:
                        node.up -= 1
                        return node
                    else: return node
                else:
                    return right if depth == node.up else node
            elif isinstance(node, Abstraction):
                return Abstraction([
                    dfs(node.children[0], depth+1)])
            elif isinstance(node, Application):
                return Application([
                    dfs(node.children[0], depth),
                    dfs(node.children[1], depth)])

        r = dfs(left.children[0], 0)
        return r

    def reduce(self) -> Node:

        Q = [self.etree]

        while len(Q) > 0:
            node = Q.pop(0)
            while isinstance(node, Application) and isinstance(node.children[0], Abstraction):
                before = node.__class__
                node.replace(self.beta(node))
                if node.__class__ == Abstraction and before != node.__class__ and node.parent is not None:
                    # there might be some work left above, a new abstraction appeared
                    Q = [node.parent] + Q
                    break
            for child in node.children:
                Q.append(child)

        return self.etree