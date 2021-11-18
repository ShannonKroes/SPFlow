"""
Created on November 6, 2021

@authors: Bennet Wittelsbach, Philipp Deibert
"""

from .parametric import ParametricLeaf
from .statistical_types import ParametricType
from .exceptions import InvalidParametersError
from typing import Optional, Tuple, Dict, List, Union
import numpy as np
from scipy.stats import binom  # type: ignore
from scipy.stats._distn_infrastructure import rv_discrete  # type: ignore

from multipledispatch import dispatch  # type: ignore


class Binomial(ParametricLeaf):
    """(Univariate) Binomial distribution.

    PMF(k) =
        (n)C(k) * p^k * (1-p)^(n-k), where
            - (n)C(k) is the binomial coefficient (n choose k)

    Attributes:
        n:
            Number of i.i.d. Bernoulli trials (greater of equal to 0).
        p:
            Probability of success of each trial in the range [0,1]
    """

    type = ParametricType.COUNT

    def __init__(
        self, scope: List[int], n: Optional[int] = None, p: Optional[float] = None
    ) -> None:
        if len(scope) != 1:
            raise ValueError(
                f"Scope size for {self.__class__.__name__} should be 1, but was: {len(scope)}"
            )

        super().__init__(scope)

        if n is None:
            n = np.random.randint(1, 11)
        if p is None:
            p = np.random.uniform(0.0, 1.0)

        self.set_params(n, p)

    def set_params(self, n: int, p: float) -> None:

        if p < 0.0 or p > 1.0 or not np.isfinite(p):
            raise ValueError(
                f"Value of p for Binomial distribution must to be between 0.0 and 1.0, but was: {p}"
            )

        if n < 0 or not np.isfinite(n):
            raise ValueError(
                f"Value of n for Binomial distribution must to greater of equal to 0, but was: {n}"
            )

        self.n = n
        self.p = p

    def get_params(self) -> Tuple[int, float]:
        return self.n, self.p


@dispatch(Binomial)  # type: ignore[no-redef]
def get_scipy_object(node: Binomial) -> rv_discrete:
    return binom


@dispatch(Binomial)  # type: ignore[no-redef]
def get_scipy_object_parameters(node: Binomial) -> Dict[str, Union[int, float]]:
    if node.n is None:
        raise InvalidParametersError(f"Parameter 'n' of {node} must not be None")
    if node.p is None:
        raise InvalidParametersError(f"Parameter 'p' of {node} must not be None")
    parameters = {"n": node.n, "p": node.p}
    return parameters
