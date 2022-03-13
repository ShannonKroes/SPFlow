"""
Created on May 05, 2021

@authors: Kevin Huy Nguyen, Bennet Wittelsbach

This file provides the basic components to build abstract probabilistic circuits, like ISumNode, IProductNode,
and ILeafNode.
"""

from re import I
from typing import List, Tuple, cast, Callable, Set, Type, Deque, Optional, Dict, Union
from multipledispatch import dispatch  # type: ignore
import numpy as np
import collections
from collections import deque, OrderedDict


class INode:
    """Base class for all types of nodes in an SPN

    Attributes:
        children:
            A list of INodes containing the children of this INode, or None.
        scope:
            A list of integers containing the scopes of this INode, or None.
        value:
            A float representing the value of the node. nan-value represents a node, with its value not calculated yet.
    """

    def __init__(self, children: List["INode"], scope: List[int]) -> None:
        self.children = children
        self.scope = scope
        self.value: float = np.nan
        self.id: int = -1

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.scope}"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return 1

    def print_treelike(self, prefix: str = "") -> None:
        """
        Ad-hoc method to print structure of node and children (for debugging purposes).
        """
        print(prefix + f"{self.__class__.__name__}: {self.scope}")

        for child in self.children:
            child.print_treelike(prefix=prefix + "    ")

    def equals(self, other: "INode") -> bool:
        """
        Checks whether two objects are identical by comparing their class, scope and children (recursively).
        """
        return (
            type(self) is type(other)
            and self.scope == other.scope
            and all(map(lambda x, y: x.equals(y), self.children, other.children))
        )


class IProductNode(INode):
    """A Internal ProductNode provides a factorization of its children,
    i.e. IProductNodes in SPNs have children with distinct scopes"""

    def __init__(self, children: List[INode], scope: List[int]) -> None:
        super().__init__(children=children, scope=scope)


class ISumNode(INode):
    """An Internal SumNode provides a weighted mixture of its children,
    i.e. ISumNodes in SPNs have children with identical scopes

    Args:
        weights:
            A np.array of floats assigning a weight value to each of the encapsulated ISumNode's children.

    """

    def __init__(self, children: List[INode], scope: List[int], weights: np.ndarray = None) -> None:
        super().__init__(children=children, scope=scope)

        if weights is None:
            weights = np.random.rand(sum(len(child) for child in children)) + 1e-08  # avoid zeros
            weights /= weights.sum()

        self.weights = weights

    def equals(self, other: INode) -> bool:
        """
        Checks whether two objects are identical by comparing their class, scope, children (recursively) and weights.
        Note that weight comparison is done approximately due to numerical issues when conversion between graph
        representations.
        """
        if type(other) is ISumNode:
            other = cast(ISumNode, other)
            return (
                super().equals(other)
                and np.allclose(self.weights, other.weights, rtol=1.0e-5)
                and self.weights.shape == other.weights.shape
            )
        else:
            return False


class ILeafNode(INode):
    """A Internal LeafNode provides a probability distribution over the random variables in its scope"""

    def __init__(self, scope: List[int]) -> None:
        super().__init__(children=[], scope=scope)


@dispatch(list)  # type: ignore[no-redef]
def _print_node_graph(root_nodes: List[INode]) -> None:
    """Prints all unique nodes of a node graph in BFS fashion.

    Args:
        root_nodes:
            A list of Nodes that are the roots/outputs of the (perhaps multi-class) SPN.
    """
    nodes: List[INode] = list(root_nodes)
    while nodes:
        node: INode = nodes.pop(0)
        print(node)
        nodes.extend(list(set(node.children) - set(nodes)))


@dispatch(INode)  # type: ignore[no-redef]
def _print_node_graph(root_node: INode) -> None:
    """Wrapper for SPNs with single root node"""
    _print_node_graph([root_node])


@dispatch(list)  # type: ignore[no-redef]
def _get_node_counts(root_nodes: List[INode]) -> Tuple[int, int, int]:
    """Count the # of unique internal ISumNodes, IProductNodes, ILeafNodes in an SPN with arbitrarily many root nodes.

    Args:
        root_nodes:
            A list of INodes that are the roots/outputs of the (perhaps multi-class) SPN.
    """
    nodes: List[INode] = root_nodes.copy()
    n_sumnodes = 0
    n_productnodes = 0
    n_leaves = 0

    while nodes:
        node: INode = nodes.pop(0)
        if type(node) is ISumNode:
            n_sumnodes += 1
        elif type(node) is IProductNode:
            n_productnodes += 1
        elif isinstance(node, ILeafNode):
            n_leaves += 1
        else:
            raise ValueError("Node must be ISumNode, IProductNode, or ILeafNode")
        nodes.extend(list(set(node.children) - set(nodes)))

    return n_sumnodes, n_productnodes, n_leaves


@dispatch(INode)  # type: ignore[no-redef]
def _get_node_counts(root_node: INode) -> Tuple[int, int, int]:
    """Wrapper for SPNs with single root node"""
    return _get_node_counts([root_node])


@dispatch(list)  # type: ignore[no-redef]
def _get_leaf_nodes(root_nodes: List[INode]) -> List[INode]:
    """Returns a list of leaf nodes to populate.

    Args:
        root_nodes:
            A list of INodes that are the roots/outputs of the (perhaps multi-class) SPN.
    """
    nodes: List[INode] = root_nodes.copy()
    leaves: List[INode] = []
    id_counter = 0
    while nodes:
        node: INode = nodes.pop(0)
        if issubclass(type(node), ILeafNode):
            leaves.append(node)
        extension = node.children.copy()
        for rem in nodes:
            if rem in node.children:
                extension.remove(rem)
        nodes.extend(extension)
        id_counter += 1
    return leaves


@dispatch(INode)  # type: ignore[no-redef]
def _get_leaf_nodes(root_node: INode) -> List[INode]:
    """Wrapper for SPNs with single root node"""
    return _get_leaf_nodes([root_node])


########################################################################################################################
# multi für single vs multiple root nodes?
def bfs(root: INode, func: Callable):
    """Iterates through SPN in breadth first order and calls func on all nodes in SPN.

    Args:
        root:
            SPN root node.
        func:
            function to call on all the nodes.
    """

    seen: Set = {root}
    queue: Deque[INode] = collections.deque([root])
    while queue:
        node = queue.popleft()
        func(node)
        if not isinstance(node, ILeafNode):
            for c in node.children:
                if c not in seen:
                    seen.add(c)
                    queue.append(c)


def get_nodes_by_type(node: INode, ntype: Union[Type, Tuple[Type, ...]] = INode) -> List[INode]:
    """Iterates SPN in breadth first order and collects nodes of type ntype..

    Args:
        node:
            SPN root node.
        ntype:
            Type of nodes to get. If not specified it will look for any node.

    Returns: List of nodes in SPN which fit ntype.
    """
    assert node is not None
    result: List[INode] = []

    def add_node(node):
        if isinstance(node, ntype):
            result.append(node)

    bfs(node, add_node)
    return result


def get_topological_order(node: INode) -> List[INode]:
    """
    Evaluates the spn bottom up using functions specified for node types.

    Args:
        node:
            SPN root node.

    Returns: List of nodes in SPN in their order specified by their structure.
    """
    nodes: List[INode] = get_nodes_by_type(node)

    parents: "OrderedDict[INode, List]" = OrderedDict({node: []})
    in_degree: "OrderedDict[INode, int]" = OrderedDict()
    for n in nodes:
        in_degree[n] = in_degree.get(n, 0)
        if not isinstance(n, ILeafNode):
            for c in n.children:
                parent_list: Optional[List[Optional[INode]]] = parents.get(c, None)
                if parent_list is None:
                    parents[c] = parent_list = []
                parent_list.append(n)
                in_degree[n] += 1

    S: Deque = deque()  # Set of all nodes with no incoming edge
    for u in in_degree:
        if in_degree[u] == 0:
            S.appendleft(u)

    L: List[INode] = []  # Empty list that will contain the sorted elements

    while S:
        n = S.pop()  # remove a node n from S
        L.append(n)  # add n to tail of L

        for m in parents[n]:  # for each node m with an edge e from n to m do
            in_degree_m: int = in_degree[m] - 1  # remove edge e from the graph
            in_degree[m] = in_degree_m
            if in_degree_m == 0:  # if m has no other incoming edges then
                S.appendleft(m)  # insert m into S

    assert len(L) == len(nodes), "Graph is not DAG, it has at least one cycle"
    return L


def eval_spn_bottom_up(
    node: INode,
    eval_functions: Dict[Type, Callable],
    all_results: Optional[Dict[INode, np.ndarray]] = None,
    **args,
) -> np.ndarray:
    """
    Evaluates the spn bottom up using functions specified for node types.

    Args:
        node:
            SPN root node.
        eval_functions:
            dictionary that contains k: Class of the node, v: lambda function that receives as parameters (node, args**)
            for leaf nodes and (node, [children results], args**) for other nodes.
        all_results: dictionary that contains k: node, v: result of evaluation of the lambda
                        function for that node. Used to store intermediate results so non-tree graphs can be
                        computed in O(n) size of the network.
        args: free parameters that will be fed to the lambda functions.

    Returns: Result of computing and propagating all the values through the network.
    """

    nodes: List[INode] = get_topological_order(node)

    if all_results is None:
        all_results = {}
    else:
        all_results.clear()
    node_type_eval_func_dict: Dict[Type, List[Callable]] = {}
    node_type_is_leaf_dict: Dict[Type, bool] = {}
    for node_type, func in eval_functions.items():
        if node_type not in node_type_eval_func_dict:
            node_type_eval_func_dict[node_type] = []
        node_type_eval_func_dict[node_type].append(func)
        node_type_is_leaf_dict[node_type] = issubclass(node_type, ILeafNode)
    leaf_func: Optional[Callable] = eval_functions.get(ILeafNode, None)

    tmp_children_list: List[Optional[np.ndarray]] = []
    len_tmp_children_list: int = 0
    for n in nodes:
        try:
            func = node_type_eval_func_dict[type(n)][-1]
            n_is_leaf: bool = node_type_is_leaf_dict[type(n)]
        except:
            if isinstance(n, ILeafNode) and leaf_func is not None:
                func = leaf_func
                n_is_leaf = True
            else:
                raise AssertionError(
                    "No lambda function associated with type: %s" % type(n).__name__
                )

        if n_is_leaf:
            result: np.ndarray = func(n, **args)
        else:
            len_children: int = len(n.children)
            if len_tmp_children_list < len_children:
                tmp_children_list.extend([None] * len_children)
                len_tmp_children_list = len(tmp_children_list)
            for i in range(len_children):
                ci: INode = n.children[i]
                tmp_children_list[i] = all_results[ci]
            result = func(n, tmp_children_list[0:len_children], **args)
        all_results[n] = result

    for node_type, func in eval_functions.items():
        del node_type_eval_func_dict[node_type][-1]
        if len(node_type_eval_func_dict[node_type]) == 0:
            del node_type_eval_func_dict[node_type]
    return all_results[node]


def get_topological_order_layers(node: INode) -> List[List[INode]]:
    """
    Returns the nodes in their topological ordering starting from the bottom to the top layers.

    Args:
        node:
            SPN root node.

    Returns: List containing lists of nodes each representing a layer.
    """
    nodes: List[INode] = get_nodes_by_type(node)

    parents: "OrderedDict[INode, List]" = OrderedDict({node: []})
    in_degree: "OrderedDict[INode, int]" = OrderedDict()
    for n in nodes:
        in_degree[n] = in_degree.get(n, 0)
        if not isinstance(n, ILeafNode):
            for c in n.children:
                parent_list: Optional[List[Optional[INode]]] = parents.get(c, None)
                if parent_list is None:
                    parents[c] = parent_list = []
                parent_list.append(n)
                in_degree[n] += 1

    # create list of all nodes with no incoming edge
    layer: List[INode] = []
    for u in in_degree:
        if in_degree[u] == 0:
            layer.append(u)

    # add first layer
    L: List[List[INode]] = [layer]

    added_nodes: int = len(layer)
    while True:
        layer = []

        for n in L[-1]:
            for m in parents[n]:  # for each node m with an edge e from n to m do
                in_degree_m: int = in_degree[m] - 1  # remove edge e from the graph
                in_degree[m] = in_degree_m
                if in_degree_m == 0:  # if m has no other incoming edges then
                    layer.append(m)  # insert m into layer

        if len(layer) == 0:
            break

        added_nodes += len(layer)
        L.append(layer)

    assert added_nodes == len(nodes), "Graph is not DAG, it has at least one cycle"
    return L


def eval_spn_top_down(
    root: INode,
    eval_functions: Dict[Type, Callable],
    all_results: Optional[Dict[INode, List]] = None,
    parent_result: Optional[np.ndarray] = None,
    **args,
) -> List:
    """
    Evaluates an spn top to down using functions specified for node types.

    Args:
        root:
            SPN root node.
        eval_functions:
            dictionary that contains k: Class of the node, v: lambda function that receives as
            parameters (node, args**) for leaf nodes and (node, [children results], args**) for other nodes.
        all_results: dictionary that contains k: node, v: result of evaluation of the lambda
                        function for that node. Used to store intermediate results so non-tree graphs can be
                        computed in O(n) size of the network.
        parent_result: initial input to the root node.
        args: free parameters that will be fed to the lambda functions.

    Returns: Result of computing and propagating all the values through the network.
    """

    if all_results is None:
        all_results = {}
    else:
        all_results.clear()

    all_results[root] = [parent_result]
    leaf_func: Optional[Callable] = eval_functions.get(ILeafNode, None)

    for layer in reversed(get_topological_order_layers(root)):
        for n in layer:
            if isinstance(n, ILeafNode) and leaf_func is not None:
                try:
                    func: Callable = leaf_func
                except:
                    raise AssertionError(
                        "No lambda function associated with type: %s" % type(n).__name__
                    )
            else:
                func = eval_functions[type(n)]

            params: Optional[List] = all_results[n]
            result: Optional[Dict[INode, np.ndarray]] = func(n, params, **args)

            if result is not None and not isinstance(n, ILeafNode):
                for child, param in result.items():
                    if child not in all_results:
                        all_results[child] = []
                    all_results[child].append(param)
    return all_results[root]


def set_node_ids(root: INode) -> None:
    """Set node IDs in the SPN by counting the nodes.
    
    Args: 
        root: The root node of the SPN.

    Returns: None
    """
    i = 0
    for node in get_topological_order(root):
        node.id = i
        i += 1
