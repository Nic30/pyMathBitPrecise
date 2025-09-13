#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import math
from typing import List, Tuple, Generator, Union, Optional, Literal, Sequence

from pyMathBitPrecise.utils import grouper


def mask(bits: int) -> int:
    """
    Generate mask of specified size (sequence of '1')
    """
    return (1 << bits) - 1


def bit_field(_from: int, to: int) -> int:
    """
    Generate int which has bits '_from' to 'to' set to '1'

    :note: _from 0 to 1 -> '1'
    """
    w = to - _from
    return mask(w) << _from


def get_bit(val: int, bitNo: int) -> int:
    """
    Get bit from int
    """
    return (val >> bitNo) & 1


def get_bit_range(val: int, bitsStart: int, bitsLen: int) -> int:
    """
    Get sequence of bits from an int value
    """
    val >>= bitsStart
    return val & mask(bitsLen)


def get_single_1_at_position_of_least_significant_0(x: int):
    """
    Hacker's Delight: 2nd Edition, 2-1 Manipulating Rightmost Bits
    
    10100111 -> 00001000
    """
    assert x >= 0, x
    return ~x & (x + 1)


def get_single_0_at_position_of_least_significant_1(x: int, width: int):
    """
    Hacker's Delight: 2nd Edition, 2-1 Manipulating Rightmost Bits
    
    10101000 -> 11110111
    """
    assert x >= 0, x
    res = ~x | (x - 1)
    return to_unsigned(res, width)


def clean_bit(val: int, bitNo: int) -> int:
    """
    Set a specified bit to '0'
    """
    return val & ~(1 << bitNo)


def clear_least_significant_1(x: int) -> int:
    """
    Hacker's Delight: 2nd Edition, 2-1 Manipulating Rightmost Bits
    010110 -> 010100
    
    :note: can be used for 2**n test
    """
    # :note: this is equivalent to x - (x & -x)
    return x & (x - 1)


def clear_trailing_1s(x: int) -> int:
    """
    Hacker's Delight: 2nd Edition, 2-1 Manipulating Rightmost Bits
    10100111 -> 10100000
    
    :note: can be used for 2**n – 1 test
    """
    return x & (x + 1)


def set_bit(val: int, bitNo: int) -> int:
    """
    Set a specified bit to '1'
    """
    return val | (1 << bitNo)


def set_least_significant_0(x: int) -> int:
    """
    Hacker's Delight: 2nd Edition, 2-1 Manipulating Rightmost Bits

    101001 -> 101011
    """
    return x | (x + 1)


def set_trailing_0s(x: int) -> int:
    """
    Hacker's Delight: 2nd Edition, 2-1 Manipulating Rightmost Bits

    10101000 -> 10101111
    """
    return x | (x - 1)


def toggle_bit(val: int, bitNo: int) -> int:
    """
    Toggle specified bit in int
    """
    return val ^ (1 << bitNo)


def set_bit_range(val: int, bitStart: int, bitsLen: int, newBits: int) -> int:
    """
    Set specified range of bits in int to a specified value
    """
    _mask = mask(bitsLen)
    newBits &= _mask

    _mask <<= bitStart
    newBits <<= bitStart

    return (val & ~_mask) | newBits


def bit_set_to(val: int, bitNo: int, bitVal: int) -> int:
    """
    Set specified bit in int to a specified value
    """
    if bitVal == 0:
        return clean_bit(val, bitNo)
    elif bitVal == 1:
        return set_bit(val, bitNo)
    else:
        raise ValueError(("Invalid value of bit to set", bitVal))


def byte_mask_to_bit_mask_int(m: int, width: int, byte_width:int=8) -> int:
    """
    Expands each bit byte_width times to convert from byte mask to bit mask
    """
    res = 0
    mTmp = m
    byte_mask = mask(byte_width)
    for i in range(width):
        b = mTmp & 1
        if b:
            res |= byte_mask << (i * byte_width)
        mTmp >>= 1

    return res


def byte_mask_to_bit_mask(m: "Bits3Val", byte_width:int=8) -> "Bits3Val":
    """
    Replicate each bit byte_width times
    """
    res = None
    for b in m:
        if res is None:
            res = b._sext(byte_width)
        else:
            res = b._sext(byte_width)._concat(res)

    return res


def bit_mask_to_byte_mask_int(m: int, width: int, byte_width:int=8) -> int:
    """
    Compresses all bit in byte to 1 bit to convert from bit mask to byte mask
    """
    assert width % byte_width == 0
    mTmp = m
    res = 0
    byte_mask = mask(byte_width)
    for i in range(width // byte_width):
        B = mTmp & byte_mask
        if B == byte_mask:
            res |= 1 << i
        else:
            assert B == 0, "Each byte must be entirely set or entirely unset"
        mTmp >>= byte_width

    return res


def apply_set_and_clear(val: int, set_flag: int, clear_flag: int):
    """
    :param val: an input value of the flag(s)
    :param set_flag: a mask of bits to set to 1
    :param clear_flag: a mask of bits to set to 0
    :note: set has higher priority

    :return: new value of the flag
    """
    return (val & ~clear_flag) | set_flag


def apply_write_with_mask(current_data: "Bits3val", new_data: "Bits3val", write_mask: "Bits3val") -> "Bits3val":
    """
    :return: an updated value current_data which has bytes defined by write_mask updated from new_data
    """
    m = byte_mask_to_bit_mask(write_mask)
    return apply_set_and_clear(current_data, new_data & m, m)


def extend_to_width_multiple_of_8(v: "Bits3val") -> "Bits3val":
    """
    make width of signal modulo 8 equal to 0
    """
    w = v._dtype.bit_length()
    cosest_multiple_of_8 = math.ceil((w // 8) / 8) * 8
    if cosest_multiple_of_8 == w:
        return v
    else:
        return v._ext(cosest_multiple_of_8)


def align(val: int, lowerBitCntToAlign: int) -> int:
    """
    Cut off lower bits to align a int value.
    """
    val = val >> lowerBitCntToAlign
    return val << lowerBitCntToAlign


def align_with_known_width(val, width: int, lowerBitCntToAlign: int):
    """
    Does same as :func:`~.align` just with the known width of val
    """
    return val & (mask(width - lowerBitCntToAlign) << lowerBitCntToAlign)


def iter_bits(val: int, length: int) -> Generator[Literal[0, 1], None, None]:
    """
    Iterate bits in int. LSB first.
    """
    for _ in range(length):
        yield val & 1
        val >>= 1


def iter_bits_sequences(val: int, length: int) -> Generator[Tuple[Literal[0, 1], int], None, None]:
    """
    Iter tuples (bitVal, number of same bits), lsb first
    """
    assert length > 0, length
    assert val >= 0
    # start of new bit seqence
    w = 1
    valBit = val & 1
    val >>= 1
    foundBit = valBit
    for _ in range(length - 1):
        # extract single bit from val
        valBit = val & 1
        val >>= 1
        # check if it fits into current bit sequence
        if valBit == foundBit:
            w += 1
        else:
            # end of sequence of same bits
            yield (foundBit, w)
            foundBit = valBit
            w = 1

    if w != 0:
        yield (foundBit, w)


def to_signed(val: int, width: int) -> int:
    """
    Convert unsigned int to negative int which has same bits set (emulate sign overflow).

    :note: bits in value are not changed, just python int object
        has signed flag set properly. And number is in expected range.
    """
    if val > 0:
        msb = 1 << (width - 1)
        if val & msb:
            val -= mask(width) + 1
    return val


def to_unsigned(val, width) -> int:
    if val < 0:
        return val & mask(width)
    else:
        return val


def mask_bytes(val: int, byte_mask: int, mask_bit_length: int) -> int:
    """
    Use each bit in byte_mask as a mask for each byte in val.

    :note: Useful for masking of value for HW interfaces where mask
        is represented by a vector of bits where each bit is mask
        for byte in data vector.
    """
    res = 0
    for i, m in enumerate(iter_bits(byte_mask, mask_bit_length)):
        if m:
            res |= (val & 0xff) << (i * 8)
        val >>= 8
    return res


INT_BASES = {
    "b": 2,
    "o": 8,
    "d": 10,
    "h": 16,
}


class ValidityError(ValueError):
    """
    Value is not fully defined and thus can not be used
    """


def normalize_slice(s: slice, obj_width: int) -> Tuple[int, int]:
    start, stop, step = s.start, s.stop, s.step
    if step is not None and step != -1:
        raise NotImplementedError(s.step)
    else:
        step = -1
    if stop is None:
        stop = 0
    else:
        stop = int(stop)

    if start is None:
        start = int(obj_width)
    else:
        start = int(start)
    # n...0
    if start <= stop:
        raise IndexError(s)
    firstBitNo = stop
    size = start - stop
    if start < 0 or stop < 0 or size < 0 or start > obj_width:
        raise IndexError(s)

    return firstBitNo, size


def reverse_bits(val: int, width: int):
    """
    Reverse bits in integer value of specified width
    """
    v = 0
    for i in range(width):
        v |= (get_bit(val, width - i - 1) << i)
    return v


def extend_to_size(collection: Sequence, items: int, pad=0):
    toAdd = items - len(collection)
    assert toAdd >= 0
    for _ in range(toAdd):
        collection.append(pad)

    return collection


def rotate_right(v: int, width: int, shAmount:int):
    # https://www.geeksforgeeks.org/rotate-bits-of-an-integer/
    assert v >= 0, v
    assert width > 0, width
    assert shAmount >= 0, shAmount
    return (v >> shAmount) | ((v << (width - shAmount)) & mask(width))


def rotate_left(v: int, width: int, shAmount:int):
    # https://www.geeksforgeeks.org/rotate-bits-of-an-integer/
    assert v >= 0, v
    assert width > 0, width
    assert shAmount >= 0, shAmount
    return ((v << shAmount) & mask(width)) | (v >> (width - shAmount))


def bit_list_reversed_endianity(bitList: List[Literal[0, 1]], extend=True):
    w = len(bitList)
    i = w

    items = []
    while i > 0:
        # take last 8 bytes or rest
        lower = max(i - 8, 0)
        b = bitList[lower:i]
        if extend:
            extend_to_size(b, 8)
        items.extend(b)
        i -= 8

    return items


def bit_list_reversed_bits_in_bytes(bitList: List[Literal[0, 1]], extend=None):
    "Byte reflection  (0x0f -> 0xf0)"
    w = len(bitList)
    if extend is None:
        assert w % 8 == 0
    tmp = []
    for db in grouper(8, bitList, padvalue=0):
        tmp.extend(reversed(db))

    if not extend and len(tmp) != w:
        rem = w % 8
        # rm zeros from [0, 0, 0, 0, 0, d[2], d[1], d[0]] like
        tmp = tmp[:w - rem] + tmp[-rem:]

    return tmp


def bytes_to_bit_list_lower_bit_first(bytes_: bytes) -> List[Literal[0, 1]]:
    """
    b'\x01' to [1, 0, 0, 0, 0, 0, 0, 0]
    """
    result: List[Literal[0, 1]] = []
    for byte in bytes_:
        for _ in range(8):
            result.append(byte & 0b1)
            byte >>= 1
    return result


def bytes_to_bit_list_upper_bit_first(bytes_: bytes) -> List[Literal[0, 1]]:
    """
    b'\x01' to [0, 0, 0, 0, 0, 0, 0, 1]
    """
    result: List[Literal[0, 1]] = []
    for byte in bytes_:
        for _ in range(8):
            result.append((byte & 0x80) >> 7)
            byte <<= 1
    return result


def byte_list_to_be_int(_bytes: List[Literal[0, 1, 2, 3, 4, 5, 6, 7]]):
    """
    In input list LSB first, in result little endian ([1, 0] -> 0x0001)
    """
    return int_list_to_int(_bytes, 8)


def bit_list_to_int(bitList: List[Literal[0, 1]]):
    """
    In input list LSB first, in result little endian ([0, 1] -> 0b10)
    """
    res = 0
    for i, r in enumerate(bitList):
        res |= (r & 0x1) << i
    return res


def bit_list_to_bytes(bitList: List[Literal[0, 1]]) -> bytes:
    byteCnt = len(bitList) // 8
    if len(bitList) % 8:
        byteCnt += 1
    return bit_list_to_int(bitList).to_bytes(byteCnt, 'big')


def int_list_to_int(il: List[int], item_width: int):
    """
    [0x0201, 0x0403] -> 0x04030201
    """
    v = 0
    for i, b in enumerate(il):
        v |= b << (i * item_width)

    return v


def int_to_int_list(v: int, item_width: int, number_of_items: int):
    """
    opposite of :func:`~.int_list_to_int`
    """
    item_mask = mask(item_width)
    res = []
    for _ in range(number_of_items):
        res.append(v & item_mask)
        v >>= item_width

    assert v == 0, ("there should be nothing left, the value is larger", v)
    return res


def reverse_byte_order(val: "Bits3val"):
    """
    Reverse byteorder (littleendian/bigendian) of signal or value
    """
    w = val._dtype.bit_length()
    i = w
    items = []

    while i > 0:
        # take last 8 bytes or rest
        lower = max(i - 8, 0)
        items.append(val[i:lower])
        i -= 8

    # Concat(*items)
    top = None
    for s in items:
        if top is None:
            top = s
        else:
            top = top._concat(s)
    return top


def reverse_byte_order_int(val: int, width: int):
    assert width % 8 == 0, width
    return int.from_bytes(val.to_bytes(width // 8, "big"), "little")


def is_power_of_2(v: Union["Bits3val", int]):
    if isinstance(v, int):
        assert v > 0
        return (v != 0) & (clear_least_significant_1(v) == 0)
    else:
        return (v != 0) & (clear_least_significant_1(v)._eq(0))


def next_power_of_2(v: Union["Bits3val", int], width:Optional[int]=None):
    # depend on the fact that v < 2^width
    v = v - 1
    if isinstance(v, int):
        assert width is not None
        v = to_unsigned(v, width)
    else:
        width = v._dtype.bit_length()

    i = 1
    while True:
        v |= (v >> i)  # 1, 2, 4, 8, 16 for 32b
        i <<= 1
        if i > width // 2:
            break

    v = v + 1

    if isinstance(v, int):
        v &= mask(width)

    return v


def round_up_to_multiple_of(v: int, divider:int):
    """
    Round up the v to be the multiple of divider
    """
    _v = (v // divider) * divider
    if _v < v:
        return _v + divider
    else:
        return _v


def round_up_to_power_of_2(x: int):
    assert x >= 0, x
    if x == 0:
        return 0
    return int(2 ** math.ceil(math.log2(x)))


def ctlz(Val: int, width: int) -> int:
    """
    Count leading zeros
    """
    if Val == 0:
        return width

    # Bisection method.
    ZeroBits = 0
    if not is_power_of_2(width):
        # because alg. works only for pow2 width
        _w = next_power_of_2(width, 64)
        paddingBits = _w - width
        width = _w
    else:
        paddingBits = 0

    Shift = width >> 1
    while Shift:
        Tmp = Val >> Shift
        if Tmp:
            Val = Tmp
        else:
            ZeroBits |= Shift
        Shift >>= 1
    return ZeroBits - paddingBits


def _ctpop_u64(v: int) -> int:
    v = v - ((v >> 1) & 0x5555555555555555)
    v = (v & 0x3333333333333333) + ((v >> 2) & 0x3333333333333333)
    v = (v + (v >> 4)) & 0x0F0F0F0F0F0F0F0F
    return (v * 0x0101010101010101) >> 56


def ctpop(val: int, width: int):
    """
    count number of 1 in val (population count)
    """
    res = 0
    mask_u64 = mask(64)
    while True:
        res += _ctpop_u64(val & mask_u64)
        width -= 64
        if width <= 0:
            break
        val >>= 64
    return res


def cttz(val: int, width:int):
    """
    Count trailing zeros
    """
    if val == 0:
        return width
    if val & 0x1:
        return 0

    # ctpop method: (x & -x).bit_length() - 1
    # Bisection method.
    ZeroBits = 0
    if not is_power_of_2(width):
        width = next_power_of_2(width, 64)  # because alg. works only for pow2  width
    Shift = width >> 1
    Mask = mask(width) >> Shift
    while Shift:
        if (val & Mask) == 0:
            val >>= Shift
            ZeroBits |= Shift

        Shift >>= 1
        Mask >>= Shift

    return ZeroBits
