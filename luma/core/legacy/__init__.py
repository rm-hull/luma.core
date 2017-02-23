# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import time

from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy.font import DEFAULT_FONT


def textsize(text, font=None):
    font = font or DEFAULT_FONT
    src = [c for ascii_code in text for c in font[ord(ascii_code)]]
    return (len(src), 8)


def text(draw, xy, text, fill=None, font=None):
    font = font or DEFAULT_FONT
    x, y = xy
    for ch in text:
        for byte in font[ord(ch)]:
            for j in range(8):
                if byte & 0x01 > 0:
                    draw.point((x, y + j), fill=fill)

                byte >>= 1
            x += 1


def show_message(device, msg, y_offset=0, fill=None, font=None, scroll_delay=0.03):
    font = font or DEFAULT_FONT
    with canvas(device) as draw:
        w, h = textsize(msg, font)

    x = device.width
    virtual = viewport(device, width=w + x + x, height=device.height)

    with canvas(virtual) as draw:
        text(draw, (x, y_offset), msg, font=font, fill=fill)

    i = 0
    while i < w + x:
        virtual.set_position((i, 0))
        i += 1
        time.sleep(scroll_delay)
