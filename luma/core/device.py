# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import atexit

from luma.core import mixin
import luma.core.const
from luma.core.interface.serial import i2c, noop


class device(mixin.capabilities):
    """
    Base class for display driver classes

    .. note::
        Direct use of the :func:`command` and :func:`data` methods are
        discouraged: Screen updates should be effected through the
        :func:`display` method, or preferably with the
        :class:`luma.core.render.canvas` context manager.
    """
    def __init__(self, const=None, serial_interface=None):
        self._const = const or luma.core.const.common
        self._serial_interface = serial_interface or i2c()

        def shutdown_hook():  # pragma: no cover
            try:
                self.cleanup()
            except:
                pass

        atexit.register(shutdown_hook)

    def command(self, *cmd):
        """
        Sends a command or sequence of commands through to the delegated
        serial interface.
        """
        self._serial_interface.command(*cmd)

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes through to the delegated
        serial interface.
        """
        self._serial_interface.data(data)

    def show(self):
        """
        Sets the display mode ON, waking the device out of a prior
        low-power sleep mode.
        """
        self.command(self._const.DISPLAYON)

    def hide(self):
        """
        Switches the display mode OFF, putting the device in low-power
        sleep mode.
        """
        self.command(self._const.DISPLAYOFF)

    def contrast(self, level):
        """
        Switches the display contrast to the desired level, in the range
        0-255. Note that setting the level to a low (or zero) value will
        not necessarily dim the display to nearly off. In other words,
        this method is **NOT** suitable for fade-in/out animation.

        :param level: Desired contrast level in the range of 0-255.
        :type level: int
        """
        assert(0 <= level <= 255)
        self.command(self._const.SETCONTRAST, level)

    def cleanup(self):
        """
        Attempt to switch the device off or put into low power mode (this
        helps prolong the life of the device), clear the screen and close
        resources associated with the underlying serial interface.

        This is a managed function, which is called when the python processs
        is being shutdown, so shouldn't usually need be called directly in
        application code.
        """
        self.hide()
        self.clear()
        self._serial_interface.cleanup()


class dummy(device):
    """
    Pseudo-device that acts like a physical display, except that it does nothing
    other than retain a copy of the displayed image. It is mostly useful for
    testing. Supports 24-bit color depth.
    """
    def __init__(self, width=128, height=64, rotate=0, mode="RGB", **kwargs):
        super(dummy, self).__init__(serial_interface=noop())
        self.capabilities(width, height, rotate, mode)
        self.image = None

    def display(self, image):
        """
        Takes a :py:mod:`PIL.Image` and makes a copy of it for later
        use/inspection.
        """
        assert(image.size == self.size)

        self.image = self.preprocess(image).copy()
