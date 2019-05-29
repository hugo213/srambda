from etree import Node, Application, Abstraction, Variable, DFS

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

        class BetaDFS(DFS):

            class FixVariablesDFS(DFS):
                def variable(self, node: Variable, depth: int, add=0, **kwargs):
                    if node.up < depth:
                        return node
                    else:
                        return Variable([], up=node.up + add)

            def variable(self, node: Variable, depth: int, **kwargs):
                if depth == node.up:  # substitution
                    return self.FixVariablesDFS(right).go(add=depth)
                elif depth < node.up:  # reference outside the application
                    return Variable([], up=node.up-1)
                else:  # internal reference
                    return node

        return BetaDFS(left.children[0]).go()

    def reduce(self) -> Node:

        total = 1
        while total > 0:
            total = 0
            Q = [self.etree]
            while len(Q) > 0:
                node = Q.pop(0)
                while isinstance(node, Application) and isinstance(node.children[0], Abstraction):
                    before = node.__class__
                    node.replace(self.beta(node))
                    total += 1
                    if node.__class__ == Abstraction and before != node.__class__ and node.parent is not None:
                        # there might be some work left above, a new abstraction appeared
                        Q = [node.parent] + Q
                        break
                for child in node.children:
                    Q.append(child)

        class EtaDFS(DFS):

            class CheckNoRefs(DFS):
                class RefException(Exception): pass
                def variable(self, node: Variable, depth: int, **kwargs):
                    if node.up == depth: raise self.RefException

            class FixVariablesDFS(DFS):
                def variable(self, node: Variable, depth: int, **kwargs):
                    if node.up > depth: return Variable([], node.up-1)
                    return super().variable(node, depth, **kwargs)

            def try_eta(self, node):

                if not isinstance(node, Abstraction) or not isinstance(node.children[0], Application): return None
                left, right = node.children[0].children
                if not isinstance(right, Variable) or not right.up == 0: return None

                try: self.CheckNoRefs(left).go()
                except self.CheckNoRefs.RefException: return None

                return self.FixVariablesDFS(left).go()

            def abstraction(self, node: Abstraction, depth: int, **kwargs):
                if self.try_eta(node) is not None:
                    return self._dfs(self.try_eta(node), depth, **kwargs)
                else:
                    return super().abstraction(node, depth, **kwargs)

        self.etree = EtaDFS(self.etree).go()

        return self.etree