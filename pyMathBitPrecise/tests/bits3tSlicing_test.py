#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest
from pyMathBitPrecise.tests.bits3tBaseTC import uint8_t
from pyMathBitPrecise.bits3t import Bits3t

BIT = Bits3t(1, name="bit")


def vec(val, w):
    t = Bits3t(w)
    return t.from_py(val)


class BitsSlicingTC(unittest.TestCase):

    def test_slice_bits(self):
        v128 = uint8_t.from_py(128)
        v1 = uint8_t.from_py(1)

        with self.assertRaises(IndexError):
            self.assertEqual(v128[8], 1)

        self.assertTrue(v128[7]._eq(BIT.from_py(1)))
        self.assertTrue(v128[1]._eq(BIT.from_py(0)))
        self.assertTrue(v128[0]._eq(BIT.from_py(0)))

        with self.assertRaises(IndexError):
            v128[-1]

        with self.assertRaises(IndexError):
            v128[9:-1]

        with self.assertRaises(IndexError):
            v128[9:]

        with self.assertRaises(IndexError):
            v128[9:0]

        with self.assertRaises(IndexError):
            v128[0:]

        with self.assertRaises(IndexError):
            v128[0:0]

        self.assertTrue(v128[8:]._eq(v128))
        self.assertTrue(v128[8:0]._eq(v128))
        self.assertTrue(v128[:0]._eq(v128))
        self.assertTrue(v128[:1]._eq(vec(64, 7)))
        self.assertTrue(v128[:2]._eq(vec(32, 6)))
        self.assertTrue(v128[:7]._eq(vec(1, 1)))

        self.assertTrue(v1[1:]._eq(vec(1, 1)))
        self.assertTrue(v1[2:]._eq(vec(1, 2)))
        self.assertTrue(v1[8:]._eq(vec(1, 8)))

    def test_BitsIndexOnSingleBit(self):
        v = BIT.from_py(1)
        self.assertTrue(v[0]._eq(BIT.from_py(1)))

    def test_BitsConcatIncompatibleType(self):
        v = BIT.from_py(1)
        with self.assertRaises(TypeError):
            v._concat(2)

    def test_BitsIndexTypes(self):
        t = Bits3t(8)
        v = t.from_py(1)
        with self.assertRaises(TypeError):
            v[object()]
        with self.assertRaises(IndexError):
            v[9:]
        with self.assertRaises(IndexError):
            v[:-1]

        p = 2
        self.assertEqual(v[p]._dtype.bit_length(), 1)

        p2 = slice(p, 0)
        self.assertEqual(v[p2]._dtype.bit_length(), 2)

        v[p] = 1
        self.assertTrue(v._eq(5))

        v[p2] = 2
        self.assertTrue(v._eq(6))

        with self.assertRaises(TypeError):
            v[None] = 2

        v[:] = 0
        self.assertTrue(v._eq(0))

        v[2] = 1
        self.assertTrue(v._eq(4))
        v[3:] = p
        self.assertTrue(v._eq(2))

        v[1] = None
        with self.assertRaises(ValueError):
            int(v)

        with self.assertRaises(TypeError):
            v["asfs"]

    def test_BitsMulInvalidType(self):
        t = Bits3t(8)
        v = t.from_py(1)
        with self.assertRaises(TypeError):
            v * "a"


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(BitsSlicingTC('test_slice_bits_sig'))
    suite.addTest(unittest.makeSuite(BitsSlicingTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
