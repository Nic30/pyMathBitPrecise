#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest
from tests.bits3tBaseTC import Bits3tBaseTC, int8_t, Bits3valToInt, \
    int512_t, uint512_t, uint8_t
from pyMathBitPrecise.bits3t import Bits3t
from pyMathBitPrecise.bit_utils import mask


class Bits3tArithmeticTC(Bits3tBaseTC):

    def test_4b_sign_cast(self):
        t = Bits3t(4)
        v = t.from_py(0xf)
        self.assertEqual(int(v), 0xf)
        self.assertEqual(int(v._cast_sign(True)), -1)
        self.assertEqual(int(v._cast_sign(True)._cast_sign(False)), 0xf)

        v = t.from_py(0xe)
        self.assertEqual(int(v), 0xe)
        self.assertEqual(int(v._cast_sign(True)), -2)
        self.assertEqual(int(v._cast_sign(True)._cast_sign(False)), 0xe)

    def test_4b_sext(self):
        t = Bits3t(4)
        v = t.from_py(0xf)
        self.assertEqual(int(v._sext(4)), 0x0f)
        self.assertEqual(int(v._sext(5)), 0x1f)
        self.assertEqual(int(v._sext(6)), 0x3f)
        with self.assertRaises(AssertionError):
            v._sext(3)

        v = t.from_py(0b0111)
        self.assertEqual(int(v._sext(4)), 0b0111)
        self.assertEqual(int(v._sext(5)), 0b0111)
        self.assertEqual(int(v._sext(6)), 0b0111)

    def test_4b_zext(self):
        t = Bits3t(4)
        v = t.from_py(0xf)
        self.assertEqual(int(v._zext(4)), 0xf)
        self.assertEqual(int(v._zext(5)), 0xf)
        self.assertEqual(int(v._zext(6)), 0xf)
        with self.assertRaises(AssertionError):
            v._zext(3)

        v = t.from_py(0b0111)
        self.assertEqual(int(v._zext(4)), 0b0111)

    def test_4b_trunc(self):
        t = Bits3t(4)
        v = t.from_py(0xf)
        self.assertEqual(int(v._trunc(3)), 0b111)
        self.assertEqual(int(v._trunc(2)), 0b11)

        t = Bits3t(4, signed=True)
        low, up, _, _ = self.getMinMaxVal(t)

        self.assertEqual(int(low._trunc(3)), 0)
        self.assertEqual(int(up._trunc(3)), -1)

    def test_8b_add(self, t=int8_t):
        low, up, intLow, intUp = self.getMinMaxVal(t)

        ae = self.assertEqual
        if t.signed:
            ae(t.from_py(-1) + -1, -2)
            ae(t.from_py(-1) + 0, -1)
            ae(t.from_py(-1) + 1, 0)
        ae(t.from_py(1) + 0, 1)
        ae(low + 1, intLow + 1)
        if t.signed:
            ae(low + -1, intUp)
        ae(up + 1, intLow)
        if t.signed:
            ae(up + -1, intUp - 1)

        if t.signed:
            ae(t.from_py(-10) + 20, 10)
            ae(t.from_py(10) + -20, -10)
            ae(t.from_py(intUp) + 20, intLow + (20 - 1))
        else:
            ae(t.from_py(intUp) + 20, 20 - 1)

    def test_8b_sub(self, t=int8_t):
        low, up, intLow, intUp = self.getMinMaxVal(t)

        ae = self.assertEqual
        if t.signed:
            ae(t.from_py(-1) - -1, 0)
            ae(t.from_py(-1) - 0, -1)
            ae(t.from_py(-1) - 1, -2)
            ae(low - -1, intLow + 1)
            ae(up - -1, intLow)

            ae(t.from_py(-10) - 20, -30)
            ae(t.from_py(10) - -20, 30)
        else:
            ae(t.from_py(intUp) - intUp, 0)
            ae(t.from_py(1) - 0, 1)
            ae(t.from_py(1) - 1, 0)

            ae(t.from_py(10) - 20, intUp - 10 + 1)

        ae(low - 1, intUp)
        ae(t.from_py(1) - 0, 1)
        ae(up - 1, intUp - 1)

    def test_8b_mul(self, t=int8_t):
        w = t.bit_length()
        low, up, _, _ = self.getMinMaxVal(t)
        ut = Bits3t(w)

        ae = self.assertEqual
        if t.signed:
            ae(int(t.from_py(-1) * t.from_py(-1)), 1)
        ae(int(t.from_py(1) * t.from_py(1)), 1)
        if t.signed:
            ae(int(t.from_py(0) * t.from_py(-1)), 0)
        ae(int(ut.from_py(0) * ut.from_py(1)), 0)
        ae(int(ut.from_py(mask(w)) * ut.from_py(2)), (mask(w) << 1) & mask(w))
        if t.signed:
            ae(int(t.from_py(-1) * ut.from_py(2)), -2)
        ae(low * t.from_py(2), 0)
        if t.signed:
            ae(up * t.from_py(2), -2)

        m = up * t.from_py(None)
        ae(Bits3valToInt(m), None)

    def test_8b_neg(self, t=int8_t):
        w = t.bit_length()
        low, up, _, _ = self.getMinMaxVal(t)

        ae = self.assertEqual
        if t.signed:
            m1 = t.from_py(-1)
            ae(int(m1), -1)
            ae(int(-m1), 1)

            ae(int(-t.from_py(2)), -2)
            ae(int(-t.from_py(-2)), 2)

            ae(int(-low), int(low))
            ae(int(-up), -mask(w - 1))
        else:
            ae(int(-t.from_py(0)), 0)
            ae(int(-t.from_py(up)), 1)
            ae(int(-t.from_py(1)), up)

    def test_8b_div(self, t=int8_t):
        self.assertEqual((t.from_py(0) // t.from_py(1)), 0)
        self.assertEqual((t.from_py(1) // t.from_py(1)), 1)
        self.assertEqual((t.from_py(8) // t.from_py(2)), 4)
        self.assertEqual((t.from_py(8) // 2), 4)
        self.assertEqual((t.from_py(8) // t.from_py(None)).vld_mask, 0)
        self.assertEqual((t.from_py(None) // t.from_py(2)).vld_mask, 0)
        if t.signed:
            self.assertEqual((t.from_py(-1) // t.from_py(1)), -1)
            self.assertEqual((t.from_py(1) // t.from_py(-1)), -1)
            self.assertEqual((t.from_py(-1) // t.from_py(-1)), 1)

    def test_u8b_div(self, t=uint8_t):
        self.test_8b_div(t)

    def test_512b_add(self):
        self.test_8b_add(int512_t)

    def test_512b_sub(self):
        self.test_8b_sub(int512_t)

    def test_512b_mul(self):
        self.test_8b_mul(int512_t)

    def test_u512b_add(self):
        self.test_8b_add(uint512_t)

    def test_u512b_sub(self):
        self.test_8b_sub(uint512_t)

    def test_u512b_mul(self):
        self.test_8b_mul(uint512_t)

    def test_u8b_add(self):
        self.test_8b_add(uint8_t)

    def test_u8b_sub(self):
        self.test_8b_sub(uint8_t)

    def test_u8b_mul(self):
        self.test_8b_mul(uint8_t)

    def test_u8b_neg(self, t=uint8_t):
        self.test_8b_neg(t)

    def test_512b_neg(self, t=int512_t):
        self.test_8b_neg(t)

    def test_u512b_neg(self, t=uint512_t):
        self.test_8b_neg(t)


if __name__ == '__main__':
    testLoader = unittest.TestLoader()
    # suite = unittest.TestSuite([Bits3tArithmeticTC("test_512b_rshift")])
    suite = testLoader.loadTestsFromTestCase(Bits3tArithmeticTC)
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
