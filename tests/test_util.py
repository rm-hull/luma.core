#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
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
