import torch
from multipledispatch import dispatch  # type: ignore
from typing import Dict
from spflow.base.memoize import memoize
from spflow.torch.structure.nodes.leaves.parametric import TorchLogNormal


@dispatch(TorchLogNormal, torch.Tensor, cache=dict)
@memoize(TorchLogNormal)
def log_likelihood(leaf: TorchLogNormal, data: torch.Tensor, cache: Dict = {}):
    return leaf(data)
