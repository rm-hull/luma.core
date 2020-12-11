# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Richard Hull and contributors
# See LICENSE.rst for details.

import os
import atexit
from time import sleep
from itertools import islice
from PIL import Image

from luma.core import mixin
from luma.core.util import bytes_to_nibbles
from luma.core.framebuffer import diff_to_previous
import luma.core.const
from luma.core.interface.serial import i2c, noop

__all__ = ["linux_framebuffer"]


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
        assert 0 <= level <= 255
        self.command(self._const.SETCONTRAST, level)

    def cleanup(self):
        """
        Attempt to switch the device off or put into low power mode (this
        helps prolong the life of the device), clear the screen and close
        resources associated with the underlying serial interface.

        If :py:attr:`persist` is ``True``, the device will not be switched off.

        This is a managed function, which is called when the python processs
        is being shutdown, so shouldn't usually need be called directly in
        application code.
        """
        if not self.persist:
            self.hide()
            self.clear()
        self._serial_interface.cleanup()


class parallel_device(device):
    """
    Wrapper class to manage communications with devices that can operate in
    four or eight bit modes.

    .. note::
        parallel_devices require specific timings which are managed by using
        ``time.sleep`` to cause the process to block for small amounts of time.
        If your application is especially time sensitive, consider running the
        drivers in a separate thread.

    .. versionadded:: 1.16.0
    """

    def __init__(self, const=None, serial_interface=None, exec_time=None, **kwargs):
        super(parallel_device, self).__init__(const, serial_interface)

        self._exec_time = exec_time if exec_time is not None else \
            serial_interface._pulse_time if hasattr(serial_interface, '_pulse_time') \
            else 0
        self._bitmode = serial_interface._bitmode if hasattr(serial_interface, '_bitmode') else 4
        assert self._bitmode in (4, 8), f'Bit mode {self._bitmode} is invalid.  It can only be 4 or 8'

    def command(self, *cmd, exec_time=None, only_low_bits=False):
        """
        Sends a command or sequence of commands through to the serial interface.
        If operating in four bit mode, expands each command from one byte
        values (8 bits) to two nibble values (4 bits each)

        :param cmd: A spread of commands.
        :type cmd: int
        :param exec_time: Amount of time to wait for the command to finish
            execution.  If not provided, the device default will be used instead
        :type exec_time: float
        :param only_low_bits: If ``True``, only the lowest four bits of the command
            will be sent.  This is necessary on some devices during initialization
        :type only_low_bits: bool
        """
        cmd = cmd if (self._bitmode == 8 or only_low_bits) else \
            bytes_to_nibbles(cmd)
        super(parallel_device, self).command(*cmd)
        sleep(exec_time or self._exec_time)

    def data(self, data):
        """
        Sends a sequence of bytes through to the serial interface.
        If operating in four bit mode, expands each byte from a single
        value (8 bits) to two nibble values (4 bits each)

        :param data: a sequence of bytes to send to the display
        :type data: list
        """
        data = data if self._bitmode == 8 else \
            bytes_to_nibbles(data)
        super(parallel_device, self).data(data)


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

        :param image: Image to display.
        :type image: PIL.Image.Image
        """
        assert image.size == self.size

        self.image = self.preprocess(image).copy()


class linux_framebuffer(device):
    """
    Pseudo-device that acts like a physical display, except that it renders
    to a Linux framebuffer device at /dev/fbN (where N=0, 1, ...). This is specifically
    targetted to allow the luma classes to be used on higher-resolution displays that
    leverage kernel-based display drivers.

    .. note:
        Currently only supports 16-bit RGB, 24-bit RGB/BGR and 32-bit RGBA/BGRA color depths.

    :param device: the Linux framebuffer device (e.g. `/dev/fb0`). If no device
        is given, the device is determined from the `FRAMEBUFFER` environmental
        variable instead. See https://www.kernel.org/doc/html/latest/fb/framebuffer.html
        for more details.
    :param framebuffer: Framebuffer rendering strategy, currently instances of
        ``diff_to_previous`` (default, if not specified) or ``full_frame``.
    :param bgr: Set to ``True`` if device pixels are BGR order (rather than RGB). Note:
        this flag is currently supported on 24 and 32-bit color depth devices only.

    .. versionadded:: 2.0.0
    """

    def __init__(self, device=None, framebuffer=None, bgr=False, **kwargs):
        super(linux_framebuffer, self).__init__(serial_interface=noop())
        self.id = self.__get_display_id(device)
        (width, height) = self.__config("virtual_size")
        self.bits_per_pixel = next(self.__config("bits_per_pixel"))

        # Lookup table of (target bit-depth, bgr) -> function, where the
        # function takes an RGB image and converts it into a stream of
        # bytes for the target bit-depth and RGB/BGR orientation.
        image_converters = {
            (16, False): self.__toRGB565,
            (24, False): self.__toRGB,
            (24, True): self.__toBGR,
            (32, False): self.__toRGBA,
            (32, True): self.__toBGRA,
        }
        assert (self.bits_per_pixel, bgr) in image_converters, f"Unsupported bit-depth: {self.bits_per_pixel}"
        self.__image_converter = image_converters[(self.bits_per_pixel, bgr)]

        self.framebuffer = framebuffer or diff_to_previous(num_segments=16)
        self.capabilities(width, height, rotate=0, mode="RGB")

        # This file handle is closed in self.cleanup() (usually invoked
        # automatically via a registered `atexit` hook)
        self.__file_handle = open(f"/dev/fb{self.id}", "wb")

    def __get_display_id(self, device):
        """
        Extract the display-id from the device which is usually referred in
        the form `/dev/fbN` where N is numeric. If no device is given, defer
        to the FRAMEBUFFER environmental variable.

        See https://www.kernel.org/doc/html/latest/fb/framebuffer.html for more details.
        """
        if device is None:
            device = os.environ.get("FRAMEBUFFER", "/dev/fb0")

        if device.startswith("/dev/fb"):
            return int(device[7:])

        raise luma.core.error.DeviceNotFoundError(
            f"Invalid/unsupported framebuffer: {device}"
        )

    def __config(self, section):
        path = f"/sys/class/graphics/fb{self.id}/{section}"
        with open(path, "r") as fp:
            for value in fp.read().strip().split(","):
                if value:
                    yield int(value)

    def __toRGB565(self, image):
        for r, g, b in image.getdata():
            yield g << 3 & 0xE0 | b >> 3
            yield r & 0xF8 | g >> 5

    def __toRGB(self, image):
        return iter(image.tobytes())

    def __toBGR(self, image):
        r, g, b = image.split()
        return iter(Image.merge("RGB", (b, g, r)).tobytes())

    def __toRGBA(self, image):
        return iter(image.convert("RGBA").tobytes())

    def __toBGRA(self, image):
        r, g, b = image.split()
        return iter(Image.merge("RGB", (b, g, r)).convert("RGBA").tobytes())

    def cleanup(self):
        super(linux_framebuffer, self).cleanup()
        self.__file_handle.close()

    def display(self, image):
        """
        Takes a :py:mod:`PIL.Image` and converts it for consumption on the
        given /dev/fbX framebuffer device.

        :param image: Image to display.
        :type image: PIL.Image.Image
        """
        assert image.mode == self.mode
        assert image.size == self.size

        image = self.preprocess(image)
        file_handle = self.__file_handle

        bytes_per_pixel = self.bits_per_pixel // 8
        image_bytes_per_row = self.width * bytes_per_pixel

        for image, bounding_box in self.framebuffer.redraw(image):
            left, top, right, bottom = bounding_box
            segment_bytes_per_row = (right - left) * bytes_per_pixel
            left_offset = left * bytes_per_pixel
            generator = self.__image_converter(image)
            for row_offset in range(left_offset + top * image_bytes_per_row,
                                    left_offset + bottom * image_bytes_per_row,
                                    image_bytes_per_row):
                file_handle.seek(row_offset)
                file_handle.write(bytes(islice(generator, segment_bytes_per_row)))

        file_handle.flush()
