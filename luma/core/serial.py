# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Encapsulates sending commands and data over a serial interface, whether that
is I²C, SPI or bitbanging GPIO.
"""

import errno

import luma.core.error

from luma.core import lib


__all__ = ["i2c", "spi"]


class i2c(object):
    """
    Wrap an `I²C <https://en.wikipedia.org/wiki/I%C2%B2C>`_ (Inter-Integrated
    Circuit) interface to provide :py:func:`data` and :py:func:`command` methods.

    :param bus: a *smbus* implementation, if `None` is supplied (default),
        `smbus2 <https://pypi.python.org/pypi/smbus2>`_ is used.
        Typically this is overridden in tests, or if there is a specific
        reason why `pysmbus <https://pypi.python.org/pypi/pysmbus>`_ must be used
        over smbus2
    :type bus:
    :param port: I²C port number, usually 0 or 1 (default).
    :type port: int
    :param address: I²C address, default: 0x3C.
    :type address: int
    :raises luma.core.error.DeviceAddressError: I2C device address is invalid.
    :raises luma.core.error.DeviceNotFoundError: I2C device could not be found.
    :raises luma.core.error.DevicePermissionError: Permission to access I2C device
        denied.

    .. note::
       1. Only one of ``bus`` OR ``port`` arguments should be supplied;
          if both are, then ``bus`` takes precedence.
       2. If ``bus`` is provided, there is an implicit expectation
          that it has already been opened.
    """
    def __init__(self, bus=None, port=1, address=0x3C):
        import smbus2
        self._cmd_mode = 0x00
        self._data_mode = 0x40

        try:
            self._addr = int(str(address), 0)
        except ValueError:
            raise luma.core.error.DeviceAddressError(
                'I2C device address invalid: {}'.format(address))

        try:
            self._bus = bus or smbus2.SMBus(port)
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                # FileNotFoundError
                raise luma.core.error.DeviceNotFoundError(
                    'I2C device not found: {}'.format(e.filename))
            elif e.errno in [errno.EPERM, errno.EACCES]:
                # PermissionError
                raise luma.core.error.DevicePermissionError(
                    'I2C device permission denied: {}'.format(e.filename))
            else:  # pragma: no cover
                raise

    def command(self, *cmd):
        """
        Sends a command or sequence of commands through to the I²C address
        - maximum allowed is 32 bytes in one go.

        :param cmd: a spread of commands
        :type cmd: int
        :raises luma.core.error.DeviceNotFoundError: I2C device could not be found.
        """
        assert(len(cmd) <= 32)

        try:
            self._bus.write_i2c_block_data(self._addr, self._cmd_mode,
                                           list(cmd))
        except OSError as e:
            if e.errno in [errno.EREMOTEIO, errno.EIO]:
                # I/O error
                raise luma.core.error.DeviceNotFoundError(
                    'I2C device not found on address: {}'.format(self._addr))
            else:  # pragma: no cover
                raise

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes through to the I²C
        address - maximum allowed in one transaction is 32 bytes, so if
        data is larger than this, it is sent in chunks.

        :param data: a data sequence
        :type data: list, bytearray
        """
        i = 0
        n = len(data)
        write = self._bus.write_i2c_block_data
        while i < n:
            write(self._addr, self._data_mode, list(data[i:i + 32]))
            i += 32

    def cleanup(self):
        """
        Clean up I²C resources
        """
        self._bus.close()


@lib.spidev
@lib.rpi_gpio
class spi(object):
    """
    Wraps an `SPI <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>`_
    (Serial Peripheral Interface) bus to provide :py:func:`data` and
    :py:func:`command` methods.

    :param spi: SPI implementation (must be compatible with `spidev <https://pypi.python.org/pypi/spidev/>`_)
    :param gpio: GPIO interface (must be compatible with `RPi.GPIO <https://pypi.python.org/pypi/RPi.GPIO>`_).
        For slaves that dont need reset or D/C functionality, supply a :py:class:`noop`
        implementation instead.
    :param port: SPI port, usually 0 (default) or 1.
    :type port: int
    :param device: SPI device, usually 0 (default) or 1.
    :type device: int
    :param bus_speed_hz: SPI bus speed, defaults to 8MHz
    :type device: int
    :param transfer_size: Max bytes to transfer in one go. Some implementations
        only support maxium of 64 or 128 bytes, whereas RPi/py-spidev supports
        4096 (default).
    :type transfer_size: int
    :param bcm_DC: The BCM pin to connect data/command select (DC) to (defaults to 24).
    :type bcm_DC: int
    :param bcm_RST: The BCM pin to connect reset (RES / RST) to (defaults to 24).
    :type bcm_RST: int
    :raises luma.core.error.DeviceNotFoundError: SPI device could not be found.
    :raises luma.core.error.UnsupportedPlatform: GPIO access not available.
    """
    def __init__(self, spi=None, gpio=None, port=0, device=0,
                 bus_speed_hz=8000000, transfer_size=4096,
                 bcm_DC=24, bcm_RST=25):
        assert(bus_speed_hz in [mhz * 1000000 for mhz in [0.5, 1, 2, 4, 8, 16, 32]])
        self._gpio = gpio or self.__rpi_gpio__()
        self._spi = spi or self.__spidev__()

        try:
            self._spi.open(port, device)
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                raise luma.core.error.DeviceNotFoundError('SPI device not found')
            else:  # pragma: no cover
                raise

        self._transfer_size = transfer_size
        self._spi.max_speed_hz = bus_speed_hz
        self._bcm_DC = bcm_DC
        self._bcm_RST = bcm_RST
        self._cmd_mode = self._gpio.LOW    # Command mode = Hold low
        self._data_mode = self._gpio.HIGH  # Data mode = Pull high

        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self._bcm_DC, self._gpio.OUT)
        self._gpio.setup(self._bcm_RST, self._gpio.OUT)
        self._gpio.output(self._bcm_RST, self._gpio.LOW)   # Reset device
        self._gpio.output(self._bcm_RST, self._gpio.HIGH)  # Keep RESET pulled high

    def command(self, *cmd):
        """
        Sends a command or sequence of commands through to the SPI device.

        :param cmd: a spread of commands
        :type cmd: int
        """
        self._gpio.output(self._bcm_DC, self._cmd_mode)
        self._spi.writebytes(list(cmd))

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes through to the SPI device.
        If the data is more than 4Kb in size, it is sent in chunks.

        :param data: a data sequence
        :type data: list, bytearray
        """
        self._gpio.output(self._bcm_DC, self._data_mode)
        i = 0
        n = len(data)
        tx_sz = self._transfer_size
        write = self._spi.writebytes
        while i < n:
            write(data[i:i + tx_sz])
            i += tx_sz

    def cleanup(self):
        """
        Clean up SPI & GPIO resources
        """
        self._spi.close()
        self._gpio.cleanup()


class noop(object):
    """
    Does nothing, used for pseudo-devices / emulators / anything really
    """
    def __getattr__(self, attr):
        return self.__noop

    def __setattr__(self, attr, val):
        pass

    def __noop(*args, **kwargs):
        pass
