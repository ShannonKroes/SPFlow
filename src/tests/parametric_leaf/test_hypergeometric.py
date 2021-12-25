from spflow.base.structure.nodes.leaves.parametric import Hypergeometric
from spflow.base.inference.nodes.node import likelihood, log_likelihood
from spflow.base.structure.network_type import SPN
import numpy as np

import unittest


class TestHypergeometric(unittest.TestCase):
    def test_inference(self):

        # ----- configuration 1 -----
        N = 500
        M = 100
        n = 50

        hypergeometric = Hypergeometric([0], N, M, n)

        # create test inputs/outputs
        data = np.array([[5], [10], [15]])
        targets = np.array([[0.0257071], [0.147368], [0.0270206]])

        probs = likelihood(hypergeometric, data, SPN())
        log_probs = log_likelihood(hypergeometric, data, SPN())

        self.assertTrue(np.allclose(probs, np.exp(log_probs)))
        self.assertTrue(np.allclose(probs, targets))

        # ----- configuration 2 -----
        N = 100
        M = 50
        n = 10

        hypergeometric = Hypergeometric([0], N, M, n)

        # create test inputs/outputs
        data = np.array([[1], [5], [10]])
        targets = np.array([[0.00723683], [0.259334], [0.00059342]])

        probs = likelihood(hypergeometric, data, SPN())
        log_probs = log_likelihood(hypergeometric, data, SPN())

        self.assertTrue(np.allclose(probs, np.exp(log_probs)))
        self.assertTrue(np.allclose(probs, targets))

    def test_initialization(self):

        # Valid parameters for Hypergeometric distribution: N in N U {0}, M in {0,...,N}, n in {0,...,N}, p in [0,1] TODO

        # N = 0
        Hypergeometric([0], 0, 0, 0)
        # N < 0
        self.assertRaises(Exception, Hypergeometric, [0], -1, 1, 1)
        # N = inf and N = nan
        self.assertRaises(Exception, Hypergeometric, [0], np.inf, 1, 1)
        self.assertRaises(Exception, Hypergeometric, [0], np.nan, 1, 1)

        # M < 0 and M > N
        self.assertRaises(Exception, Hypergeometric, [0], 1, -1, 1)
        self.assertRaises(Exception, Hypergeometric, [0], 1, 2, 1)
        # M = inf and M = nan
        self.assertRaises(Exception, Hypergeometric, [0], 1, np.inf, 1)
        self.assertRaises(Exception, Hypergeometric, [0], 1, np.nan, 1)

        # n < 0 and n > N
        self.assertRaises(Exception, Hypergeometric, [0], 1, 1, -1)
        self.assertRaises(Exception, Hypergeometric, [0], 1, 1, 2)
        # n = inf and n = nan
        self.assertRaises(Exception, Hypergeometric, [0], 1, 1, np.inf)
        self.assertRaises(Exception, Hypergeometric, [0], 1, 1, np.nan)

        # dummy distribution and data
        hypergeometric = Hypergeometric([0], N=500, M=100, n=50)
        data = np.array([[5], [10], [15]])

        # set parameters to None manually
        hypergeometric.n = None
        self.assertRaises(Exception, likelihood, hypergeometric, data, SPN())
        hypergeometric.M = None
        self.assertRaises(Exception, likelihood, hypergeometric, data, SPN())
        hypergeometric.N = None
        self.assertRaises(Exception, likelihood, hypergeometric, data, SPN())

        # invalid scope lengths
        self.assertRaises(Exception, Hypergeometric, [], 1, 1, 1)
        self.assertRaises(Exception, Hypergeometric, [0, 1], 1, 1, 1)

    def test_support(self):

        # Support for Hypergeometric distribution: integers {max(0,n+M-N),...,min(n,M)}

        # TODO:
        #   likelihood:         0->0.000000001, 1.0->0.999999999
        #   log-likelihood: -inf->fmin

        # case n+M-N > 0
        N = 15
        M = 10
        n = 10

        hypergeometric = Hypergeometric([0], N, M, n)

        # check infinite values
        self.assertRaises(ValueError, log_likelihood, hypergeometric, np.array([[-np.inf]]), SPN())
        self.assertRaises(ValueError, log_likelihood, hypergeometric, np.array([[np.inf]]), SPN())

        # check valid integers inside valid range
        data = np.array([[max(0, n + M - N)], [min(n, M)]])

        probs = likelihood(hypergeometric, data, SPN())
        log_probs = log_likelihood(hypergeometric, data, SPN())

        self.assertTrue(all(probs != 0))
        self.assertTrue(np.allclose(probs, np.exp(log_probs)))

        # check valid integers, but outside of valid range
        self.assertRaises(
            ValueError, log_likelihood, hypergeometric, np.array([[max(0, n + M - N) - 1]]), SPN()
        )
        self.assertRaises(
            ValueError, log_likelihood, hypergeometric, np.array([[min(n, M) + 1]]), SPN()
        )

        # check invalid float values
        self.assertRaises(
            ValueError,
            log_likelihood,
            hypergeometric,
            np.array([[np.nextafter(max(0, n + M - N), 100)]]),
            SPN(),
        )
        self.assertRaises(
            ValueError,
            log_likelihood,
            hypergeometric,
            np.array([[np.nextafter(max(n, M), -1.0)]]),
            SPN(),
        )
        self.assertRaises(ValueError, log_likelihood, hypergeometric, np.array([[5.5]]), SPN())

        # case n+M-N
        N = 25

        hypergeometric = Hypergeometric([0], N, M, n)

        # check valid integers within valid range
        data = np.array([[max(0, n + M - N)], [min(n, M)]])

        probs = likelihood(hypergeometric, data, SPN())
        log_probs = log_likelihood(hypergeometric, data, SPN())

        self.assertTrue(all(probs != 0))
        self.assertTrue(np.allclose(probs, np.exp(log_probs)))

        # check valid integers, but outside of valid range
        self.assertRaises(
            ValueError, log_likelihood, hypergeometric, np.array([[max(0, n + M - N) - 1]]), SPN()
        )
        self.assertRaises(
            ValueError, log_likelihood, hypergeometric, np.array([[min(n, M) + 1]]), SPN()
        )

        # check invalid float values
        self.assertRaises(
            ValueError,
            log_likelihood,
            hypergeometric,
            np.array([[np.nextafter(max(0, n + M - N), 100)]]),
            SPN(),
        )
        self.assertRaises(
            ValueError,
            log_likelihood,
            hypergeometric,
            np.array([[np.nextafter(max(n, M), -1.0)]]),
            SPN(),
        )
        self.assertRaises(ValueError, log_likelihood, hypergeometric, np.array([[5.5]]), SPN())

    def test_marginalization(self):

        hypergeometric = Hypergeometric([0], 15, 10, 10)
        data = np.array([[np.nan]])

        # should not raise and error and should return 1 (0 in log-space)
        probs = likelihood(hypergeometric, data, SPN())
        log_probs = log_likelihood(hypergeometric, data, SPN())

        self.assertTrue(np.allclose(probs, np.exp(log_probs)))
        self.assertTrue(np.allclose(probs, 1.0))


if __name__ == "__main__":
    unittest.main()
