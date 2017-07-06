#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.util` module.
"""


import pytest

from luma.core import util

from helpers import get_reference_file


test_config_file = get_reference_file('config-test.txt')


def test_deprecation():
    """
    ``deprecated`` creates a DeprecationWarning.
    """
    class DeprecatedClass(object):
        def __init__(self):
            self.msg = 'Deprecated; will be removed in 0.0.1'
            util.deprecation(self.msg)

    with pytest.deprecated_call():
        DeprecatedClass()


def test_mutablestring():
    f = util.mutable_string('bar')
    f[1] = '2'
    assert f == 'b2r'
    assert repr(f) == "'b2r'"
    assert len(f) == 3
