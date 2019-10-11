#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pyMathBitPrecise.bits3t import Bits3t
import unittest

int8_t = Bits3t(8, signed=True)
uint8_t = Bits3t(8, signed=False)
int512_t = Bits3t(512, signed=True)
uint512_t = Bits3t(512, signed=False)


def valToInt(val):
    if val._is_full_valid():
        return int(val)
    else:
        return None


class Bits3tBaseTC(unittest.TestCase):

    def getMinMaxVal(self, t):
        m = t.all_mask()
        if t.signed:
            intLow = -(m // 2) - 1
            intUp = m // 2
        else:
            intLow = 0
            intUp = m
        return t.from_py(intLow), t.from_py(intUp), intLow, intUp

    def assertEqual(self, first, second, msg=None):
        if first is not None:
            first = int(first)

        if second is not None:
            second = int(second)

        return unittest.TestCase.assertEqual(self, first, second, msg=msg)

