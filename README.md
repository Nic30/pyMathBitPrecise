# pyMathBitPrecise
[![Build Status](https://travis-ci.org/Nic30/pyMathBitPrecise.svg?branch=master)](https://travis-ci.org/Nic30/pyMathBitPrecise)
[![Coverage Status](https://coveralls.io/repos/github/Nic30/pyMathBitPrecise/badge.svg?branch=master)](https://coveralls.io/github/Nic30/pyMathBitPrecise?branch=master)
[![PyPI version](https://badge.fury.io/py/pyMathBitPrecise.svg)](http://badge.fury.io/py/pyMathBitPrecise) 
[![Documentation Status](https://readthedocs.org/projects/pyMathBitPrecise/badge/?version=latest)](http://pyMathBitPrecise.readthedocs.io/en/latest/?badge=latest) 
[![](https://img.shields.io/github/license/Nic30/pyMathBitPrecise.svg)](https://github.com/Nic30/pyMathBitPrecise)
[![Python version](https://img.shields.io/pypi/pyversions/pyMathBitPrecise.svg)](https://img.shields.io/pypi/pyversions/pyMathBitPrecise.svg)

This library contains number types of variable bit size and utils for bit manipulations.
Thre are also types which support tri state values etc. (Python equivalents of VHDL `std_logic_vector`, Verilog `wire`/`reg`.)

This may be usefull for tools which are simulating hardware or software which needs numbers of exact size.


## Example

```Python
from pyMathBitPrecise.bits3t import Bits3t

#3t means that bits can have values 1,0,x
uint512_t = Bits3t(512, signed=False)

a = uint512_t.from_py(1)

# indexing on bits
# [note] == is not overloaded, because it would make the values unhashable
#        because of support of partially valid values which can not be compared
assert a[0]._eq(1)
assert a[0]._dtype.bit_length() == 1
assert a[1]._eq(0)
assert a[8:]._eq(1)
assert a[8:]._dtype.bit_length() == 8

# arithmetic
b = a + 1
assert b._eq(2)
assert b._dtype == uint512_t

# bitwise operations
c = a >> 8
assert c.eq(0)
assert c._dtype == uint512_t

# casting
d = int(a)
assert d == 1 and isinstance(d, int)

uint8_t = Bits3t(8, signed=False)
e = a.cast(uint8_t)
assert e._dtype == uint8_t
```
