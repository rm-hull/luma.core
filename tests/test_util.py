#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.util` module.
"""

import pytest

from luma.core import util


class DeprecatedClass(object):
    def __init__(self):
        self.msg = 'Deprecated; will be removed in 0.0.1'
        util.deprecation(self.msg)


def test_deprecation():
    with pytest.deprecated_call() as c:
        d = DeprecatedClass()

        assert str(c.list[0].message) == d.msg
