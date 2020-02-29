#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from luma.core.device import dummy
from luma.core.legacy import text, textsize, show_message
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT

from unittest.mock import Mock, call


def test_textsize():
    """
    The bounding box of the text, as drawn in the specified font, is correctly
    calculated.
    """
    assert textsize("Hello world") == (88, 8)
    assert textsize("Hello world", font=proportional(CP437_FONT)) == (71, 8)


def test_text_space():
    """
    Draw a space character.
    """
    draw = Mock(unsafe=True)
    text(draw, (2, 2), " ", fill="white")
    draw.point.assert_not_called()


def test_text_char():
    """
    Draw a text character.
    """
    draw = Mock(unsafe=True)
    text(draw, (2, 2), "L", font=LCD_FONT, fill="white")
    draw.point.assert_has_calls([
        call((2, 2), fill='white'),
        call((2, 3), fill='white'),
        call((2, 4), fill='white'),
        call((2, 5), fill='white'),
        call((2, 6), fill='white'),
        call((2, 7), fill='white'),
        call((2, 8), fill='white'),
        call((3, 8), fill='white'),
        call((4, 8), fill='white'),
        call((5, 8), fill='white'),
        call((6, 8), fill='white')
    ])


def test_show_message():
    """
    Scroll a message right-to-left across the devices display.
    """
    device = dummy()
    show_message(device, 'text', scroll_delay=0.0)
