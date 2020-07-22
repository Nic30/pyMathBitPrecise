#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from copy import copy
from enum import Enum
from math import log2, ceil
from operator import le, ge, gt, lt, ne, eq, and_, or_, xor, sub, add
from typing import Union, Optional

from pyMathBitPrecise.array3t import Array3t
from pyMathBitPrecise.bit_utils import mask, get_bit, get_bit_range, \
    to_signed, set_bit_range, bit_set_to, bit_field, to_unsigned, INT_BASES, \
    ValidityError, normalize_slice
from pyMathBitPrecise.bits3t_vld_masks import vld_mask_for_xor, vld_mask_for_and, \
    vld_mask_for_or


class Bits3t():
    """
    Meta type for integer of specified size where
    each bit can be '1', '0' or 'X' for undefined value.

    :ivar ~.bit_length: number representation of value of this type
    :ivar ~.signed: flag which tells if this type is signed or not
    :ivar ~._all_mask: cached value of mask for all bits
    :ivar ~.name: name for anotation
    :ivar ~.force_vector: use always hdl vector type
            (for example std_logic_vector(0 downto 0)
             instead of std_logic in VHDL,
             wire[1] instead of wire)
    :ivar ~.strict_sign: same thing as strict_width just for signed/unsigned
    :ivar ~.strict_width: if True the arithmetic, bitwise
        and comparision operators can be performed only on value
        of this exact same width
    :note: operation is not strict if at least one operand
        does not have strict flag set,
        the result width/sign is taken from other operand
        (or first if bouth are not strict)
    """

    def __init__(self, bit_length: int, signed=False, name: Optional[str]=None,
                 force_vector=False,
                 strict_sign=True, strict_width=True):
        self._bit_length = bit_length
        self.signed = signed
        self._all_mask = mask(bit_length)
        self.name = name
        self.force_vector = force_vector
        self.strict_sign = strict_sign
        self.strict_width = strict_width

    def __copy__(self):
        t = self.__class__(self._bit_length, signed=self.signed,
                           name=self.name,
                           force_vector=self.force_vector,
                           strict_sign=self.strict_sign,
                           strict_width=self.strict_width)
        return t

    def all_mask(self):
        """
        :return: mask for bites of this type ( 0b111 for Bits(3) )
        """
        return self._all_mask

    def bit_length(self):
        """
        :return: number of bits required for representation
            of value of this type
        """
        return self._bit_length

    def __eq__(self, other):
        return (self is other
                or (isinstance(other, Bits3t)
                    and self._bit_length == other._bit_length
                    and self.name == other.name
                    and (self.force_vector == other.force_vector
                         or self._bit_length > 1)
                    and self.strict_sign == other.strict_sign
                    and self.strict_width == other.strict_width
                    and self.signed == other.signed
                    )
                )

    def _normalize_val_and_mask(self, val, vld_mask):
        if val is None:
            vld = 0
            val = 0
            assert vld_mask is None or vld_mask == 0
        else:
            all_mask = self.all_mask()
            w = self._bit_length
            if isinstance(val, int):
                pass
            elif isinstance(val, bytes):
                val = int.from_bytes(
                    val, byteorder="little", signed=bool(self.signed))
            elif isinstance(val, str):
                if not (val.startswith("0") and len(val) > 2):
                    raise ValueError(val)

                base = INT_BASES[val[1]]
                try:
                    _val = int(val[2:], base)
                except ValueError:
                    _val = None

                if _val is None:
                    assert vld_mask is None
                    val = val.lower()
                    if base == 10 and "x" in val:
                        raise NotImplementedError()
                    v = 0
                    m = 0
                    bits_per_char = ceil(log2(base))
                    char_mask = mask(bits_per_char)
                    for digit in val[2:]:
                        v <<= bits_per_char
                        m <<= bits_per_char
                        if digit == "x":
                            pass
                        else:
                            m |= char_mask
                            v |= int(digit, base)
                    val = v
                    vld_mask = m
                else:
                    val = _val
            else:
                try:
                    val = int(val)
                except TypeError as e:
                    if isinstance(val, Enum):
                        val = int(val.value)
                    else:
                        raise e

            if vld_mask is None:
                vld = all_mask
            else:
                if vld_mask > all_mask or vld_mask < 0:
                    raise ValueError("Mask in incorrect format", vld_mask)
                vld = vld_mask

            if val < 0:
                if not self.signed:
                    raise ValueError("Negative value for unsigned int")
                _val = to_signed(val & all_mask, w)
                if _val != val:
                    raise ValueError("Too large value", val, _val)
                val = _val
            else:
                if self.signed:
                    msb = 1 << (w - 1)
                    if msb & val:
                        if val > 0:
                            raise ValueError(
                                "Value too large to fit in this type", val)

                if val & all_mask != val:
                    raise ValueError(
                        "Not enought bits to represent value",
                        val, w, val & all_mask)
                val = val & vld
        return val, vld

    def _from_py(self, val, vld_mask):
        """
        from_py without normalization
        """
        return Bits3val(self, val, vld_mask)

    def from_py(self, val: Union[int, bytes, str, Enum],
                vld_mask: Optional[int]=None) -> "Bits3val":
        """
        Construct value from pythonic value
        :note: str value has to start with base specifier (0b, 0h)
            and is much slower than the value specified
            by 'val' and 'vld_mask'. Does support x.
        """
        val, vld_mask = self._normalize_val_and_mask(val, vld_mask)
        return Bits3val(self, val, vld_mask)

    def __getitem__(self, i):
        ":return: an item from this array"
        return Array3t(self, i)

    def __hash__(self):
        return hash((
            self._bit_length,
            self.signed,
            self._all_mask,
            self.name,
            self.force_vector,
            self.strict_sign,
            self.strict_width
        ))

    def __repr__(self):
        """
        :param indent: number of indentation
        :param withAddr: if is not None is used as a additional
            information about on which address this type is stored
            (used only by HStruct)
        :param expandStructs: expand HStructTypes (used by HStruct and HArray)
        """
        constr = []
        if self.name is not None:
            constr.append('"%s"' % self.name)
        c = self.bit_length()
        constr.append("%dbits" % c)
        if self.force_vector:
            constr.append("force_vector")
        if self.signed:
            constr.append("signed")
        elif self.signed is False:
            constr.append("unsigned")
        if not self.strict_sign:
            constr.append("strict_sign=False")
        if not self.strict_width:
            constr.append("strict_width=False")

        return "<%s, %s>" % (self.__class__.__name__,
                             ", ".join(constr))


class Bits3val():
    """
    Class for value of `Bits3t` type

    :ivar ~._dtype: reference on type of this value
    :ivar ~.val: always unsigned representation int value
    :ivar ~.vld_mask: always unsigned value of the mask, if bit in mask is '0'
            the corresponding bit in val is invalid
    """
    _BOOL = Bits3t(1)

    def __init__(self, t: Bits3t, val: int, vld_mask: int):
        if not isinstance(t, Bits3t):
            raise TypeError(t)
        if type(val) != int:
            raise TypeError(val)
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
        if not self._is_full_valid():
            raise ValidityError()

        return self.val

    def __bool__(self) -> bool:
        "bool(self)"
        return bool(self.__int__())

    def _auto_cast(self, dtype):
        """
        Cast value to a compatible type
        """
        return dtype.from_py(self.val, self.vld_mask)

    def cast_sign(self, signed) -> "Bits3val":
        """
        Cast signed-unsigned value
        """
        t = self._dtype
        if t.signed == signed:
            return self
        selfSign = t.signed
        v = self.__copy__()
        w = t.bit_length()
        m = t._all_mask
        _v = v.val

        if selfSign and not signed:
            if _v < 0:
                v.val = m + _v + 1
        elif not selfSign and signed:
            msbMask = 1 << (w - 1)
            if _v >= msbMask:
                v.val = -_v + msbMask + (m >> 1) - 1
        v._dtype = v._dtype.__copy__()
        v._dtype = self._dtype.__copy__()
        v._dtype.signed = signed
        return v

    def cast(self, t: Bits3t) -> "Bits3val":
        """
        C++: static_cast<t>(self)

        :note: no sign extension
        """
        v = self.__copy__()
        v._dtype = t
        m = t.all_mask()
        v.val &= m
        v.vld_mask &= m
        if t.signed:
            v.val = to_signed(v.val, t.bit_length())
        return v

    def _concat(self, other: "Bits3val") -> "Bits3val":
        """
        Concatenate two bit vectors together
        Verilog: {self, other}, VHDL: self & other
        """
        if not isinstance(other, Bits3val):
            raise TypeError(other)
        w = self._dtype.bit_length()
        other_w = other._dtype.bit_length()
        resWidth = w + other_w
        resT = self._dtype.__class__(resWidth, signed=self._dtype.signed)

        v = self.__copy__()
        v.val = (v.val << other_w) | other.val
        v.vld_mask = (v.vld_mask << other_w) | other.vld_mask
        v._dtype = resT
        return v

    def __getitem__(self, key: Union[int, slice, "Bits3val"]) -> "Bits3val":
        "self[key]"
        if isinstance(key, slice):
            firstBitNo, size = normalize_slice(key, self._dtype.bit_length())
            val = get_bit_range(self.val, firstBitNo, size)
            vld = get_bit_range(self.vld_mask, firstBitNo, size)
        elif isinstance(key, (int, Bits3val)):
            size = 1
            try:
                _i = int(key)
            except ValidityError:
                _i = None

            if _i is None:
                val = 0
                vld = 0
            else:
                if _i < 0 or _i >= self._dtype.bit_length():
                    raise IndexError("Index out of range", _i)

                val = get_bit(self.val, _i)
                vld = get_bit(self.vld_mask, _i)
        else:
            raise TypeError(key)

        new_t = self._dtype.__class__(size, signed=self._dtype.signed)
        return new_t._from_py(val, vld)

    def __setitem__(self, index: Union[slice, int, "Bits3val"],
                    value: Union["Bits3val", int]):
        "An item assignment operator self[index] = value."
        if isinstance(index, slice):
            firstBitNo, size = normalize_slice(index, self._dtype.bit_length())
            if isinstance(value, Bits3val):
                v = value.val
                m = value.vld_mask
            else:
                v = value
                m = mask(size)

            self.val = set_bit_range(self.val, firstBitNo, size, v)
            self.vld_mask = set_bit_range(
                self.vld_mask, firstBitNo, size, m)
        else:
            if index is None:
                raise TypeError(index)
            try:
                _i = int(index)
            except ValidityError:
                _i = None

            if _i is None:
                self.val = 0
                self.vld_mask = 0
            else:
                if value is None:
                    v = 0
                    m = 0
                elif isinstance(value, Bits3val):
                    v = value.val
                    m = value.vld_mask
                else:
                    v = value
                    m = 0b1
                try:
                    index = int(index)
                except ValidityError:
                    index = None
                if index is None:
                    self.val = 0
                    self.vld_mask = 0
                else:
                    self.val = bit_set_to(self.val, index, v)
                    self.vld_mask = bit_set_to(self.vld_mask, index, m)

    def __invert__(self) -> "Bits3val":
        "Operator ~x."
        v = self.__copy__()
        v.val = ~v.val
        w = v._dtype.bit_length()
        v.val &= mask(w)
        if self._dtype.signed:
            v.val = to_signed(v.val, w)
        return v

    def __neg__(self):
        "Operator -x."
        if not self._dtype.signed:
            raise TypeError("unsigned")

        v = self.__copy__()
        _v = -v.val
        _max = self._dtype.all_mask() >> 1
        _min = -_max - 1
        if _v > _max:
            _v = _min + (_v - _max - 1)
        elif _v < _min:
            _v = _max - (_v - _min + 1)
        v.val = _v
        return v

    def __hash__(self):
        return hash((self._dtype, self.val, self.vld_mask))

    def _is(self, other):
        """check if other is object with same values"""
        return isinstance(other, Bits3val)\
            and self._dtype == other._dtype\
            and self.val == other.val\
            and self.vld_mask == other.vld_mask

    def _eq(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        """
        Operator self._eq(other) as self == other
        == is not overriden in order to prevent tricky behavior if hashing partially valid values
        """
        return bitsCmp__val(self, other, eq)

    def __req__(self, other: int) -> "Bits3val":
        "Operator ==."
        return bitsCmp__val(self._dtype.from_py(other), self, eq)

    def __ne__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator !=."
        return bitsCmp__val(self, other, ne)

    def __rne__(self, other: int) -> "Bits3val":
        "Operator !=."
        return bitsCmp__val(self._dtype.from_py(other), self, ne)

    def __lt__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator <."
        return bitsCmp__val(self, other, lt)

    def __rlt__(self, other: int) -> "Bits3val":
        "Operator <."
        return bitsCmp__val(self._dtype.from_py(other), self, lt)

    def __gt__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator >."
        return bitsCmp__val(self, other, gt)

    def __rgt__(self, other: int) -> "Bits3val":
        "Operator >."
        return bitsCmp__val(self._dtype.from_py(other), self, gt)

    def __ge__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator >=."
        return bitsCmp__val(self, other, ge)

    def __rge__(self, other: int) -> "Bits3val":
        "Operator >=."
        return bitsCmp__val(self._dtype.from_py(other), self, ge)

    def __le__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator <=."
        return bitsCmp__val(self, other, le)

    def __rle__(self, other: int) -> "Bits3val":
        "Operator <=."
        return bitsCmp__val(self._dtype.from_py(other), self, le)

    def __xor__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator ^."
        return bitsBitOp__val(self, other, xor, vld_mask_for_xor)

    def __rxor__(self, other: int) -> "Bits3val":
        "Operator ^."
        return bitsBitOp__val(self._dtype.from_py(other), self, xor,
                              vld_mask_for_xor)

    def __and__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator &."
        return bitsBitOp__val(self, other, and_, vld_mask_for_and)

    def __rand__(self, other: int) -> "Bits3val":
        "Operator &."
        return bitsBitOp__val(self._dtype.from_py(other), self, and_,
                              vld_mask_for_and)

    def __or__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator |."
        return bitsBitOp__val(self, other, or_, vld_mask_for_or)

    def __ror__(self, other: int) -> "Bits3val":
        "Operator |."
        return bitsBitOp__val(self._dtype.from_py(other), self, or_,
                              vld_mask_for_or)

    def __sub__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator -."
        return bitsArithOp__val(self, other, sub)

    def __rsub__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator -."
        return bitsArithOp__val(self._dtype.from_py(other), self, sub)

    def __add__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator +."
        return bitsArithOp__val(self, other, add)

    def __radd__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator +."
        return bitsArithOp__val(self._dtype.from_py(other), self, add)

    def __rshift__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator >>."
        try:
            o = int(other)
        except ValidityError:
            o = None
        v = self.__copy__()
        if o is None:
            v.vld_mask = 0
            v.val = 0
        elif o == 0:
            return v
        else:
            if o < 0:
                raise ValueError("negative shift count")
            w = self._dtype.bit_length()
            v.vld_mask >>= o
            v.vld_mask |= bit_field(w - o, w)
            if v.val < 0:
                assert self._dtype.signed
                v.val = to_unsigned(v.val, w)
            v.val >>= o

        return v

    def __lshift__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator <<."
        try:
            o = int(other)
        except ValidityError:
            o = None

        v = self.__copy__()
        if o is None:
            v.vld_mask = 0
            v.val = 0
        elif o == 0:
            return v
        else:
            if o < 0:
                raise ValueError("negative shift count")
            t = self._dtype
            m = t.all_mask()
            v.vld_mask <<= o
            v.vld_mask |= mask(o)
            v.vld_mask &= m
            v.val <<= o
            v.val &= m
            if t.signed:
                v.val = to_signed(v.val, t.bit_length())
        return v

    def __floordiv__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator //."
        other_is_int = isinstance(other, int)
        if other_is_int:
            v = self.val // other
            m = self._dtype.all_mask()
        else:
            if self._is_full_valid() and other._is_full_valid():
                v = self.val // other.val
                m = self._dtype.all_mask()
            else:
                v = 0
                m = 0
        return self._dtype._from_py(v, m)

    def __mul__(self, other: Union[int, "Bits3val"]) -> "Bits3val":
        "Operator *."
        # [TODO] resT should be wider
        resT = self._dtype
        other_is_int = isinstance(other, int)
        if other_is_int:
            v = self.val * other
        elif isinstance(other, Bits3val):
            v = self.val * other.val
        else:
            raise TypeError(other)

        v &= resT.all_mask()
        if resT.signed:
            v = to_signed(v, resT.bit_length())

        if self._is_full_valid() and (other_is_int
                                      or other._is_full_valid()):
            vld_mask = resT._all_mask
        else:
            vld_mask = 0

        return resT._from_py(v, vld_mask)

    def _ternary(self, a, b):
        """
        Ternary operator (a if self else b).
        """
        try:
            if self:
                return a
            else:
                return b
        except ValidityError:
            pass
        res = copy(a)
        res.vld_mask = 0
        return res

    def __repr__(self):
        if self.vld_mask != self._dtype.all_mask():
            m = ", mask {0:x}".format(self.vld_mask)
        else:
            m = ""
        return "<{0:s} {1:s}{2:s}>".format(
            self.__class__.__name__, repr(self.val), m)


def bitsBitOp__val(self: Bits3val, other: Union[Bits3val, int],
                   evalFn, getVldFn) -> "Bits3val":
    """
    Apply bitwise operator
    """
    res_t = self._dtype
    if isinstance(other, int):
        other = res_t.from_py(other)
    w = res_t.bit_length()
    assert w == other._dtype.bit_length(), (res_t, other._dtype)
    vld = getVldFn(self, other)
    res = evalFn(self.val, other.val) & vld
    if res_t.signed:
        res = to_signed(res, w)

    return res_t._from_py(res, vld)


def bitsCmp__val(self: Bits3val, other: Union[Bits3val, int],
                 evalFn) -> "Bits3val":
    """
    Apply comparative operator
    """
    t = self._dtype
    if isinstance(other, int):
        other = t.from_py(other)
        ot = other._dtype
        w = t.bit_length()
    else:
        ot = other._dtype
        w = t.bit_length()
        if t.signed != ot.signed or w != ot.bit_length():
            raise TypeError(t, ot)

    vld = self.vld_mask & other.vld_mask
    _vld = int(vld == t._all_mask)
    res = evalFn(self.val, other.val) & _vld

    return self._BOOL._from_py(int(res), int(_vld))


def bitsArithOp__val(self: Bits3val, other: Union[Bits3val, int],
                     evalFn) -> "Bits3val":
    """
    Apply arithmetic operator
    """
    if isinstance(other, int):
        other = self._dtype.from_py(other)
    v = self.__copy__()
    self_vld = self._is_full_valid()
    other_vld = other._is_full_valid()

    v.val = evalFn(self.val, other.val)

    w = v._dtype.bit_length()
    if self._dtype.signed:
        _v = v.val
        _max = mask(w - 1)
        _min = -_max - 1
        if _v > _max:
            _v = _min + (_v - _max - 1)
        elif _v < _min:
            _v = _max - (_v - _min + 1)

        v.val = _v
    else:
        v.val &= mask(w)

    if self_vld and other_vld:
        v.vld_mask = mask(w)
    else:
        v.vld_mask = 0

    return v

