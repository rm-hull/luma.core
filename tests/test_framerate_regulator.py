#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-17 Richard Hull and contributors
# See LICENSE.rst for details.


import time

from luma.core.sprite_system import framerate_regulator


def test_init_default():
    regulator = framerate_regulator()
    assert regulator.start_time is None
    assert regulator.last_time is None
    assert regulator.called == 0
    before = time.time()
    with regulator:
        pass
    after = time.time()

    assert regulator.max_sleep_time == 1 / 16.67
    assert before <= regulator.start_time <= after
    assert regulator.called == 1


def test_init_unlimited():
    regulator = framerate_regulator(fps=0)
    before = time.time()
    with regulator:
        pass
    after = time.time()

    assert regulator.max_sleep_time == -1
    assert before <= regulator.start_time <= after
    assert regulator.called == 1


def test_init_30fps():
    regulator = framerate_regulator(fps=30)
    before = time.time()
    with regulator:
        pass
    after = time.time()

    assert regulator.max_sleep_time == 1 / 30.00
    assert before <= regulator.start_time <= after
    assert regulator.called == 1


def test_sleep():
    regulator = framerate_regulator(fps=100.00)
    before = time.time()
    for _ in range(200):
        with regulator:
            pass
    after = time.time()

    assert regulator.called == 200
    assert after - before >= 2.0
