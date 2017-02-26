#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-17 Richard Hull and contributors
# See LICENSE.rst for details.


import time

from luma.core.sprite_system import framerate_regulator


def test_init_default():
    before = time.time()
    regulator = framerate_regulator()
    after = time.time()

    assert regulator.max_sleep_time == 1 / 16.67
    assert before <= regulator.start_time <= after
    assert regulator.start_time == regulator.last_time
    assert regulator.called == 0


def test_init_unlimited():
    before = time.time()
    regulator = framerate_regulator(fps=0)
    after = time.time()

    assert regulator.max_sleep_time == -1
    assert before <= regulator.start_time <= after
    assert regulator.start_time == regulator.last_time
    assert regulator.called == 0


def test_init_30fps():
    before = time.time()
    regulator = framerate_regulator(fps=30.00)
    after = time.time()

    assert regulator.max_sleep_time == 1 / 30.00
    assert before <= regulator.start_time <= after
    assert regulator.start_time == regulator.last_time
    assert regulator.called == 0


def test_sleep():
    before = time.time()
    regulator = framerate_regulator(fps=100.00)
    for _ in range(200):
        regulator.sleep()
    after = time.time()

    assert regulator.called == 200
    assert after - before >= 2.0
