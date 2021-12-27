from spflow.base.structure.nodes.leaves.parametric import LogNormal
from spflow.base.inference.nodes.node import likelihood, log_likelihood
from spflow.base.structure.network_type import SPN
import numpy as np

import unittest
import random


class TestLogNormal(unittest.TestCase):
    def test_likelihood(self):

        # ----- configuration 1 -----
        mean = 0.0
        stdev = 0.25

        log_normal = LogNormal([0], mean, stdev)

        # create test inputs/outputs
        data = np.array([[0.5], [1.0], [1.5]])
        targets = np.array([[0.0683495], [1.59577], [0.285554]])

        probs = likelihood(log_normal, data, SPN())
        log_probs = log_likelihood(log_normal, data, SPN())

        self.assertTrue(np.allclose(probs, np.exp(log_probs)))
        self.assertTrue(np.allclose(probs, targets))

        # ----- configuration 2 -----
        mean = 0.0
        stdev = 0.5

        log_normal = LogNormal([0], mean, stdev)

        # create test inputs/outputs
        data = np.array([[0.5], [1.0], [1.5]])
        targets = np.array([[0.610455], [0.797885], [0.38287]])

        probs = likelihood(log_normal, data, SPN())
        log_probs = log_likelihood(log_normal, data, SPN())

        self.assertTrue(np.allclose(probs, np.exp(log_probs)))
        self.assertTrue(np.allclose(probs, targets))

        # ----- configuration 3 -----
        mean = 0.0
        stdev = 1.0

        log_normal = LogNormal([0], mean, stdev)

        # create test inputs/outputs
        data = np.array([[0.5], [1.0], [1.5]])
        targets = np.array([[0.627496], [0.398942], [0.244974]])

        probs = likelihood(log_normal, data, SPN())
        log_probs = log_likelihood(log_normal, data, SPN())

        self.assertTrue(np.allclose(probs, np.exp(log_probs)))
        self.assertTrue(np.allclose(probs, targets))

    def test_initialization(self):

        # Valid parameters for Log-Normal distribution: mean in (-inf,inf), stdev in (0,inf)

        # mean = +-inf and mean = nan
        self.assertRaises(Exception, LogNormal, [0], np.inf, 1.0)
        self.assertRaises(Exception, LogNormal, [0], -np.inf, 1.0)
        self.assertRaises(Exception, LogNormal, [0], np.nan, 1.0)

        mean = random.random()

        # stdev <= 0
        self.assertRaises(Exception, LogNormal, [0], mean, 0.0)
        self.assertRaises(Exception, LogNormal, [0], mean, np.nextafter(0.0, -1.0))
        # stdev = +-inf and stdev = nan
        self.assertRaises(Exception, LogNormal, [0], mean, np.inf)
        self.assertRaises(Exception, LogNormal, [0], mean, -np.inf)
        self.assertRaises(Exception, LogNormal, [0], mean, np.nan)

        # dummy distribution and data
        log_normal = LogNormal([0], 0.0, 1.0)
        data = np.array([[0.5], [1.0], [1.5]])

        # set parameters to None manually
        log_normal.stdev = None
        self.assertRaises(Exception, likelihood, log_normal, data, SPN())
        log_normal.mean = None
        self.assertRaises(Exception, likelihood, log_normal, data, SPN())

        # invalid scope lengths
        self.assertRaises(Exception, LogNormal, [], 0.0, 1.0)
        self.assertRaises(Exception, LogNormal, [0, 1], 0.0, 1.0)

    def test_support(self):

        # Support for Log-Normal distribution: floats (0,inf)

        # TODO:
        #   likelihood:     None
        #   log-likelihood: None

        log_normal = LogNormal([0], 0.0, 1.0)

        # check infinite values
        self.assertRaises(ValueError, log_likelihood, log_normal, np.array([[-np.inf]]), SPN())
        self.assertRaises(ValueError, log_likelihood, log_normal, np.array([[np.inf]]), SPN())

        # invalid float values
        self.assertRaises(ValueError, log_likelihood, log_normal, np.array([[0]]), SPN())

        # valid float values
        log_likelihood(log_normal, np.array([[np.nextafter(0.0, 1.0)]]), SPN())
        log_likelihood(log_normal, np.array([[4.3]]), SPN())

    def test_marginalization(self):

        log_normal = LogNormal([0], 0.0, 1.0)
        data = np.array([[np.nan]])

        # should not raise and error and should return 1 (0 in log-space)
        probs = likelihood(log_normal, data, SPN())
        log_probs = log_likelihood(log_normal, data, SPN())

        self.assertTrue(np.allclose(probs, np.exp(log_probs)))
        self.assertTrue(np.allclose(probs, 1.0))


if __name__ == "__main__":
    unittest.main()
