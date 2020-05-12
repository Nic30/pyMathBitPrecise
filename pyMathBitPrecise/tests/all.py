#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from pyMathBitPrecise.tests.array3t_test import Array3tTC
from pyMathBitPrecise.tests.bit_utils_test import BitUtilsTC
from pyMathBitPrecise.tests.bits3tArithmetic_test import Bits3tArithmeticTC
from pyMathBitPrecise.tests.bits3tBasic_test import Bits3tBasicTC
from pyMathBitPrecise.tests.bits3tBitwise_test import Bits3tBitwiseTC
from pyMathBitPrecise.tests.bits3tCmp_test import Bits3tCmpTC
from pyMathBitPrecise.tests.bits3tSlicing_test import BitsSlicingTC
from pyMathBitPrecise.tests.enum3t_test import Enum3tTC


if __name__ == "__main__":
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

    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
