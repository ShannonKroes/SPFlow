import numpy as np
import torch
import torch.distributions as D
from torch.nn.parameter import Parameter
from typing import List, Tuple
from .parametric import TorchParametricLeaf, proj_bounded_to_real, proj_real_to_bounded
from spflow.base.structure.nodes.leaves.parametric.statistical_types import ParametricType
from spflow.base.structure.nodes.leaves.parametric import Poisson

from multipledispatch import dispatch  # type: ignore


class TorchPoisson(TorchParametricLeaf):
    """(Univariate) Poisson distribution.
    PMF(k) =
        l^k * exp(-l) / k!
    Attributes:
        l:
            Expected value (& variance) of the Poisson distribution (usually denoted as lambda).
    """

    ptype = ParametricType.COUNT

    def __init__(self, scope: List[int], l: float) -> None:

        if(len(scope) != 1):
            raise ValueError(f"Scope size for TorchPoisson should be 1, but was: {len(scope)}")

        super(TorchPoisson, self).__init__(scope)

        # register auxiliary torch parameter for lambda l
        self.l_aux = Parameter()

        # set parameters
        self.set_params(l)

    @property
    def l(self) -> torch.Tensor:
        # project auxiliary parameter onto actual parameter range
        return proj_real_to_bounded(self.l_aux, lb=0.0)  # type: ignore

    @property
    def dist(self) -> D.Distribution:
        return D.Poisson(rate=self.l)

    def forward(self, data: torch.Tensor) -> torch.Tensor:

        batch_size: int = data.shape[0]

        # get information relevant for the scope
        scope_data = data[:, list(self.scope)]

        # initialize empty tensor (number of output values matches batch_size)
        log_prob: torch.Tensor = torch.empty(batch_size, 1)

        # ----- marginalization -----

        # if the scope variables are fully marginalized over (NaNs) return probability 1 (0 in log-space)
        log_prob[torch.isnan(scope_data).sum(dim=1) == len(self.scope)] = 0.0

        # ----- log probabilities -----

        # create Torch distribution with specified parameters
        dist = D.Poisson(rate=self.l)

        # compute probabilities on data samples where we have all values
        prob_mask = torch.isnan(scope_data).sum(dim=1) == 0
        # set probabilities of values outside of distribution support to 0 (-inf in log space)
        support_mask = (scope_data >= 0).sum(dim=1).bool()
        log_prob[prob_mask & (~support_mask)] = -float("Inf")
        # compute probabilities for values inside distribution support
        log_prob[prob_mask & support_mask] = dist.log_prob(scope_data[prob_mask & support_mask])

        return log_prob

    def set_params(self, l: float) -> None:

        if not np.isfinite(l):
            raise ValueError(f"Value of l for Poisson distribution must be finite, but was: {l}")

        self.l_aux.data = proj_bounded_to_real(torch.tensor(float(l)), lb=0.0)

    def get_params(self) -> Tuple[float]:
        return (self.l.data.cpu().numpy(),)  # type: ignore


@dispatch(Poisson)  # type: ignore[no-redef]
def toTorch(node: Poisson) -> TorchPoisson:
    return TorchPoisson(node.scope, *node.get_params())


@dispatch(TorchPoisson)  # type: ignore[no-redef]
def toNodes(torch_node: TorchPoisson) -> Poisson:
    return Poisson(torch_node.scope, *torch_node.get_params())
