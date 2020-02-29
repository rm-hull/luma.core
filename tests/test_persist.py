#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Richard Hull and contributors
# See LICENSE.rst for details.


from unittest.mock import patch

from luma.core.device import dummy


def test_persist():
    dev = dummy()
    assert dev.persist is False
    with patch.object(dev, 'hide') as mock:
        dev.cleanup()
    mock.assert_called_once_with()
    dev = dummy()
    dev.persist = True
    with patch.object(dev, 'hide') as mock:
        dev.cleanup()
    mock.assert_not_called()
