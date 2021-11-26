import torch
from multipledispatch import dispatch  # type: ignore
from typing import Dict
from spflow.base.memoize import memoize
from spflow.torch.structure.nodes.leaves.parametric import TorchNegativeBinomial


@dispatch(TorchNegativeBinomial, torch.Tensor, cache=dict)
@memoize(TorchNegativeBinomial)
def log_likelihood(leaf: TorchNegativeBinomial, data: torch.Tensor, cache: Dict = {}):
    return leaf(data)