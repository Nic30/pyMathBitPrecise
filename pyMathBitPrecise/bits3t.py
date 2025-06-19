#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from copy import copy
from enum import Enum
from math import log2, ceil
from operator import le, ge, gt, lt, ne, eq, and_, or_, xor, sub, add
from typing import Union, Optional, Callable, Self, Literal

from pyMathBitPrecise.array3t import Array3t
from pyMathBitPrecise.bit_utils import mask, get_bit, get_bit_range, \
    to_signed, set_bit_range, bit_set_to, bit_field, to_unsigned, INT_BASES, \
    ValidityError, normalize_slice, rotate_right, rotate_left
from pyMathBitPrecise.bits3t_vld_masks import vld_mask_for_xor, vld_mask_for_and, \
    vld_mask_for_or


class _NOT_SPECIFIED:

    def __init__(self):
        raise AssertionError("This class should be used as a constant")


class Bits3t():
    """
    Meta type for integer of specified size where
    each bit can be '1', '0' or 'X' for undefined value.

    :ivar ~.bit_length: number representation of value of this type
    :ivar ~.signed: flag which tells if this type is signed or not
    :ivar ~._all_mask: cached value of mask for all bits
    :ivar ~.name: name for annotation
    :ivar ~.force_vector: use always hdl vector type
            (for example std_logic_vector(0 downto 0)
             instead of std_logic in VHDL,
             wire[1] instead of wire)
    :ivar ~.strict_sign: same thing as strict_width just for signed/unsigned
    :ivar ~.strict_width: if True the arithmetic, bitwise
        and comparison operators can be performed only on value
        of this exact same width
    :note: operation is not strict if at least one operand
        does not have strict flag set,
        the result width/sign is taken from other operand
        (or first if both are not strict)
    """

    def __init__(self, bit_length: int, signed:Optional[bool]=False, name: Optional[str]=None,
                 force_vector=False,
                 strict_sign=True, strict_width=True):
        if force_vector and bit_length != 1:
            assert bit_length == 1, "force_vector=True is appliable only for 1b values"
        self._bit_length = bit_length
        self.signed = signed
        self._all_mask = mask(bit_length)
        self.name = name
        self.force_vector = force_vector
        self.strict_sign = strict_sign
        self.strict_width = strict_width

    def _createMutated(self,
            bit_length: int=_NOT_SPECIFIED,
            signed:Optional[bool]=_NOT_SPECIFIED, name: Optional[str]=_NOT_SPECIFIED,
            force_vector=_NOT_SPECIFIED,
            strict_sign=_NOT_SPECIFIED,
            strict_width=_NOT_SPECIFIED) -> Self:
        if bit_length is _NOT_SPECIFIED:
            bit_length = self._bit_length
        if signed is  _NOT_SPECIFIED:
            signed = self.signed
        if name  is _NOT_SPECIFIED:
            name = self.name
        if force_vector is _NOT_SPECIFIED:
            force_vector = self.force_vector
        if strict_sign is _NOT_SPECIFIED:
            strict_sign = self.strict_sign
        if strict_width is _NOT_SPECIFIED:
            strict_width = self.strict_width
        return self.__class__(bit_length, signed=signed, name=name, force_vector=force_vector, strict_sign=strict_sign, strict_width=strict_width)

    def __copy__(self) -> Self:
        t = self.__class__(self._bit_length, signed=self.signed,
                           name=self.name,
                           force_vector=self.force_vector,
                           strict_sign=self.strict_sign,
                           strict_width=self.strict_width)
        return t

    def all_mask(self) -> int:
        """
        :return: mask for bites of this type ( 0b111 for Bits(3) )
        """
        return self._all_mask

    def get_domain_range(self):
        m = self.all_mask()
        if self.signed:
            intMin = -(m // 2) - 1
            intMax = m // 2
        else:
            intMin = 0
            intMax = m
        return (intMin, intMax)

    def bit_length(self) -> int:
        """
        :return: number of bits required for representation
            of value of this type
        """
        return self._bit_length

    def __eq__(self, other) -> bool:
        return (self is other
                or (isinstance(other, Bits3t)
                    and self._bit_length == other._bit_length
                    and self.name == other.name
                    and self.force_vector == other.force_vector
                    and self.strict_sign == other.strict_sign
                    and self.strict_width == other.strict_width
                    and self.signed == other.signed
                    )
                )

    def _normalize_val_and_mask(self, val: Optional[int], vld_mask: Optional[int]) -> tuple[int, int]:
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
                    raise ValueError("Mask in incorrect format", vld_mask, w, all_mask)
                vld = vld_mask

            if val < 0:
                if not self.signed:
                    raise ValueError("Negative value for unsigned int")
                _val = to_signed(val & all_mask, w)
                if _val != val:
                    raise ValueError("Too large value", val, _val)
                val = to_unsigned(_val, w)
            else:
                if self.signed:
                    msb = 1 << (w - 1)
                    if msb & val:
                        if val > 0:
                            raise ValueError(
                                "Value too large to fit in this type", val)

                if val & all_mask != val:
                    raise ValueError(
                        "Not enough bits to represent value",
                        val, "on", w, "bit" if w == 1 else "bits", val & all_mask)
                val = val & vld
        return val, vld

    def _from_py(self, val: int, vld_mask: int) -> "Bits3val":
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
            constr.append(f'"{self.name:s}"')
        c = self.bit_length()

        if self.signed:
            sign = "i"
        elif self.signed is False:
            sign = "u"
        else:
            sign = "b"

        constr.append(f"{sign:s}{c:d}")
        if self.force_vector:
            constr.append("force_vector")

        if not self.strict_sign:
            constr.append("strict_sign=False")
        if not self.strict_width:
            constr.append("strict_width=False")

        return "<%s %s>" % (self.__class__.__name__,
                             ", ".join(constr))


class Bits3val():
    """
    Class for value of `Bits3t` type

    :ivar ~._dtype: reference on type of this value
    :ivar ~.val: always unsigned representation int value
    :note: the reason why the unsigned is always used is that
        the signed variant would require cast to unsigned on every bitwise operation
    :ivar ~.vld_mask: always unsigned value of the mask, if bit in mask is '0'
            the corresponding bit in val is invalid
    """
    _BOOL = Bits3t(1)
    _SIGNED_FOR_SLICE_RESULT = False
    _SIGNED_FOR_CONCAT_RESULT = False

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

    def __copy__(self) -> Self:
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
            raise ValidityError(self)
        if self._dtype.signed:
            return to_signed(self.val, self._dtype.bit_length())
        else:
            return self.val

    def __bool__(self) -> bool:
        "bool(self)"
        return bool(self.__int__())

    def _auto_cast(self, dtype):
        """
        Cast value to a compatible type
        """
        return dtype.from_py(self.val, self.vld_mask)

    def _cast_sign(self, signed: Optional[bool]) -> Self:
        """
        Cast signed-unsigned value
        """
        t = self._dtype
        if t.signed == signed:
            return self
        selfSign = t.signed
        v = self.__copy__()
        m = t._all_mask
        _v = v.val

        if selfSign and not signed:
            if _v < 0:
                v.val = m + _v + 1

        v._dtype = v._dtype.__copy__()
        v._dtype = self._dtype.__copy__()
        v._dtype.signed = signed
        return v

    def _concat(self, other: "Bits3val") -> Self:
        """
        Concatenate two bit vectors together (self will be at MSB side)
        Verilog: {self, other}, VHDL: self & other
        """
        if not isinstance(other, Bits3val):
            raise TypeError(other)
        w = self._dtype.bit_length()
        other_w = other._dtype.bit_length()
        resWidth = w + other_w
        resT = self._dtype.__class__(resWidth, signed=self._SIGNED_FOR_CONCAT_RESULT)
        other_val = other.val
        if other_val < 0:
            other_val = to_unsigned(other_val, other_w)
        v = self.__copy__()
        if v.val < 0:
            v.val = to_unsigned(v.val, w)
        v.val = (v.val << other_w) | other_val
        v.vld_mask = (v.vld_mask << other_w) | other.vld_mask
        v._dtype = resT
        return v

    def _ext(self, newWidth: Union[int, Self], signed: Union[bool, Literal[_NOT_SPECIFIED]]=_NOT_SPECIFIED) -> Self:
        """
        :note: preserves sign of type
        """
        if signed is _NOT_SPECIFIED:
            signed = self._dtype.signed
        if signed:
            return self._sext(newWidth)
        else:
            return self._zext(newWidth)

    def _sext(self, newWidth: Union[int, Self]) -> Self:
        """
        signed extension, pad with MSB bit on MSB side to newWidth result width
        :see: :meth:`Bits3val._ext`
        """
        t = self._dtype
        w = t.bit_length()
        if newWidth == w:
            return self
        assert newWidth > w, (newWidth, w)
        resTy = t._createMutated(newWidth)
        val = self.val
        newBitsMask = bit_field(w, newWidth)
        if get_bit(val, w - 1):
            val |= newBitsMask
        vldMask = self.vld_mask
        if get_bit(vldMask, w - 1):
            vldMask |= newBitsMask

        return resTy._from_py(val, vldMask)
        # alfternatively:
        # sign_bit = 1 << (bits - 1)
        # return (value & (sign_bit - 1)) - (value & sign_bit)

    def _zext(self, newWidth: Union[int, Self]) -> Self:
        """
        zero extension, pad with 0 on msb side to newWidth result width
        :see: :meth:`Bits3val._ext`
        """

        t = self._dtype
        w = t.bit_length()
        if newWidth == w:
            return self
        assert newWidth > w, (newWidth, w)
        resTy = t._createMutated(newWidth)
        return resTy.from_py(self.val, vld_mask=self.vld_mask | bit_field(w, newWidth))

    def _trunc(self, newWidth: Union[int, Self]) -> Self:
        assert newWidth > 0, newWidth
        w = self._dtype.bit_length()
        assert newWidth <= w, newWidth
        resTy = self._dtype._createMutated(newWidth)
        resMask = mask(newWidth)
        return resTy._from_py(self.val & resMask, self.vld_mask & resMask)

    def _extOrTrunc(self, newWidth: int, signed: Union[bool, Literal[_NOT_SPECIFIED]]=_NOT_SPECIFIED) -> Self:
        w = self._dtype.bit_length()
        if w < newWidth:
            return self._ext(newWidth, signed)
        elif w > newWidth:
            return self._trunc(newWidth)
        else:
            return self

    def __getitem__(self, key: Union[int, slice, Self]) -> Self:
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

        new_t = self._dtype._createMutated(size, signed=self._SIGNED_FOR_SLICE_RESULT)
        return new_t._from_py(val, vld)

    def __setitem__(self, index: Union[slice, int, Self],
                    value: Union[int, Self]):
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

    def __invert__(self) -> Self:
        "Operator ~x."
        v = self.__copy__()
        v.val = ~v.val
        w = v._dtype.bit_length()
        v.val &= mask(w)
        if v.val < 0:
            v.val = to_unsigned(v.val, w)

        return v

    def __neg__(self) -> Self:
        "Operator -x."
        v = self.__copy__()
        width = self._dtype.bit_length()
        _v = -to_signed(v.val, width)
        v.val = to_unsigned(_v, width)
        return v

    def __hash__(self) -> int:
        return hash((self._dtype, self.val, self.vld_mask))

    def _is(self, other) -> bool:
        """check if other is object with same values"""
        return isinstance(other, Bits3val)\
            and self._dtype == other._dtype\
            and self.val == other.val\
            and self.vld_mask == other.vld_mask

    def _eq(self, other: Union[int, Self]) -> Self:
        """
        Operator self._eq(other) as self == other
        == is not overridden in order to prevent tricky behavior if hashing partially valid values
        """
        return bitsCmp__val(self, other, eq)

    def __req__(self, other: int) -> Self:
        "Operator ==."
        return bitsCmp__val(self._dtype.from_py(other), self, eq)

    def __ne__(self, other: Union[int, Self]) -> Self:
        "Operator !=."
        return bitsCmp__val(self, other, ne)

    def __rne__(self, other: int) -> Self:
        "Operator !=."
        return bitsCmp__val(self._dtype.from_py(other), self, ne)

    def __lt__(self, other: Union[int, Self]) -> Self:
        "Operator <."
        return bitsCmp__val(self, other, lt)

    def __rlt__(self, other: int) -> Self:
        "Operator <."
        return bitsCmp__val(self._dtype.from_py(other), self, lt)

    def __gt__(self, other: Union[int, Self]) -> Self:
        "Operator >."
        return bitsCmp__val(self, other, gt)

    def __rgt__(self, other: int) -> Self:
        "Operator >."
        return bitsCmp__val(self._dtype.from_py(other), self, gt)

    def __ge__(self, other: Union[int, Self]) -> Self:
        "Operator >=."
        return bitsCmp__val(self, other, ge)

    def __rge__(self, other: int) -> Self:
        "Operator >=."
        return bitsCmp__val(self._dtype.from_py(other), self, ge)

    def __le__(self, other: Union[int, Self]) -> Self:
        "Operator <=."
        return bitsCmp__val(self, other, le)

    def __rle__(self, other: int) -> Self:
        "Operator <=."
        return bitsCmp__val(self._dtype.from_py(other), self, le)

    def __xor__(self, other: Union[int, Self]) -> Self:
        "Operator ^."
        return bitsBitOp__val(self, other, xor, vld_mask_for_xor)

    def __rxor__(self, other: int) -> Self:
        "Operator ^."
        return bitsBitOp__val(self._dtype.from_py(other), self, xor,
                              vld_mask_for_xor)

    def __and__(self, other: Union[int, Self]) -> Self:
        "Operator &."
        return bitsBitOp__val(self, other, and_, vld_mask_for_and)

    def __rand__(self, other: int) -> Self:
        "Operator &."
        return bitsBitOp__val(self._dtype.from_py(other), self, and_,
                              vld_mask_for_and)

    def __or__(self, other: Union[int, Self]) -> Self:
        "Operator |."
        return bitsBitOp__val(self, other, or_, vld_mask_for_or)

    def __ror__(self, other: int) -> Self:
        "Operator |."
        return bitsBitOp__val(self._dtype.from_py(other), self, or_,
                              vld_mask_for_or)

    def __sub__(self, other: Union[int, Self]) -> Self:
        "Operator -."
        return bitsArithOp__val(self, other, sub)

    def __rsub__(self, other: Union[int, Self]) -> Self:
        "Operator -."
        return bitsArithOp__val(self._dtype.from_py(other), self, sub)

    def __add__(self, other: Union[int, Self]) -> Self:
        "Operator +."
        return bitsArithOp__val(self, other, add)

    def __radd__(self, other: Union[int, Self]) -> Self:
        "Operator +."
        return bitsArithOp__val(self._dtype.from_py(other), self, add)

    def __rshift__(self, other: Union[int, Self]) -> Self:
        "Operator >>."
        if self._dtype.signed:
            return bitsBitOp__ashr(self, other)
        else:
            return bitsBitOp__lshr(self, other)

    def __lshift__(self, other: Union[int, Self]) -> Self:
        "Operator <<. (shifts in 0)"
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
            assert v.val >= 0, v.val
        return v

    def __floordiv__(self, other: Union[int, Self]) -> Self:
        "Operator //."
        other_is_int = isinstance(other, int)
        t = self._dtype
        if other_is_int:
            v0 = self.val
            if t.signed:
                w = t.bit_length()
                v0 = to_signed(v0, w)
            v = v0 // other
            m = self._dtype.all_mask()
        else:
            if self._is_full_valid() and other._is_full_valid():
                v0 = self.val
                v1 = other.val
                if t.signed:
                    w = t.bit_length()
                    v0 = to_signed(v0, w)
                    v1 = to_signed(v1, w)
                v = v0 // v1
                m = self._dtype.all_mask()
            else:
                v = 0
                m = 0
        return self._dtype._from_py(v, m)

    def __mul__(self, other: Union[int, Self]) -> Self:
        "Operator *."
        resT = self._dtype
        other_is_int = isinstance(other, int)
        if other_is_int:
            v0 = self.val
            if resT.signed:
                w = resT.bit_length()
                v0 = to_signed(v0, w)

            v = v0 * other
        elif isinstance(other, Bits3val):
            v0 = self.val
            v1 = other.val
            if resT.signed:
                w = resT.bit_length()
                v0 = to_signed(v0, w)
                v1 = to_signed(v1, w)

            v = v0 * v1
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

    def __mod__(self, other: Union[int, Self]) -> Self:
        "Operator %."
        resT = self._dtype
        other_is_int = isinstance(other, int)
        if other_is_int:
            v0 = self.val
            if resT.signed:
                w = resT.bit_length()
                v0 = to_signed(v0, w)

            v = v0 % other
        elif isinstance(other, Bits3val):
            v0 = self.val
            v1 = other.val
            if resT.signed:
                w = resT.bit_length()
                v0 = to_signed(v0, w)
                v1 = to_signed(v1, w)

            v = v0 % v1
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
        t = self._dtype
        if self.vld_mask != t.all_mask():
            m = ", mask {0:x}".format(self.vld_mask)
        else:
            m = ""
        typeDescrChar = 'b' if t.signed is None else 'i' if t.signed else 'u'
        if t.bit_length() == 1 and t.force_vector:
            vecSpec = "vec"
        else:
            vecSpec = ""
        return (f"<{self.__class__.__name__:s} {typeDescrChar:s}{t.bit_length():d}{vecSpec:s}"
                f" {to_signed(self.val, t.bit_length()) if t.signed else self.val:d}{m:s}>")


def bitsBitOp__ror(self: Bits3val, shAmount: Union[Bits3val, int]):
    """
    rotate right by specified amount
    """
    t = self._dtype
    width = t.bit_length()
    try:
        shAmount = int(shAmount)
    except ValidityError:
        return t.from_py(None)
    assert shAmount >= 0

    v = rotate_right(self.val, width, shAmount)
    if t.signed:
        v = to_signed(v, width)
    return t.from_py(v, rotate_right(self.vld_mask, width, shAmount))


def bitsBitOp__rol(self: Bits3val, shAmount: Union[Bits3val, int]):
    """
    rotate left by specified amount
    """
    t = self._dtype
    width = t.bit_length()
    try:
        shAmount = int(shAmount)
    except ValidityError:
        return t.from_py(None)
    assert shAmount >= 0
    v = rotate_left(self.val, width, shAmount)
    if t.signed:
        v = to_signed(v, width)
    return t.from_py(v, rotate_left(self.vld_mask, width, shAmount))


def bitsBitOp__lshr(self: Bits3val, shAmount: Union[Bits3val, int]) -> Bits3val:
    """
    logical shift right (shifts in 0)
    """
    t = self._dtype
    width = t.bit_length()
    try:
        sh = int(shAmount)
    except ValidityError:
        return t.from_py(None)
    assert sh >= 0, sh

    if sh >= width:
        # all bits are shifted out
        return t.from_py(0, mask(width))

    v = self.val >> sh
    if t.signed:
        v = to_signed(v, width)
    newBitsMask = bit_field(width - sh, width)
    return t.from_py(v, (self.vld_mask >> sh) | newBitsMask)


def bitsBitOp__ashr(self: Bits3val, shAmount: Union[Bits3val, int]) -> Bits3val:
    """
    arithmetic shift right (shifts in MSB)
    """
    try:
        sh = int(shAmount)
    except ValidityError:
        sh = None

    v = self.__copy__()
    if sh is None:
        v.vld_mask = 0
        v.val = 0
    elif sh == 0:
        pass
    else:
        if shAmount < 0:
            raise ValueError("negative shift count")
        w = self._dtype.bit_length()
        if sh < w:
            msb = v.val >> (w - 1)
            newBitsMask = bit_field(w - sh, w)
            v.vld_mask >>= sh
            v.vld_mask |= newBitsMask  # set newly shifted-in bits to defined
            v.val >>= sh
            if msb:
                v.val |= newBitsMask
        else:
            # completely shifted out
            v.val = 0
            v.vld_mask = mask(w)
    return v


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
    assert res >= 0, res

    return res_t._from_py(res, vld)


def bitsCmp__val(self: Bits3val, other: Union[Bits3val, int],
                 evalFn: Callable[[int, int], bool]) -> "Bits3val":
    """
    Apply comparative operator
    """
    t = self._dtype
    w = t.bit_length()
    if isinstance(other, int):
        other = t.from_py(other)
        ot = other._dtype
    else:
        ot = other._dtype
        if bool(t.signed) != bool(ot.signed) or w != ot.bit_length():
            raise TypeError("Value compare supports only same width and sign type", t, ot)

    v0 = self.val
    v1 = other.val
    if t.signed:
        v0 = to_signed(v0, w)
        v1 = to_signed(v1, w)

    vld = self.vld_mask & other.vld_mask
    _vld = int(vld == t._all_mask)
    res = evalFn(v0, v1) & _vld

    return self._BOOL._from_py(int(res), int(_vld))


def bitsArithOp__val(self: Bits3val, other: Union[Bits3val, int],
                     evalFn: Callable[[int, int], int]) -> "Bits3val":
    """
    Apply arithmetic operator
    """
    if isinstance(other, int):
        other = self._dtype.from_py(other)
    v = self.__copy__()
    self_vld = self._is_full_valid()
    other_vld = other._is_full_valid()
    v0 = self.val
    v1 = other.val
    w = v._dtype.bit_length()
    t = self._dtype
    if t.signed:
        v0 = to_signed(v0, w)
        v1 = to_signed(v1, w)

    _v = evalFn(v0, v1)

    if t.signed:
        _v = to_unsigned(_v, w)
    else:
        _v &= mask(w)

    v.val = _v
    if self_vld and other_vld:
        v.vld_mask = mask(w)
    else:
        v.vld_mask = 0

    return v

