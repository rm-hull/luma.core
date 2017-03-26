# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import warnings


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)
