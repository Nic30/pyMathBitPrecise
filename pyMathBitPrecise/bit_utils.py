#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from pyMathBitPrecise.utils import grouper


def mask(bits: int):
    """
    Generate mask of sepcified size (sequence of '1')

    :type bits: int
    """
    return (1 << bits) - 1


def bitField(_from: int, to: int):
    """
    Generate int which has bits '_from' to 'to' set to '1'

    :note: _from 0 to 1 -> '1'
    """
    w = to - _from
    return mask(w) << _from


def selectBit(val: int, bitNo: int):
    """
    Get bit from int
    """
    return (val >> bitNo) & 1


def selectBitRange(val: int, bitsStart: int, bitsLen: int):
    """
    Get sequence of bits from an int value
    """
    val >>= bitsStart
    return val & mask(bitsLen)


def cleanBit(val: int, bitNo: int):
    """
    Set a specified bit to '0'
    """
    return val & ~(1 << bitNo)


def setBit(val: int, bitNo: int):
    """
    Set a specified bit to '1'
    """
    return val | (1 << bitNo)


def toogleBit(val: int, bitNo: int):
    """
    Toogle specified bit in int
    """
    return val ^ (1 << bitNo)


def setBitRange(val: int, bitStart: int, bitsLen: int, newBits: int):
    """
    Set specified range of bits in int to a specified value
    """
    _mask = mask(bitsLen)
    newBits &= _mask

    _mask <<= bitStart
    newBits <<= bitStart

    return (val & ~_mask) | newBits


def bitSetTo(val: int, bitNo: int, bitVal: int):
    """
    Set specified bit in int to a specified value
    """
    if bitVal == 0:
        return cleanBit(val, bitNo)
    elif bitVal == 1:
        return setBit(val, bitNo)
    else:
        raise ValueError(("Invalid value of bit to set", bitVal))


def align(val: int, lowerBitCntToAlign: int):
    """
    Cut off lower bits to aligin a int value.
    """
    val = val >> lowerBitCntToAlign
    return val << lowerBitCntToAlign


def iter_bits(val, length):
    """
    Iterate bits in int.
    """
    for _ in range(length):
        yield val & 1
        val >>= 1


def to_signed(val, width):
    """
    Convert too large positive int to negative int which has same bits set.

    :note: bits in value are not changed, just python int object
        has signed flag set properly. And number is in expected range.
    """
    if val > 0:
        msb = 1 << (width - 1)
        if val & msb:
            val -= mask(width) + 1
    return val


def to_unsigned(val, width):
    if val < 0:
        return val & mask(width)
    else:
        return val


def mask_bytes(val, byte_mask, mask_bit_length):
    """
    Use each bit in byte_mask as a mask for each byte in val.

    :note: Usefull for masking of value for HW interfaces where mask
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


def normalize_slice(s, obj_width):
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


def reverseBits(val, width):
    """
    Reverse bits in integer value of specified width
    """
    v = 0
    for i in range(width):
        v |= (selectBit(val, width - i - 1) << i)
    return v


def bitListToInt(bitList):
    """
    List of bits (0/1) to a int value
    little-endian
    """
    res = 0
    for i, r in enumerate(bitList):
        res |= (r & 0x1) << i
    return res


def extendToSize(collection, items, pad=0):
    toAdd = items - len(collection)
    assert toAdd >= 0
    for _ in range(toAdd):
        collection.append(pad)


def bitListReversedEndianity(bitList):
    w = len(bitList)
    i = w

    items = []
    while i > 0:
        # take last 8 bytes or rest
        lower = max(i - 8, 0)
        b = bitList[lower:i]
        extendToSize(b, 8)
        items.extend(b)
        i -= 8

    return items


def bitListReversedBitsInBytes(bitList):
    assert len(bitList) % 8 == 0
    tmp = []
    for db in grouper(8, bitList):
        tmp.extend(reversed(db))
    return tmp
