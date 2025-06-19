#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pyMathBitPrecise.bits3t import Bits3t
import unittest

int8_t = Bits3t(8, signed=True)
uint8_t = Bits3t(8, signed=False)
int512_t = Bits3t(512, signed=True)
uint512_t = Bits3t(512, signed=False)


def Bits3valToInt(val):
    if val._is_full_valid():
        return int(val)
    else:
        return None


class Bits3tBaseTC(unittest.TestCase):

    def getMinMaxVal(self, t):
        intMin, intMax = t.get_domain_range()
        return t.from_py(intMin), t.from_py(intMax), intMin, intMax

    def assertEqual(self, first, second, msg=None):
        if first is not None:
            first = int(first)

        if second is not None:
            second = int(second)

        return unittest.TestCase.assertEqual(self, first, second, msg=msg)

