#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.device.parallel_device` class.
"""

from unittest.mock import Mock, call
from luma.core.device import parallel_device


def test_4bit():
    serial = Mock(unsafe=True)
    serial._bitmode = 4
    serial._pulse_time = 1
    pd = parallel_device(serial_interface=serial)

    pd.command(0x10, 0x11, 0xff)
    pd.data([0x41, 0x42, 0x43])

    comm = call(0x01, 0x00, 0x01, 0x01, 0x0f, 0x0f)
    data = call([0x04, 0x01, 0x04, 0x02, 0x04, 0x03])
    serial.command.assert_has_calls([comm])
    serial.data.assert_has_calls([data])


def test_8bit():
    serial = Mock(unsafe=True)
    serial._bitmode = 8
    serial._pulse_time = 1
    pd = parallel_device(serial_interface=serial)

    pd.command(0x10, 0x11, 0xff)
    pd.data([0x41, 0x42, 0x43])

    comm = call(0x10, 0x11, 0xff)
    data = call([0x41, 0x42, 0x43])
    serial.command.assert_has_calls([comm])
    serial.data.assert_has_calls([data])
