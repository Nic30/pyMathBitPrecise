#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from pyMathBitPrecise.bit_utils import to_signed, mask
from pyMathBitPrecise.bits3t import Bits3t
from pyMathBitPrecise.tests.bits3tBaseTC import Bits3tBaseTC, int8_t, int512_t, \
    uint512_t, uint8_t


class Bits3tBitwiseTC(Bits3tBaseTC):

    def test_8b_and(self, t=int8_t):
        low, up, intLow, intUp = self.getMinMaxVal(t)
        ut = Bits3t(t.bit_length())
        m = t.all_mask()

        ae = self.assertEqual
        if t.signed:
            v = t.from_py(-1)
        else:
            v = t.from_py(m)

        if t.signed:
            ae(v & ut.from_py(m), -1)
        ae(v & ut.from_py(0), 0)
        ae(v & ut.from_py(1), 1)
        ae(low & up, 0)
        if t.signed:
            ae(low & -1, intLow)
        else:
            ae(low & m, intLow)
        ae(up & ut.from_py(m), intUp)

    def test_8b_or(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        m = t.all_mask()
        low, up, intLow, intUp = self.getMinMaxVal(t)

        ae = self.assertEqual
        if t.signed:
            v = t.from_py(-1)
        else:
            v = t.from_py(m)

        if t.signed:
            ae(v | ut.from_py(m), -1)
            ae(v | ut.from_py(0), -1)
            ae(low | ut.from_py(m), -1)
            ae(up | ut.from_py(m), -1)

        ae(low | ut.from_py(0), intLow)
        ae(up | ut.from_py(0), intUp)

    def test_8b_xor(self, t=int8_t):
        ut = Bits3t(t.bit_length())
        m = t.all_mask()

        if t.signed:
            v = t.from_py(-1)
        else:
            v = t.from_py(m)

        ae = self.assertEqual
        ae(v ^ ut.from_py(m), 0)
        if t.signed:
            ae(v ^ ut.from_py(0), -1)
            ae(v ^ ut.from_py(1), -2)
        else:
            ae(v ^ ut.from_py(0), m)
            ae(v ^ ut.from_py(1), m ^ 1)

    def test_8b_invert(self, t=int8_t):
        low, up, intLow, intUp = self.getMinMaxVal(t)

        if t.signed:
            self.assertEqual(~t.from_py(-1), 0)
        else:
            self.assertEqual(~t.from_py(mask(t.bit_length())), 0)
        self.assertEqual(~low, intUp)
        self.assertEqual(~up, intLow)

    def test_8b_lshift(self, t=int8_t):
        w = t.bit_length()
        for i in range(w + 1):
            if i == w:
                v = 0
            else:
                v = (1 << i) & t.all_mask()
                if t.signed:
                    v = to_signed(v, w)
            self.assertEqual(t.from_py(1) << i, v)

    def test_8b_rshift(self, t=int8_t):
        w = t.bit_length()
        m = t.all_mask()
        for i in range(w):
            if t.signed:
                res = t.from_py(-1) >> i
                if i == 0:
                    self.assertEqual(res, -1, i)
                else:
                    self.assertEqual(res, m >> i, i)
            else:
                self.assertEqual(t.from_py(m) >> i, m >> i)

    def test_8b_16b_concat(self):
        t0 = uint8_t
        t1 = Bits3t(16)
        self.assertEqual(int(t0.from_py(0xff)._concat(
            t1.from_py(1))), (0xff << 16) | 1)

    def test_512b_and(self):
        self.test_8b_and(int512_t)

    def test_512b_or(self):
        self.test_8b_or(int512_t)

    def test_512b_xor(self):
        self.test_8b_xor(int512_t)

    def test_512b_invert(self):
        self.test_8b_invert(int512_t)

    def test_512b_lshift(self):
        self.test_8b_lshift(int512_t)

    def test_512b_rshift(self):
        self.test_8b_rshift(int512_t)

    def test_u512b_and(self):
        self.test_8b_and(uint512_t)

    def test_u512b_or(self):
        self.test_8b_or(uint512_t)

    def test_u512b_xor(self):
        self.test_8b_xor(uint512_t)

    def test_u512b_invert(self):
        self.test_8b_invert(uint512_t)

    def test_u512b_lshift(self):
        self.test_8b_lshift(uint512_t)

    def test_u512b_rshift(self):
        self.test_8b_rshift(uint512_t)

    def test_u8b_and(self):
        self.test_8b_and(uint8_t)

    def test_u8b_or(self):
        self.test_8b_or(uint8_t)

    def test_u8b_xor(self):
        self.test_8b_xor(uint8_t)

    def test_u8b_invert(self):
        self.test_8b_invert(uint8_t)

    def test_u8b_lshift(self):
        self.test_8b_lshift(uint8_t)

    def test_u8b_rshift(self):
        self.test_8b_rshift(uint8_t)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(Bits3tArithmeticTC('test_512b_rshift'))
    suite.addTest(unittest.makeSuite(Bits3tBitwiseTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
