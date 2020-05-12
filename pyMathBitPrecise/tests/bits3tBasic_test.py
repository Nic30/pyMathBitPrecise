#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pyMathBitPrecise.tests.bits3tBaseTC import Bits3tBaseTC, int8_t, int512_t, \
    uint512_t, uint8_t
import unittest
from pyMathBitPrecise.bits3t import Bits3t
from pyMathBitPrecise.bit_utils import mask


class Bits3tBasicTC(Bits3tBaseTC):

    def test_8b_proper_val(self, t=int8_t):
        if t.signed:
            self.assertEqual(t.from_py(-1), -1)
        else:
            with self.assertRaises(ValueError):
                t.from_py(-1)

        low, up, intLow, intUp = self.getMinMaxVal(t)

        self.assertEqual(low, intLow)
        self.assertEqual(up, intUp)

        # value is not correct value
        with self.assertRaises(TypeError):
            t.from_py({})

        # value is out of range of type
        with self.assertRaises(ValueError):
            t.from_py(intLow - 1)

        with self.assertRaises(ValueError):
            t.from_py(intUp + 1)

    def test_8b_cast(self, t=int8_t):
        w = t.bit_length()
        if t.signed:
            ut = Bits3t(w)
        else:
            ut = t
            t = Bits3t(w, True)
        self.assertEqual(int(t.from_py(-1).cast(ut)), mask(w))
        self.assertEqual(int(t.from_py(-1).cast_sign(False)), mask(w))
        self.assertEqual(int(t.from_py(-1).cast_sign(None)), mask(w))
        self.assertEqual(int(t.from_py(1).cast(ut)), 1)
        self.assertEqual(int(t.from_py(0).cast(ut)), 0)
        self.assertEqual(int(ut.from_py(1).cast(t)), 1)
        self.assertEqual(int(ut.from_py(mask(w)).cast(t)), -1)
        self.assertEqual(int(ut.from_py(mask(w)).cast_sign(True)), -1)

    def test_512b_proper_val(self):
        self.test_8b_proper_val(int512_t)

    def test_u512b_proper_val(self):
        self.test_8b_proper_val(uint512_t)

    def test_u8b_proper_val(self):
        self.test_8b_proper_val(uint8_t)
        t = uint8_t
        with self.assertRaises(ValueError):
            t.from_py("0b0000000e")

        v = t.from_py("0b0000000x")
        self.assertEqual(v.val, 0)
        self.assertEqual(v.vld_mask, mask(7) << 1)

        v = t.from_py("0bxx000000")
        self.assertEqual(v.val, 0)
        self.assertEqual(v.vld_mask, mask(6))

    def test_512b_cast(self):
        self.test_8b_cast(int512_t)

    def test_u512b_cast(self):
        self.test_8b_cast(uint512_t)

    def test_u8b_cast(self):
        self.test_8b_cast(uint8_t)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(Bits3tBasicTC('test_8b_proper_val'))
    suite.addTest(unittest.makeSuite(Bits3tBasicTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
