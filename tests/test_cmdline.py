#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.cmdline` module.
"""

import sys

from luma.core import cmdline
from luma.core.serial import __all__ as iface_types

from helpers import get_reference_file, patch, Mock


test_config_file = get_reference_file('config-test.txt')


def test_get_interface_types():
    """
    Enumerate interface types.
    """
    assert cmdline.get_interface_types() == iface_types


def test_get_display_types():
    """
    Enumerate display types.
    """
    assert list(cmdline.get_display_types().keys()) == cmdline.get_supported_libraries()


def test_get_choices_unknown_module():
    """
    get_choices returns an empty list when trying to inspect an unknown module.
    """
    result = cmdline.get_choices('foo')
    assert result == []


def test_load_config_file_parse():
    """
    load_config parses a text file and returns a list of arguments.
    """
    result = cmdline.load_config(test_config_file)
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
    sys.modules['luma.emulator'] = Mock()
    sys.modules['luma.emulator.render'] = Mock()

    with patch('luma.core.cmdline.get_display_types') as mocka:
        mocka.return_value = {
            'foo': ['a', 'b'],
            'bar': ['c', 'd'],
            'emulator': ['e', 'f']
        }
        parser = cmdline.create_parser(description='test')
        args = parser.parse_args(['-f', test_config_file])
        assert args.config == test_config_file
