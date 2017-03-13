# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import warnings


__all__ = ["deprecation"]


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)
