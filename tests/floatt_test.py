#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


from operator import lt, le, ge, gt, add, truediv, sub, mul
import unittest

from pyMathBitPrecise.floatt import Floatt


#float_32 = Floatt(8, 23, name="float")
float_64 = Floatt(11, 52, name="double")


class FloattTC(unittest.TestCase):

    def test_bit_length(self):
        self.assertEqual(float_64.bit_length(), 64)

    def test_fo_and_from_py(self):
        v0 = float_64.from_py(0.0)
        self.assertEqual(float(v0), 0.0)

        v1 = float_64.from_py(1.0)
        self.assertEqual(float(v1), 1.0)

        v1_25 = float_64.from_py(1.25)
        self.assertEqual(float(v1_25), 1.25)

        v0_0625 = float_64.from_py(0.0625)
        self.assertEqual(float(v0_0625), 0.0625)

    def test_basic_arith_operands_64(self):
        for op in [add, sub, truediv, mul]:
            v0_0625 = float_64.from_py(0.0625)
            v2 = float_64.from_py(2)
            res0 = op(v0_0625, v2)
            self.assertEqual(float(res0), op(0.0625, 2), op)

            res1 = op(v2, v0_0625)
            self.assertEqual(float(res1), op(2, 0.0625), op)

    def test_basic_cmp_operands_64(self):
        for op in [lt, le, ge, gt, ]:
            v0_0625 = float_64.from_py(0.0625)
            v2 = float_64.from_py(2)
            res0 = op(v0_0625, v2)
            self.assertEqual(bool(res0), op(0.0625, 2), op)

            res1 = op(v2, v0_0625)
            self.assertEqual(bool(res1), op(2, 0.0625), op)


if __name__ == '__main__':
    testLoader = unittest.TestLoader()
    # suite = unittest.TestSuite([FloattTC("test_instantiation_and_eq_neq")])
    suite = testLoader.loadTestsFromTestCase(FloattTC)
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
