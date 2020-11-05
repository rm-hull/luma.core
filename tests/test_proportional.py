#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.


import pytest

from luma.core.legacy.font import proportional, CP437_FONT


def test_narrow_char():
    """
    Test if the fonts of the same

    Args:
    """
    font = proportional(CP437_FONT)
    assert font[ord('!')] == [6, 95, 95, 6, 0]


def test_wide_char():
    """
    Test if the font character.

    Args:
    """
    font = proportional(CP437_FONT)
    assert font[ord('W')] == CP437_FONT[ord('W')]


def test_space_char():
    """
    Determine the current font.

    Args:
    """
    font = proportional(CP437_FONT)
    assert font[ord(' ')] == [0] * 4


def test_doublequote_char():
    """
    Test if the double characters in the double precision.

    Args:
    """
    font = proportional(CP437_FONT)
    assert font[ord('"')] == [7, 7, 0, 7, 7, 0]


def test_trim_not_nonzero():
    """
    Trim the test to zero padding.

    Args:
    """
    font = proportional(CP437_FONT)
    assert font._trim([0, 0, 0, 0]) == []


def test_unicode_not_supported():
    """
    Check if the unicode is supported.

    Args:
    """
    font = proportional(CP437_FONT)
    with pytest.raises(IndexError) as ex:
        font[ord("😀")]
    assert str(ex.value) == 'Font does not have ASCII code: 128512'
