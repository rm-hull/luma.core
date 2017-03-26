# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import time
import warnings

try:
    # only available since python 3.3
    monotonic = time.monotonic
except AttributeError:
    from monotonic import monotonic



def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


