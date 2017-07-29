#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
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
    assert repr(f) == "'b2r'"
    assert len(f) == 3
