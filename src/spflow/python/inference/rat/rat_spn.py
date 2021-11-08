from multipledispatch import dispatch  # type: ignore
import numpy as np
from spflow.python.structure.rat import RatSpn
from spflow.python.inference.nodes import log_likelihood


@dispatch(RatSpn, np.ndarray)  # type: ignore[no-redef]
def log_likelihood(rat_spn: RatSpn, data: np.ndarray):
    return log_likelihood(rat_spn.network_type, rat_spn.output_nodes[0], data)


@dispatch(RatSpn, np.ndarray)  # type: ignore[no-redef]
def likelihood(rat_spn: RatSpn, data: np.ndarray):
    return np.exp(log_likelihood(rat_spn.network_type, rat_spn.output_nodes[0], data))