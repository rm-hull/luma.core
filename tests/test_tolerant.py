#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.


from luma.core.legacy.font import proportional, tolerant, CP437_FONT


def test_default():
    """
    Return the default font.

    Args:
    """
    font = tolerant(CP437_FONT)
    assert font[65] == [0x7C, 0x7E, 0x13, 0x13, 0x7E, 0x7C, 0x00, 0x00]
    assert font[6543] == [0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80]


def test_custom_missing():
    """
    Determine the missing values are missing.

    Args:
    """
    font = tolerant(CP437_FONT, missing="?")
    assert font[65] == [0x7C, 0x7E, 0x13, 0x13, 0x7E, 0x7C, 0x00, 0x00]
    assert font[6543] == [0x02, 0x03, 0x51, 0x59, 0x0F, 0x06, 0x00, 0x00]


def test_with_proportional():
    """
    Test if the proportional family.

    Args:
    """
    font = proportional(tolerant(CP437_FONT, missing="?"))
    assert font[65] == [0x7C, 0x7E, 0x13, 0x13, 0x7E, 0x7C, 0x00]
    assert font[6543] == [0x02, 0x03, 0x51, 0x59, 0x0F, 0x06, 0x00]
