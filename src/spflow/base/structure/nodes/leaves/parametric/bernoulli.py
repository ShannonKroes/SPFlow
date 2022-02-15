"""
Created on November 6, 2021

@authors: Bennet Wittelsbach, Philipp Deibert
"""

from .parametric import ParametricLeaf
from .statistical_types import ParametricType
from .exceptions import InvalidParametersError
from typing import Optional, Tuple, Dict, List
import numpy as np
from scipy.stats import bernoulli  # type: ignore
from scipy.stats._distn_infrastructure import rv_discrete  # type: ignore

from multipledispatch import dispatch  # type: ignore


class Bernoulli(ParametricLeaf):
    """(Univariate) Binomial distribution

    PMF(k) =
        p   , if k=1
        1-p , if k=0

    Attributes:
        p:
            Probability of success in the range [0,1].
    """

    type = ParametricType.BINARY

    def __init__(self, scope: List[int], p: Optional[float] = None) -> None:
        if len(scope) != 1:
            raise ValueError(
                f"Scope size for {self.__class__.__name__} should be 1, but was: {len(scope)}"
            )

        super().__init__(scope)

        if p is None:
            p = np.random.uniform(0.0, 1.0)

        self.set_params(p)

    def set_params(self, p: float) -> None:

        if p < 0.0 or p > 1.0 or not np.isfinite(p):
            raise ValueError(
                f"Value of p for Bernoulli distribution must to be between 0.0 and 1.0, but was: {p}"
            )

        self.p = p

    def get_params(self) -> Tuple[float]:
        return (self.p,)


@dispatch(Bernoulli)  # type: ignore[no-redef]
def get_scipy_object(node: Bernoulli) -> rv_discrete:
    return bernoulli


@dispatch(Bernoulli)  # type: ignore[no-redef]
def get_scipy_object_parameters(node: Bernoulli) -> Dict[str, float]:
    if node.p is None:
        raise InvalidParametersError(f"Parameter 'p' of {node} must not be None")
    parameters = {"p": node.p}
    return parameters


@dispatch(Bernoulli, np.ndarray, np.ndarray)  # type: ignore[no-redef]
def update_parameters_em(node: Bernoulli, data: np.ndarray, responsibilities: np.ndarray) -> None:
    responsilbility_factor = 1 / np.sum(responsibilities)
    p = responsilbility_factor * (responsibilities.T @ data[:, node.scope])
    node.set_params(p)
