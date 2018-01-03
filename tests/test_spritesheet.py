#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.sprite_system.spritesheet` class.
"""

import pytest
import PIL

from luma.core.sprite_system import spritesheet


data = {
    'image': "tests/reference/images/runner.png",
    'frames': {
        'width': 64,
        'height': 67,
        'regX': 0,
        'regY': 2
    },
    'animations': {
        'run-right': {
            'frames': range(19, 9, -1),
            'next': "run-right",
        },
        'run-left': {
            'frames': range(0, 10)
        },
        'run-slow': {
            'frames': range(0, 10),
            'speed': 0.5
        },
        'composite': {
            'frames': [1, 2, 3, 'run-left', 4, 5, 6, 'run-left']
        }
    }
}


def test_init():
    sheet = spritesheet(**data)
    # Reframed by 2px
    assert sheet.width == 640
    assert sheet.height == 134
    assert sheet.frames.count == 20
    assert sheet.frames.width == 64
    assert sheet.frames.height == 67
    assert sheet.frames.size == (64, 67)
    assert sheet.cache == {}


def test_len():
    sheet = spritesheet(**data)
    assert len(sheet) == sheet.frames.count


def test_caching():
    sheet = spritesheet(**data)
    assert sheet.cache == {}
    frame = sheet[17]
    assert list(sheet.cache.keys()) == [17]
    assert sheet.cache[17] == frame


def test_get():
    w = 64
    h = 67
    sheet = spritesheet(**data)
    frame = sheet[16]
    expected = sheet.image.crop((w * 6, h * 1, w * 7, h * 2))
    assert frame == expected


def test_get_string():
    sheet = spritesheet(**data)
    with pytest.raises(TypeError):
        sheet['banana']


def test_get_outofrange():
    sheet = spritesheet(**data)
    with pytest.raises(IndexError):
        sheet[-2]
    with pytest.raises(IndexError):
        sheet[3002]


def test_animate_unknown_seq():
    sheet = spritesheet(**data)
    with pytest.raises(AttributeError):
        list(sheet.animate("unknown"))


def test_animate_finite_seq():
    sheet = spritesheet(**data)
    frames = list(sheet.animate("run-left"))
    assert len(frames) == 10
    for i, frame in enumerate(frames):
        assert isinstance(frame, PIL.Image.Image)
        assert sheet[i] == frame


def test_animate_slow_seq():
    sheet = spritesheet(**data)
    frames = list(sheet.animate("run-slow"))
    assert len(frames) == 20
    for i, frame in enumerate(frames):
        assert isinstance(frame, PIL.Image.Image)
        assert sheet[i // 2] == frame


def test_animate_infinite_seq():
    sheet = spritesheet(**data)
    runner = sheet.animate("run-right")
    frames = []
    for _ in range(50):
        frames.append(next(runner))

    expected = list(range(19, 9, -1)) * 5

    for i, frame_ref in enumerate(expected):
        assert isinstance(frames[i], PIL.Image.Image)
        assert sheet[frame_ref] == frames[i]


def test_animate_subroutine():
    sheet = spritesheet(**data)
    frames = list(sheet.animate("composite"))

    expected = [1, 2, 3, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    assert len(frames) == 26
    for i, frame_ref in enumerate(expected):
        assert isinstance(frames[i], PIL.Image.Image)
        assert sheet[frame_ref] == frames[i]
