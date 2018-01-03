#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.


import pytest

from luma.core.mixin import capabilities


def test_display_not_implemented():
    cap = capabilities()
    with pytest.raises(NotImplementedError):
        cap.display('foo')
