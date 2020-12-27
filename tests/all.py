#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.array3t_test import Array3tTC
from tests.bit_utils_test import BitUtilsTC
from tests.bits3tArithmetic_test import Bits3tArithmeticTC
from tests.bits3tBasic_test import Bits3tBasicTC
from tests.bits3tBitwise_test import Bits3tBitwiseTC
from tests.bits3tCmp_test import Bits3tCmpTC
from tests.bits3tSlicing_test import BitsSlicingTC
from tests.enum3t_test import Enum3tTC

suite = unittest.TestSuite()
tcs = [
    BitUtilsTC,
    Bits3tBasicTC,
    Bits3tBitwiseTC,
    Bits3tArithmeticTC,
    Bits3tCmpTC,
    BitsSlicingTC,
    Array3tTC,
    Enum3tTC,
]
for tc in tcs:
    suite.addTest(unittest.makeSuite(tc))

if __name__ == '__main__':
    import sys
    runner = unittest.TextTestRunner(verbosity=2)

    try:
        from concurrencytest import ConcurrentTestSuite, fork_for_tests
        useParallerlTest = True
    except ImportError:
        # concurrencytest is not installed, use regular test runner
        useParallerlTest = False

    if useParallerlTest:
        # Run same tests across 4 processes
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests())
        runner.run(concurrent_suite)
    else:
        sys.exit(not runner.run(suite).wasSuccessful())
