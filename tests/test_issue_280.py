#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2026 Richard Hull and contributors
# See LICENSE.rst for details.

from unittest.mock import MagicMock
from PIL import Image

from luma.core.device import dummy
from luma.core.virtual import viewport, hotspot


def test_viewport_refresh_optimization():
    device = dummy()
    device.display = MagicMock()
    
    virtual = viewport(device, width=200, height=200)
    
    # 1. Initial refresh with no content/changes should be no-op
    virtual.refresh()
    device.display.assert_not_called()
    
    # 2. display(image) should force refresh
    img = Image.new(virtual.mode, (200, 200))
    virtual.display(img)
    device.display.assert_called_once()
    device.display.reset_mock()
    
    # 3. Subsequent refresh with no changes should be no-op
    virtual.refresh()
    device.display.assert_not_called()
    
    # 4. set_position should force refresh
    virtual.set_position((10, 10))
    device.display.assert_called_once()
    device.display.reset_mock()
    
    # 5. Hotspot update should trigger refresh
    # Default hotspot always returns True for should_redraw
    hs = hotspot(20, 20)
    virtual.add_hotspot(hs, (50, 50))
    
    virtual.refresh()
    device.display.assert_called_once()
    device.display.reset_mock()
    
    # 6. Remove hotspot should trigger refresh on next call
    virtual.remove_hotspot(hs, (50, 50))
    # remove_hotspot itself does not call display/refresh
    device.display.assert_not_called()
    
    # But the next refresh call should verify the removal (dirty state)
    virtual.refresh()
    device.display.assert_called_once()
    device.display.reset_mock()
    
    # 7. Back to steady state
    virtual.refresh()
    device.display.assert_not_called()
