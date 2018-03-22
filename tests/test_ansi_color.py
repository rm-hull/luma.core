#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.ansi_color` module.
"""

import pytest

from luma.core import ansi_color


def test_parse_str_no_escape():
    gen = ansi_color.parse_str("hello world")
    assert next(gen) == ["putch", "h"]
    assert next(gen) == ["putch", "e"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", " "]
    assert next(gen) == ["putch", "w"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", "r"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "d"]

    with pytest.raises(StopIteration):
        next(gen)


def test_parse_str_valid_ansi_colors():
    gen = ansi_color.parse_str("hello \033[31mworld\33[0m")
    assert next(gen) == ["putch", "h"]
    assert next(gen) == ["putch", "e"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", " "]
    assert next(gen) == ["foreground_color", "red"]
    assert next(gen) == ["putch", "w"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", "r"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "d"]
    assert next(gen) == ["reset"]

    with pytest.raises(StopIteration):
        next(gen)


def test_parse_str_valid_ansi_colors_extended_codeset():
    gen = ansi_color.parse_str(u"á \033[31mFußgänger Текст на\033[0m")
    assert next(gen) == ["putch", u"á"]
    assert next(gen) == ["putch", " "]
    assert next(gen) == ["foreground_color", "red"]
    assert next(gen) == ["putch", "F"]
    assert next(gen) == ["putch", "u"]
    assert next(gen) == ["putch", u"ß"]
    assert next(gen) == ["putch", "g"]
    assert next(gen) == ["putch", u"ä"]
    assert next(gen) == ["putch", "n"]
    assert next(gen) == ["putch", "g"]
    assert next(gen) == ["putch", "e"]
    assert next(gen) == ["putch", "r"]
    assert next(gen) == ["putch", " "]
    assert next(gen) == ["putch", u"Т"]
    assert next(gen) == ["putch", u"е"]
    assert next(gen) == ["putch", u"к"]
    assert next(gen) == ["putch", u"с"]
    assert next(gen) == ["putch", u"т"]
    assert next(gen) == ["putch", " "]
    assert next(gen) == ["putch", u"н"]
    assert next(gen) == ["putch", u"а"]
    assert next(gen) == ["reset"]

    with pytest.raises(StopIteration):
        next(gen)


def test_parse_str_multiple_ansi_colors():
    gen = ansi_color.parse_str("hello \033[32;46mworld\33[7;0m")
    assert next(gen) == ["putch", "h"]
    assert next(gen) == ["putch", "e"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", " "]
    assert next(gen) == ["foreground_color", "green"]
    assert next(gen) == ["background_color", "cyan"]
    assert next(gen) == ["putch", "w"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", "r"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "d"]
    assert next(gen) == ["reverse_colors"]
    assert next(gen) == ["reset"]

    with pytest.raises(StopIteration):
        next(gen)


def test_parse_str_unknown_ansi_colors_ignored():
    gen = ansi_color.parse_str("hello \033[27mworld")
    assert next(gen) == ["putch", "h"]
    assert next(gen) == ["putch", "e"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", " "]
    assert next(gen) == ["putch", "w"]
    assert next(gen) == ["putch", "o"]
    assert next(gen) == ["putch", "r"]
    assert next(gen) == ["putch", "l"]
    assert next(gen) == ["putch", "d"]

    with pytest.raises(StopIteration):
        next(gen)


def test_strip_ansi_codes():
    gen = ansi_color.strip_ansi_codes("hello \033[27mworld")
    assert gen == "hello world"
