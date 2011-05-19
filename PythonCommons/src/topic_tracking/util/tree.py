class HierarchicalDict(object):
    """Wrapper for dictionary objects that uses multi-level keys.
    
    The dictionary hierarchy is made of elements of the form:
    D[atom_1][atom_2]...[atom_3] = leaf
    """

    @staticmethod
    def __default_is_leaf(node):
        """Default function for testing if a node is a leaf."""

        return not isinstance(node, dict)

    def __init__(self, root=None, factory=dict, is_leaf=None):
        """
        @param root: the dictionary on the first level
        @param factory: factory used to create new levels
        @param is_leaf: function used to check if a node is a leaf
        """

        if root is None:
            root = factory()

        self.root = root
        self.factory = factory

        # leaf testing
        self.is_leaf = self.__default_is_leaf
        if not is_leaf is None:
            self.is_leaf = is_leaf

    def set(self, key, value):
        """Set the value at the specified key.
        
        This method uses the factory to build the missing dictionary levels.
        
        @param key: a tuple of key atoms
        @param value: the value to assign at the given key
        """

        node = self.root
        last_node = None
        last_atom = None
        for k in key:
            if not k in node:
                node[k] = self.factory()
            last_node = node
            last_atom = k
            node = node[k]
        last_node[last_atom] = value

    def get(self, key, default=None):
        """Retrieves the value found at the specified key.
        
        @param key: a tuple of key atoms, forming a full key or a prefix
        @param default: value to be returned if there is no value assigned
            to the key
        """

        node = self.root
        for k in key:
            if k in node and not self.is_leaf(node):
                node = node[k]
            else:
                return default
        return node

    def to_map(self, prefix=None, full_key=False):
        """Creates a flatten map of the hierarchy, where each key is a tuple."""

        if prefix is None:
            prefix = tuple()
        node = self.get(prefix)

        if not full_key:
            prefix = tuple()

        map = {}
        for k, v in self.__iterate_leafs(node, prefix):
            map[k] = v
        return map

    def __iter__(self):
        return self.__iterate_leafs(self.root, [])

    def __iterate_leafs(self, node, prefix):
        if self.is_leaf(node):
            yield (tuple(prefix), node)
        else:
            for k, v in node.iteritems():
                p = list(prefix)
                p.append(k)
                for i in self.__iterate_leafs(v, p):
                    yield i


if __name__ == '__main__':
    tree = HierarchicalDict()
    tree.set((1, 1, 1, 1), 'a')
    tree.set((1, 2), 'b')
    tree.set((2, 1), 'c')
    print(tree.root)
    print(tree.get((1,)))
    gen = (i for i in (1, 1, 1))
    print(tree.get(gen))
    print(tree.to_map((1, 1)))
    print(tree.to_map((1, 1), full_key=True))

    print('iterator:')
    for i in tree:
        print(i)

