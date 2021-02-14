import math
from typing import Union, Optional, Tuple

from pyMathBitPrecise.bit_utils import ValidityError
from pyMathBitPrecise.bits3t import Bits3t
from decimal import DecimalTuple
from pyMathBitPrecise.array3t import Array3t
from operator import lt, le, ge, gt, add, truediv, sub, mul
# from decimal import Decimal, DecimalTuple, localcontext, Context, DefaultContext


class Floatt():
    """
    IEEE 754 like float type with configurable sizes fo exponent and mantisa.
    """

    def __init__(self, exponent_w, mantisa_w, name=None):
        self.name = name
        self.exponent_w = exponent_w
        self.mantisa_w = mantisa_w
        # self._ctx = Context(prec=None, rounding=rounding)

    def _is_float64(self):
        return self.exponent_w == 11 and self.mantisa_w == 52

    def __copy__(self):
        t = self.__class__(self.exponent_w, self.mantisa_w)
        return t

    def all_mask(self):
        """
        :return: mask for bites of this type ( 0b111 for Bits(3) )
        """
        return 1

    def bit_length(self):
        """
        :return: number of bits required for representation
            of value of this type
        """
        return 1 + self.exponent_w + self.mantisa_w

    def __eq__(self, other):
        return (self is other
                or (isinstance(other, Floatt)
                    and self.exponent_w == other.exponent_w
                    and self.mantisa_w == other.mantisa_w
                    and self.name == other.name
                    )
            )

    def __hash__(self):
        return hash((
            self.exponent_w,
            self.mantisa_w,
            self.name,
        ))

    def from_py(self, val: Union[int, str, float],
                vld_mask: Optional[int]=None) -> "FloattVal":
        """
        Construct value from pythonic value
        """

        if isinstance(val, int):
            val = float(val)
            if float(val) != val:
                raise NotImplementedError("Need to implement better conversion method")

        if val is None:
            sign = 0
            exp = 0
            man = 0
            assert vld_mask is None or vld_mask == 0
            vld_mask = 0
        elif isinstance(val, float):
            man, exp = math.frexp(val)
            man = abs(man)
            man = int(man * (2 ** self.mantisa_w))
            sign = int(val < 0)
            if vld_mask is None:
                vld_mask = 1
        elif isinstance(val, tuple):
            sign, man, exp = val
            if vld_mask is None:
                vld_mask = 1
        else:
            raise TypeError(val)

        return FloattVal(self, DecimalTuple(sign, man, exp), vld_mask)

    def __getitem__(self, i):
        ":return: an item from this array"
        return Array3t(self, i)

    def __repr__(self):
        return "<%s, exp:%d, man:%d>" % (
            self.__class__.__name__,
            self.exponent_w,
            self.mantisa_w,
        )


def FloattVal__arith_op(self, other, op):
    t = self._dtype
    if isinstance(other, (float, int)):
        other = t.from_py(other)

    if not self.vld_mask or not other.vld_mask:
        return t.from_py(None)
    elif self._dtype._is_float64():
        return t.from_py(op(float(self), float(other)))
    else:
        raise NotImplementedError()


def FloattVal__cmp_op(self, other, op):
    t = self._dtype
    if isinstance(other, (float, int)):
        other = t.from_py(other)

    if not self.vld_mask or not other.vld_mask:
        return t.from_py(None)
    elif self._dtype._is_float64():
        return self._BOOL.from_py(int(op(float(self), float(other))))
    else:
        raise NotImplementedError()


class FloattVal():
    """
    Class for value of `Bits3t` type

    :ivar ~._dtype: reference on type of this value
    :ivar ~.val: always unsigned representation int value
    :ivar ~.vld_mask: always unsigned value of the mask, if bit in mask is '0'
            the corresponding bit in val is invalid
    """
    _BOOL = Bits3t(1)

    def __init__(self, t: Floatt, val: Tuple[int, int, int], vld_mask: int):
        if not isinstance(t, Floatt):
            raise TypeError(t)
        if len(val) != 3:
            raise TypeError(val)
        for x in val:
            if not isinstance(x, int):
                raise TypeError(val)
        assert val[1] >= 0

        if type(vld_mask) != int:
            raise TypeError(vld_mask)

        self._dtype = t
        self.val = val
        self.vld_mask = vld_mask

    def __copy__(self):
        return self.__class__(self._dtype, self.val, self.vld_mask)

    def to_py(self) -> int:
        return int(self)

    def _is_full_valid(self) -> bool:
        """
        :return: True if all bits in value are valid
        """
        return self.vld_mask == self._dtype.all_mask()

    def __int__(self) -> int:
        "int(self)"
        return int(self.__float__())

    def __bool__(self) -> bool:
        "bool(self)"
        return bool(self.__int__())

    def __float__(self) -> float:
        if not self._is_full_valid():
            raise ValidityError()
        sign, mantisa, exponent = self.val
        mantisa = float(mantisa)
        mantisa *= (2 ** (exponent - self._dtype.mantisa_w))
        if sign:
            return mantisa * -1.0
        else:
            return mantisa

    def __hash__(self):
        return hash((self._dtype, self.val, self.vld_mask))

    def _is(self, other):
        """check if other is object with same values"""
        return isinstance(other, FloattVal)\
            and self._dtype == other._dtype\
            and self.val == other.val\
            and self.vld_mask == other.vld_mask

    def __neg__(self):
        "Operator -x."
        t = self._dtype
        if not self.vld_mask:
            return t.from_py(None)
        elif self._dtype._is_float_32():
            return t.from_py(float(self))
        else:
            raise NotImplementedError()

    def _eq(self, other):
        return self._BOOL.from_py(
            int(self.val == other.val),
            vld_mask=self.vld_mask & other.vld_mask)

    def __ne__(self, other):
        return self._BOOL.from_py(
            int(self.val != other.val),
            vld_mask=self.vld_mask & other.vld_mask)

    def __req__(self, other: int) -> "Bits3val":
        "Operator ==."
        return self._dtype.from_py(other).__eq__(self)

    def __rne__(self, other: int) -> "Bits3val":
        "Operator !=."
        return self._dtype.from_py(other).__ne__(self)

    def __lt__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator <."
        return FloattVal__cmp_op(self, other, lt)

    def __rlt__(self, other: int) -> "Bits3val":
        "Operator <."
        return FloattVal__cmp_op(self._dtype.from_py(other), self, lt)

    def __gt__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator >."
        return FloattVal__cmp_op(self, other, gt)

    def __rgt__(self, other: int) -> "Bits3val":
        "Operator >."
        return FloattVal__cmp_op(self._dtype.from_py(other), self, gt)

    def __ge__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator >=."
        return FloattVal__cmp_op(self, other, ge)

    def __rge__(self, other: int) -> "Bits3val":
        "Operator >=."
        return FloattVal__cmp_op(self._dtype.from_py(other), self, ge)

    def __le__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator <=."
        return FloattVal__cmp_op(self, other, le)

    def __rle__(self, other: int) -> "Bits3val":
        "Operator <=."
        return FloattVal__cmp_op(self._dtype.from_py(other), self, le)

    def __add__(self, other):
        return FloattVal__arith_op(self, other, add)

    def __radd__(self, other):
        return FloattVal__cmp_op(self._dtype.from_py(other), self, add)

    def __sub__(self, other):
        return FloattVal__arith_op(self, other, sub)

    def __rsub__(self, other):
        return FloattVal__cmp_op(self._dtype.from_py(other), self, sub)

    def __mul__(self, other):
        return FloattVal__arith_op(self, other, mul)

    def __rmul__(self, other):
        return FloattVal__cmp_op(self._dtype.from_py(other), self, mul)

    def __truediv__(self, other):
        return FloattVal__arith_op(self, other, truediv)

    def __rtruediv__(self, other):
        return FloattVal__cmp_op(self._dtype.from_py(other), self, truediv)

