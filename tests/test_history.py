#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Richard Hull and contributors
# See LICENSE.rst for details.


import pytest

from luma.core.render import canvas
from luma.core.device import dummy
from luma.core.virtual import history

import baseline_data


def test_restore_throws_error_when_empty():
    """
    Restore the history of a given histogram.

    Args:
    """
    device = dummy()
    hist = history(device)
    assert len(hist) == 0
    with pytest.raises(IndexError):
        hist.restore()


def test_save_and_restore_reverts_image():
    """
    Save the image todo.

    Args:
    """
    device = dummy()
    hist = history(device)

    with canvas(hist) as draw:
        baseline_data.primitives(hist, draw)

    img1 = device.image
    hist.savepoint()
    assert len(hist) == 1

    with canvas(hist) as draw:
        draw.text((10, 10), text="Hello", fill="white")

    img2 = device.image
    assert img1 != img2
    hist.restore()
    img3 = device.image
    assert img1 == img3
    assert len(hist) == 0


def test_drop_and_restore():
    """
    Re - drop and drop the image.

    Args:
    """
    device = dummy()
    hist = history(device)

    copies = []
    for i in range(10):
        with canvas(hist) as draw:
            draw.text((10, 10), text=f"Hello {i}", fill="white")
        hist.savepoint()
        copies.append(device.image)

    hist.restore()
    assert device.image == copies[9]
    hist.restore(drop=2)
    assert device.image == copies[6]
    hist.restore(drop=4)
    assert device.image == copies[1]
    assert len(hist) == 1
