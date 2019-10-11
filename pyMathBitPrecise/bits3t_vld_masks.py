#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


def vld_mask_for_and(a, b):
    # (val, vld)
    # (0, 0) & (0, 0) -> (0, 0)
    # (0, 1) & (0, 0) -> (0, 1)
    # (0, 0) & (0, 1) -> (0, 1)
    # (1, 1) & (0, 0) -> (0, 0)

    a_vld = (a.vld_mask & ~a.val)
    b_vld = (b.vld_mask & ~b.val)
    vld = (a.vld_mask & b.vld_mask) | a_vld | b_vld
    return vld


def vld_mask_for_or(a, b):
    a_vld = (a.vld_mask & a.val)
    b_vld = (b.vld_mask & b.val)
    vld = (a.vld_mask & b.vld_mask) | a_vld | b_vld
    return vld


def vld_mask_for_xor(a, b):
    return a.vld_mask & b.vld_mask
