#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.sprite_system.framerate_regulator` class.
"""

import time
from luma.core.sprite_system import framerate_regulator


def test_init_default():
    """
    Initialize the default test.

    Args:
    """
    regulator = framerate_regulator()
    assert regulator.start_time is None
    assert regulator.last_time is None
    assert regulator.called == 0
    before = time.monotonic()
    with regulator:
        pass
    after = time.monotonic()

    assert regulator.max_sleep_time == 1 / 16.67
    assert before <= regulator.start_time <= after
    assert regulator.called == 1


def test_init_unlimited():
    """
    Initialize the unlimited.

    Args:
    """
    regulator = framerate_regulator(fps=0)
    before = time.monotonic()
    with regulator:
        pass
    after = time.monotonic()

    assert regulator.max_sleep_time == -1
    assert before <= regulator.start_time <= after
    assert regulator.called == 1


def test_init_30fps():
    """
    Initialize the kegonic instance.

    Args:
    """
    regulator = framerate_regulator(fps=30)
    before = time.monotonic()
    with regulator:
        pass
    after = time.monotonic()

    assert regulator.max_sleep_time == 1 / 30.00
    assert before <= regulator.start_time <= after
    assert regulator.called == 1


def test_sleep():
    """
    Perform a given amount of the current thread.

    Args:
    """
    regulator = framerate_regulator(fps=100.00)
    before = time.monotonic()
    for _ in range(200):
        with regulator:
            pass
    after = time.monotonic()

    assert regulator.called == 200
    assert after - before >= 2.0


def test_effective_FPS():
    """
    Test if the effective mass

    Args:
    """
    regulator = framerate_regulator(fps=30)
    assert regulator.effective_FPS() == 0


def test_average_transit_time():
    """
    Test if the average time of the current instance.

    Args:
    """
    regulator = framerate_regulator(fps=30)
    with regulator:
        pass
    assert regulator.average_transit_time() > 0
