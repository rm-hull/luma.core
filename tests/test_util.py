#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-20 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.util` module.
"""


from luma.core import util

from helpers import get_reference_file


test_config_file = get_reference_file('config-test.txt')


def test_mutablestring():
    f = util.mutable_string('bar')
    f[1] = '2'
    assert f == 'b2r'
    assert repr(f) == repr('b2r')
    assert len(f) == 3


def test_mutablestring_unicode():
    f = util.mutable_string(u'bazül')
    f[4] = 'L'
    assert f == u'baz\xfcL'
    assert repr(f) == repr(u'baz\xfcL')
    assert len(f) == 5


def test_from_16_to_8_to_16():
    """
    Test the conversion from 16 bit to 8 bit values and back.  Ensure that conversion
    from 8 to 16 bit takes into account whether the 16 bit value is negative or
    positive
    """
    data = [1, 2, 3, 2**15, 2**16 - 1]
    expect = [0, 1, 0, 2, 0, 3, 0x80, 0, 0xFF, 0xFF]

    result = util.from_16_to_8(data)
    assert result == expect

    expect = [1, 2, 3, -32768, -1]
    result = util.from_8_to_16(result)
    assert result == expect


def test_bytes_to_nibbles():
    """
    Test the conversion from 8 bit values into 4 bit (nibbles)
    """
    data = [0, 1, 2, 3, 0xFF, 0x7F]
    expect = [0, 0, 0, 1, 0, 2, 0, 3, 15, 15, 7, 15]

    result = util.bytes_to_nibbles(data)
    assert result == expect
