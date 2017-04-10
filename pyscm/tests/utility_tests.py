from __future__ import print_function, division, absolute_import, unicode_literals

import numpy as np
import sys

from numpy import infty as inf
from unittest import TestCase
from sklearn.utils import estimator_checks

from .._scm_utility import find_max
from ..scm import SetCoveringMachineClassifier

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# TODO: Things that must be tested:
# * Verify that the the solver handles equivalent feature values correctly
# * Go crazy, try to break it!

class UtilityTests(TestCase):
    def setUp(self):
        """
        Called before each test

        """
        pass

    def tearDown(self):
        """
        Called after each test

        """
        pass

    def test_1(self):
        """
        Dummy test #1
        """
        X = np.array([[1, 2, 2, 2, 3, 4]], dtype=np.double).reshape(-1, 1).copy()
        y = np.array([0, 1, 0, 1, 1, 1])
        p = 1
        Xas = np.argsort(X, axis=0)
        best_utility, best_feat_idx, \
        best_thresholds, best_kinds = find_max(p, X, y, Xas, np.arange(X.shape[0]), np.ones(1))
        np.testing.assert_almost_equal(actual=best_utility, desired=1.0)
        np.testing.assert_almost_equal(actual=best_feat_idx, desired=[0])
        np.testing.assert_almost_equal(actual=best_thresholds, desired=[1])
        np.testing.assert_almost_equal(actual=best_kinds, desired=[0])

    def test_2(self):
        """
        Test that hyperparameter p works
        """
        X = np.array([[1, 2, 2, 2, 3, 4]], dtype=np.double).reshape(-1, 1).copy()
        y = np.array([0, 1, 0, 1, 1, 1])
        Xas = np.argsort(X, axis=0)
        p = 0.5
        best_utility, best_feat_idx, \
        best_thresholds, best_kinds = find_max(p, X, y, Xas, np.arange(X.shape[0]), np.ones(1))

        np.testing.assert_almost_equal(actual=best_utility, desired=1.0)
        np.testing.assert_almost_equal(actual=best_feat_idx, desired=[0, 0])
        np.testing.assert_almost_equal(actual=best_thresholds, desired=[1, 2])
        np.testing.assert_almost_equal(actual=best_kinds, desired=[0, 0])

    def test_3(self):
        """
        Test that feature_weights works
        """
        X = np.array([[1, 1],
                      [1, 0]], dtype=np.double)
        y = np.array([0, 1])
        Xas = np.argsort(X, axis=0)
        p = 1.0

        # Equal weights, feat 1 should be the best with utility 1
        best_utility, best_feat_idx, \
        best_thresholds, best_kinds = find_max(p, X, y, Xas, np.arange(X.shape[0]), np.ones(X.shape[1]))
        np.testing.assert_almost_equal(actual=best_utility, desired=1)
        np.testing.assert_almost_equal(actual=best_feat_idx, desired=[1])

        # Double weight for feat 1, should be the best with utility 2
        best_utility, best_feat_idx, \
        best_thresholds, best_kinds = find_max(p, X, y, Xas, np.arange(X.shape[0]), np.array([1.0, 2.0]))
        np.testing.assert_almost_equal(actual=best_utility, desired=2)
        np.testing.assert_almost_equal(actual=best_feat_idx, desired=[1])

        # 10 times the weight for feat 1, should be the best with utility 10
        best_utility, best_feat_idx, \
        best_thresholds, best_kinds = find_max(p, X, y, Xas, np.arange(X.shape[0]), np.array([1.0, 10.0]))
        np.testing.assert_almost_equal(actual=best_utility, desired=10)
        np.testing.assert_almost_equal(actual=best_feat_idx, desired=[1])

    def test_4(self):
        """
        Test that example_idx works
        """
        X = np.array([[1, 1],
                      [0, 0],
                      [1, 0]], dtype=np.double)
        y = np.array([0, 1, 1])
        Xas = np.argsort(X, axis=0)
        p = 1.0

        # If example 3 is included, the best feature is feat1
        best_utility, best_feat_idx, \
        best_thresholds, best_kinds = find_max(p, X, y, Xas, np.arange(X.shape[0]), np.ones(X.shape[1]))
        np.testing.assert_almost_equal(actual=best_feat_idx, desired=[1])

        # If example 3 is included, the best feature is feat1
        best_utility, best_feat_idx, \
        best_thresholds, best_kinds = find_max(p, X, y, Xas, np.array([1, 2], dtype=np.int), np.ones(X.shape[1]))
        np.testing.assert_almost_equal(actual=best_feat_idx, desired=[0, 1])

    def automatic_testing(self):
        """
        Random testing
        """
        n_tests = 10 #10000

        # Using rounding generates cases with equal feature values for examples
        for n_decimals in range(3):

            # The more examples, the more likely we are to have equal feature values
            for n_examples in [10, 100, 1000]:

                # Do this a few times for each configuration
                for _ in range(n_tests):
                    p = max(0, np.random.rand() * 100.)
                    x = (np.random.rand(n_examples) * 5.).round(n_decimals).reshape(-1, 1).copy()
                    xas = np.argsort(x, axis=0)
                    y = np.random.randint(0, 2, n_examples)
                    thresholds = np.unique(x)

                    # Use the solver to find the solution
                    solver_best_utility, solver_best_feat_idx, solver_best_thresholds, solver_best_kinds = \
                        find_max(p, x, y, xas, np.arange(n_examples))

                    # Less equal rule utilities
                    le_rule_utilities = []
                    for t in thresholds:
                        rule_classifications = (x <= t).reshape(-1,)
                        N = (~rule_classifications[y == 0]).sum()
                        P_bar = (~rule_classifications[y == 1]).sum()
                        le_rule_utilities.append(N - p * P_bar)

                    # Greater rule utilities
                    g_rule_utilities = []
                    for t in thresholds:
                        rule_classifications = (x > t).reshape(-1,)
                        N = 1.0 * (~rule_classifications[y == 0]).sum()
                        P_bar = 1.0 * (~rule_classifications[y == 1]).sum()
                        g_rule_utilities.append(N - p * P_bar)

                    np.testing.assert_almost_equal(actual=solver_best_utility, desired=max(max(le_rule_utilities),
                                                                                           max(g_rule_utilities)))

    def sklearn_compatibility_test(self):
        """
        Test Sklearn compatibility

        """
        for check in _yield_check_sklearn_compatibility():
            check


def _yield_check_sklearn_compatibility():
    """
    Assert Sklearn compatibility. It is fully compatible except it does not handle multi-class.
    Uses sklearn test suits.
    If fails, will raise an exception
    """
    yield estimator_checks.check_parameters_default_constructible("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier)
    for check in estimator_checks._yield_non_meta_checks("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier):
        yield check

    for check in estimator_checks._yield_classifier_checks("SetCoveringMachineClassifier",
                                                           SetCoveringMachineClassifier):
        yield check

    # Will fail because SCM does not handle multi-class.
    #yield estimator_checks.check_fit2d_predict1d("SetCoveringMachineClassifier",
    #                                                     SetCoveringMachineClassifier)
    yield estimator_checks.check_fit2d_1sample("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier)
    yield estimator_checks.check_fit2d_1feature("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier)
    yield estimator_checks.check_fit1d_1feature("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier)
    yield estimator_checks.check_fit1d_1sample("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier)
    yield estimator_checks.check_get_params_invariance("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier)
    yield estimator_checks.check_dict_unchanged("SetCoveringMachineClassifier",
                                                         SetCoveringMachineClassifier)
