#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
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


def clean_bit(val: int, bitNo: int) -> int:
    """
    Set a specified bit to '0'
    """
    return val & ~(1 << bitNo)


def set_bit(val: int, bitNo: int) -> int:
    """
    Set a specified bit to '1'
    """
    return val | (1 << bitNo)


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


def apply_set_and_clear(val: int, set_flag: int, clear_flag: int):
    """
    :param val: an input value of the flag(s)
    :param set_flag: a mask of bits to set to 1
    :param clear_flag: a mask of bits to set to 0
    :note: set has higher priority

    :return: new value of the flag
    """
    return (val & ~clear_flag) | set_flag


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


def is_power_of_2(v: Union["Bits3val", int]):
    return ~(v & (v - 1))


def next_power_of_2(v: Union["Bits3val", int], width:Optional[int]=None):
    # depend on the fact that v < 2^width
    v = v - 1
    if isinstance(v, int):
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
