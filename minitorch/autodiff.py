from dataclasses import dataclass
from typing import Any, Iterable, List, Tuple

from typing_extensions import Protocol
import pdb 

def central_difference(f: Any, *vals: Any, arg: int = 0, epsilon: float = 1e-6) -> Any:
    r"""
    Computes an approximation to the derivative of `f` with respect to one arg.

    See :doc:`derivative` or https://en.wikipedia.org/wiki/Finite_difference for more details.

    Args:
        f : arbitrary function from n-scalar args to one value
        *vals : n-float values $x_0 \ldots x_{n-1}$
        arg : the number $i$ of the arg to compute the derivative
        epsilon : a small constant

    Returns:
        An approximation of $f'_i(x_0, \ldots, x_{n-1})$
    """
    vals1 = [v for v in vals]
    vals2 = [v for v in vals]
    vals1[arg] = vals1[arg] + epsilon
    vals2[arg] = vals2[arg] - epsilon
    delta = f(*vals1) - f(*vals2)
    return delta / (2 * epsilon)


variable_count = 1


class Variable(Protocol):
    def accumulate_derivative(self, x: Any) -> None:
        """
        Accumulates the derivative (gradient) for this Variable.

        Args:
            x (Any): The gradient value to be accumulated.
        """
        pass

    @property
    def unique_id(self) -> int:
        """
        Returns:
            int: The unique identifier of this Variable.
        """
        pass

    def is_leaf(self) -> bool:
        """
        Returns whether this Variable is a leaf node in the computation graph.

        Returns:
            bool: True if this Variable is a leaf node, False otherwise.
        """
        pass

    def is_constant(self) -> bool:
        """
        Returns whether this Variable represents a constant value.

        Returns:
            bool: True if this Variable is constant, False otherwise.
        """
        pass

    @property
    def parents(self) -> Iterable["Variable"]:
        """
        Returns the parent Variables of this Variable in the computation graph.

        Returns:
            Iterable[Variable]: The parent Variables of this Variable.
        """
        pass

    def chain_rule(self, d_output: Any) -> Iterable[Tuple["Variable", Any]]:
        """
        Implements the chain rule to compute the gradient contributions of this Variable.

        Args:
            d_output (Any): The gradient of the output with respect to the Variable.

        Returns:
            Iterable[Tuple[Variable, Any]]: An iterable of tuples, where each tuple
                contains a parent Variable and the corresponding gradient contribution.
        """
        pass


def topological_sort(variable: Variable) -> Iterable[Variable]:
    """
    Computes the topological order of the computation graph.

    Args:
        variable: The right-most variable

    Returns:
        Non-constant Variables in topological order starting from the right.
    """
    # BEGIN ASSIGN1_1
    # TODO
    topoList = []
    visited = []
    def explore(u, topoList):
        visited.append(u.unique_id)
        if u.is_constant():
            return
        if u.is_leaf():
            topoList.append(u)
            return
        
        
        for v in u.parents:
            if v.unique_id == u.unique_id:
                continue
            if v.unique_id not in visited:
                explore(v, topoList) 
        if not u.is_constant():
            topoList.append(u)
        return
    explore(variable, topoList)
    return topoList[::-1]
    # END ASSIGN1_1

def backpropagate(variable: Variable, deriv: Any) -> None:
    """
    Runs backpropagation on the computation graph in order to
    compute derivatives for the leave nodes.

    Args:
        variable: The right-most variable
        deriv  : Its derivative that we want to propagate backward to the leaves.

    No return. Should write to its results to the derivative values of each leaf through `accumulate_derivative`.
    """
    # BEGIN ASSIGN1_1
    # TODO
    
    def add_grad(prev_grad, grad):
        if prev_grad is None:
            return grad
        else:
            return prev_grad + grad
    def find_index(node):
        return topoID.index(node.unique_id)
    def verify_no_constant_node(topoList):
        for node in topoList:
            assert not node.is_constant()
            
    topoList = topological_sort(variable)
    topoID = [node.unique_id for node in topoList]
    gradList = [None for node in topoList]
    gradList[find_index(variable)] = deriv
    leafNodes = []
    verify_no_constant_node(topoList)
    for node in topoList:
        if node.is_leaf():
            leafNodes.append(node)
        else:
            outgrad = gradList[find_index(node)]
            assert (outgrad is not None)
            parentGradIter = node.chain_rule(outgrad)
            for parentnode, parentgrad in parentGradIter:
                if (parentnode.is_constant()):
                    continue
                parentgrad = add_grad(gradList[find_index(parentnode)], parentgrad)
                gradList[find_index(parentnode)] = parentgrad
                
    for node in leafNodes:
        node.accumulate_derivative(gradList[find_index(node)])


@dataclass
class Context:
    """
    Context class is used by `Function` to store information during the forward pass.
    """

    no_grad: bool = False
    saved_values: Tuple[Any, ...] = ()

    def save_for_backward(self, *values: Any) -> None:
        "Store the given `values` if they need to be used during backpropagation."
        if self.no_grad:
            return
        self.saved_values = values

    @property
    def saved_tensors(self) -> Tuple[Any, ...]:
        return self.saved_values
