#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest
from pyMathBitPrecise.tests.bits3tBaseTC import Bits3tBaseTC, int8_t, \
    int512_t, uint512_t, uint8_t
from pyMathBitPrecise.bits3t import Bits3t


class Bits3tCmpTC(Bits3tBaseTC):

    def test_8b_eq(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        low, up, _, _ = self.getMinMaxVal(t)
        if t.signed:
            self.assertTrue(t.from_py(-1)._eq(-1))
        self.assertTrue(t.from_py(0)._eq(0))
        self.assertTrue(up == up)
        self.assertTrue(low == low)

        if t.signed:
            self.assertFalse(t.from_py(0)._eq(-1))
            self.assertFalse(t.from_py(-1)._eq(0))

        self.assertFalse(t.from_py(0) == 1)
        self.assertFalse(t.from_py(1) == 0)

        self.assertFalse(up == low)
        self.assertFalse(low == up)

        if t.signed:
            with self.assertRaises(TypeError):
                t.from_py(0)._eq(ut.from_py(0))

    def test_8b_ne(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        low, up, _, _ = self.getMinMaxVal(t)

        if t.signed:
            self.assertFalse(t.from_py(-1) != -1)

        self.assertFalse(t.from_py(1) != 1)
        self.assertFalse(t.from_py(0) != 0)
        self.assertFalse(up != up)
        self.assertFalse(low != low)

        if t.signed:
            self.assertTrue(t.from_py(0) != -1)
            self.assertTrue(t.from_py(-1) != 0)

        self.assertTrue(up != low)
        self.assertTrue(low != up)

        if t.signed:
            with self.assertRaises(TypeError):
                t.from_py(0) != ut.from_py(0)

    def test_8b_lt(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        low, up, _, _ = self.getMinMaxVal(t)

        if t.signed:
            self.assertFalse(t.from_py(-1) < -1)

        self.assertFalse(t.from_py(0) < 0)
        self.assertFalse(t.from_py(1) < 1)
        self.assertFalse(up < up)
        self.assertFalse(low < low)

        if t.signed:
            self.assertFalse(t.from_py(0) < -1)
            self.assertTrue(t.from_py(-1) < 0)
        self.assertFalse(up < low)
        self.assertTrue(low < up)

        if t.signed:
            with self.assertRaises(TypeError):
                t.from_py(0) < ut.from_py(0)

    def test_8b_gt(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        low, up, _, _ = self.getMinMaxVal(t)

        if t.signed:
            self.assertFalse(t.from_py(-1) > -1)

        self.assertFalse(t.from_py(0) > 0)
        self.assertFalse(t.from_py(1) > 1)
        self.assertFalse(up > up)
        self.assertFalse(low > low)

        if t.signed:
            self.assertTrue(t.from_py(0) > -1)
            self.assertFalse(t.from_py(-1) > 0)
        self.assertTrue(up > low)
        self.assertFalse(low > up)

        if t.signed:
            with self.assertRaises(TypeError):
                t.from_py(0) > ut.from_py(0)

    def test_8b_ge(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        low, up, _, _ = self.getMinMaxVal(t)

        if t.signed:
            self.assertTrue(t.from_py(-1) >= -1)
        self.assertTrue(t.from_py(0) >= 0)
        self.assertTrue(t.from_py(1) >= 1)
        self.assertTrue(up >= up)
        self.assertTrue(low >= low)

        if t.signed:
            self.assertTrue(t.from_py(0) >= -1)
            self.assertFalse(t.from_py(-1) >= 0)
        self.assertTrue(up >= low)
        self.assertFalse(low >= up)

        if t.signed:
            with self.assertRaises(TypeError):
                t.from_py(0) >= ut.from_py(0)

    def test_8b_le(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        low, up, _, _ = self.getMinMaxVal(t)

        if t.signed:
            self.assertTrue(t.from_py(-1) <= -1)
        self.assertTrue(t.from_py(0) <= 0)
        self.assertTrue(t.from_py(1) <= 1)
        self.assertTrue(up <= up)
        self.assertTrue(low <= low)

        if t.signed:
            self.assertFalse(t.from_py(0) <= -1)
            self.assertTrue(t.from_py(-1) <= 0)
        self.assertFalse(up <= low)
        self.assertTrue(low <= up)

        if t.signed:
            with self.assertRaises(TypeError):
                t.from_py(0) <= ut.from_py(0)

    def test_8b_ternary(self, t=int8_t):
        self.assertFalse(t.from_py(0)._ternary(True, False))
        self.assertTrue(t.from_py(0)._ternary(False, True))
        self.assertFalse(t.from_py(1)._ternary(False, True))
        self.assertTrue(t.from_py(1)._ternary(True, False))

    def test_512b_eq(self):
        self.test_8b_eq(int512_t)

    def test_512b_ne(self):
        self.test_8b_ne(int512_t)

    def test_512b_lt(self):
        self.test_8b_lt(int512_t)

    def test_512b_gt(self):
        self.test_8b_gt(int512_t)

    def test_512b_le(self):
        self.test_8b_le(int512_t)

    def test_512b_ge(self):
        self.test_8b_ge(int512_t)

    def test_u512b_eq(self):
        self.test_8b_eq(uint512_t)

    def test_u512b_ne(self):
        self.test_8b_ne(uint512_t)

    def test_u512b_lt(self):
        self.test_8b_lt(uint512_t)

    def test_u512b_gt(self):
        self.test_8b_gt(uint512_t)

    def test_u512b_le(self):
        self.test_8b_le(uint512_t)

    def test_u512b_ge(self):
        self.test_8b_ge(uint512_t)

    def test_u8b_eq(self):
        self.test_8b_eq(uint8_t)

    def test_u8b_ne(self):
        self.test_8b_ne(uint8_t)

    def test_u8b_lt(self):
        self.test_8b_lt(uint8_t)

    def test_u8b_gt(self):
        self.test_8b_gt(uint8_t)

    def test_u8b_le(self):
        self.test_8b_le(uint8_t)

    def test_u8b_ge(self):
        self.test_8b_ge(uint8_t)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(Bits3tArithmeticTC('test_512b_rshift'))
    suite.addTest(unittest.makeSuite(Bits3tCmpTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
