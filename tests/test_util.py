#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.util` module.
"""

import sys

import pytest

from luma.core import util

from helpers import get_reference_file, patch, Mock


test_config_file = get_reference_file('config-test.txt')


def test_deprecation():
    """
    ``deprecated`` creates a DeprecationWarning.
    """
    class DeprecatedClass(object):
        def __init__(self):
            self.msg = 'Deprecated; will be removed in 0.0.1'
            util.deprecation(self.msg)

    with pytest.deprecated_call() as c:
        d = DeprecatedClass()
        assert str(c.list[0].message) == d.msg


def test_get_interface_types():
    """
    Enumerate interface types.
    """
    assert util.get_interface_types() == ["i2c", "spi"]


def test_get_display_types():
    """
    Enumerate display types.
    """
    assert list(util.get_display_types().keys()) == [
        'oled', 'lcd', 'led_matrix', 'emulator']


def test_get_choices_unknown_module():
    """
    get_choices returns an empty list when trying to inspect an unknown module.
    """
    result = util.get_choices('foo')
    assert result == []


def test_load_config_file_parse():
    """
    load_config parses a text file and returns a list of arguments.
    """
    result = util.load_config(test_config_file)
    assert result == [
        '--display=capture',
        '--width=800',
        '--height=8600',
        '--spi-bus-speed=16000000'
    ]


def test_create_parser():
    """
    create_parser returns an argument parser instance.
    """
    sys.modules['luma.emulator.render'] = Mock()

    with patch('luma.core.util.get_display_types') as mocka:
        mocka.return_value = {
            'foo': ['a', 'b'],
            'bar': ['c', 'd'],
            'emulator': ['e', 'f']
        }
        parser = util.create_parser(description='test')
        args = parser.parse_args(['-f', test_config_file])
        assert args.config == test_config_file
