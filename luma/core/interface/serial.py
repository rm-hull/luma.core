# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Encapsulates sending commands and data over a serial interface, whether that
is I²C, SPI or bit-banging GPIO.
"""

import errno

import luma.core.error
from luma.core import lib


__all__ = ["i2c", "spi", "bitbang", "ftdi_spi", "ftdi_i2c"]


class i2c(object):
    """
    Wrap an `I²C <https://en.wikipedia.org/wiki/I%C2%B2C>`_ (Inter-Integrated
    Circuit) interface to provide :py:func:`data` and :py:func:`command` methods.

    :param bus: A *smbus* implementation, if ``None`` is supplied (default),
        `smbus2 <https://pypi.python.org/pypi/smbus2>`_ is used.
        Typically this is overridden in tests, or if there is a specific
        reason why `pysmbus <https://pypi.python.org/pypi/pysmbus>`_ must be used
        over smbus2.
    :type bus:
    :param port: I²C port number, usually 0 or 1 (default).
    :type port: int
    :param address: I²C address, default: ``0x3C``.
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
            self._managed = bus is None
            self._i2c_msg_write = smbus2.i2c_msg.write if bus is None else None
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

        :param cmd: A spread of commands.
        :type cmd: int
        :raises luma.core.error.DeviceNotFoundError: I2C device could not be found.
        """
        assert(len(cmd) <= 32)

        try:
            self._bus.write_i2c_block_data(self._addr, self._cmd_mode,
                                           list(cmd))
        except (IOError, OSError) as e:
            if e.errno in [errno.EREMOTEIO, errno.EIO]:
                # I/O error
                raise luma.core.error.DeviceNotFoundError(
                    'I2C device not found on address: 0x{0:02X}'.format(self._addr))
            else:  # pragma: no cover
                raise

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes to the I²C address.
        If the bus is in managed mode backed by smbus2, the i2c_rdwr
        method will be used to avoid having to send in chunks.
        For SMBus devices the maximum allowed in one transaction is
        32 bytes, so if data is larger than this, it is sent in chunks.

        :param data: A data sequence.
        :type data: list, bytearray
        """

        # block size is the maximum data payload that will be tolerated.
        # The managed i2c will transfer blocks of upto 4K (using i2c_rdwr)
        # whereas we must use the default 32 byte block size when unmanaged
        if self._managed:
            block_size = 4096
            write = self._write_large_block
        else:
            block_size = 32
            write = self._write_block

        i = 0
        n = len(data)
        while i < n:
            write(list(data[i:i + block_size]))
            i += block_size

    def _write_block(self, data):
        assert len(data) <= 32
        self._bus.write_i2c_block_data(self._addr, self._data_mode, data)

    def _write_large_block(self, data):
        assert len(data) <= 4096
        self._bus.i2c_rdwr(self._i2c_msg_write(self._addr, [self._data_mode] + data))

    def cleanup(self):
        """
        Clean up I²C resources
        """
        if self._managed:
            self._bus.close()


@lib.rpi_gpio
class bitbang(object):
    """
    Wraps an `SPI <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>`_
    (Serial Peripheral Interface) bus to provide :py:func:`data` and
    :py:func:`command` methods. This is a software implementation and is thus
    a lot slower than the default SPI interface. Don't use this class directly
    unless there is a good reason!

    :param gpio: GPIO interface (must be compatible with `RPi.GPIO <https://pypi.python.org/pypi/RPi.GPIO>`_).
        For slaves that don't need reset or D/C functionality, supply a
        :py:class:`noop` implementation instead.
    :param transfer_size: Max bytes to transfer in one go. Some implementations
        only support maximum of 64 or 128 bytes, whereas RPi/py-spidev supports
        4096 (default).
    :type transfer_size: int
    :param SCLK: The GPIO pin to connect the SPI clock to.
    :type SCLK: int
    :param SDA: The GPIO pin to connect the SPI data (MOSI) line to.
    :type SDA: int
    :param CE: The GPIO pin to connect the SPI chip enable (CE) line to.
    :type CE: int
    :param DC: The GPIO pin to connect data/command select (DC) to.
    :type DC: int
    :param RST: The GPIO pin to connect reset (RES / RST) to.
    :type RST: int
    """
    def __init__(self, gpio=None, transfer_size=4096, **kwargs):

        self._transfer_size = transfer_size
        self._managed = gpio is None
        self._gpio = gpio or self.__rpi_gpio__()

        self._SCLK = self._configure(kwargs.get("SCLK"))
        self._SDA = self._configure(kwargs.get("SDA"))
        self._CE = self._configure(kwargs.get("CE"))
        self._DC = self._configure(kwargs.get("DC"))
        self._RST = self._configure(kwargs.get("RST"))
        self._cmd_mode = self._gpio.LOW  # Command mode = Hold low
        self._data_mode = self._gpio.HIGH  # Data mode = Pull high

        if self._RST is not None:
            self._gpio.output(self._RST, self._gpio.LOW)  # Reset device
            self._gpio.output(self._RST, self._gpio.HIGH)  # Keep RESET pulled high

    def _configure(self, pin):
        if pin is not None:
            self._gpio.setup(pin, self._gpio.OUT)
            return pin

    def command(self, *cmd):
        """
        Sends a command or sequence of commands through to the SPI device.

        :param cmd: A spread of commands.
        :type cmd: int
        """
        if self._DC:
            self._gpio.output(self._DC, self._cmd_mode)

        self._write_bytes(list(cmd))

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes through to the SPI device.
        If the data is more than :py:attr:`transfer_size` bytes, it is sent in chunks.

        :param data: A data sequence.
        :type data: list, bytearray
        """
        if self._DC:
            self._gpio.output(self._DC, self._data_mode)

        i = 0
        n = len(data)
        tx_sz = self._transfer_size
        while i < n:
            self._write_bytes(data[i:i + tx_sz])
            i += tx_sz

    def _write_bytes(self, data):
        gpio = self._gpio
        if self._CE:
            gpio.output(self._CE, gpio.LOW)  # Active low

        for byte in data:
            for _ in range(8):
                gpio.output(self._SDA, byte & 0x80)
                gpio.output(self._SCLK, gpio.HIGH)
                byte <<= 1
                gpio.output(self._SCLK, gpio.LOW)

        if self._CE:
            gpio.output(self._CE, gpio.HIGH)

    def cleanup(self):
        """
        Clean up GPIO resources if managed.
        """
        if self._managed:
            self._gpio.cleanup()


@lib.spidev
class spi(bitbang):
    """
    Wraps an `SPI <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>`_
    (Serial Peripheral Interface) bus to provide :py:func:`data` and
    :py:func:`command` methods.

    :param spi: SPI implementation (must be compatible with `spidev <https://pypi.python.org/pypi/spidev/>`_)
    :param gpio: GPIO interface (must be compatible with `RPi.GPIO <https://pypi.python.org/pypi/RPi.GPIO>`_).
        For slaves that don't need reset or D/C functionality, supply a
        :py:class:`noop` implementation instead.
    :param port: SPI port, usually 0 (default) or 1.
    :type port: int
    :param device: SPI device, usually 0 (default) or 1.
    :type device: int
    :param bus_speed_hz: SPI bus speed, defaults to 8MHz.
    :type bus_speed_hz: int
    :param cs_high: Whether SPI chip select is high, defaults to ``False``.
    :type cs_high: bool
    :param transfer_size: Maximum amount of bytes to transfer in one go. Some implementations
        only support a maximum of 64 or 128 bytes, whereas RPi/py-spidev supports
        4096 (default).
    :type transfer_size: int
    :param gpio_DC: The GPIO pin to connect data/command select (DC) to (defaults to 24).
    :type gpio_DC: int
    :param gpio_RST: The GPIO pin to connect reset (RES / RST) to (defaults to 25).
    :type gpio_RST: int
    :raises luma.core.error.DeviceNotFoundError: SPI device could not be found.
    :raises luma.core.error.UnsupportedPlatform: GPIO access not available.
    """
    def __init__(self, spi=None, gpio=None, port=0, device=0,
                 bus_speed_hz=8000000, cs_high=False, transfer_size=4096,
                 gpio_DC=24, gpio_RST=25):
        assert(bus_speed_hz in [mhz * 1000000 for mhz in [0.5, 1, 2, 4, 8, 16, 32]])

        bitbang.__init__(self, gpio, transfer_size, DC=gpio_DC, RST=gpio_RST)

        try:
            self._spi = spi or self.__spidev__()
            self._spi.open(port, device)
            self._spi.cshigh = cs_high
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                raise luma.core.error.DeviceNotFoundError('SPI device not found')
            else:  # pragma: no cover
                raise

        self._spi.max_speed_hz = bus_speed_hz

    def _write_bytes(self, data):
        self._spi.writebytes(data)

    def cleanup(self):
        """
        Clean up SPI & GPIO resources.
        """
        self._spi.close()
        super(spi, self).cleanup()


class noop(object):
    """
    Does nothing, used for pseudo-devices / emulators / anything really.
    """
    def __getattr__(self, attr):
        return self.__noop

    def __setattr__(self, attr, val):  # pragma: no cover
        pass

    def __noop(self, *args, **kwargs):
        pass


def _ftdi_pin(pin):
    return 1 << pin


class __FTDI_WRAPPER_SPI:
    """
    Adapter for FTDI to spidev. Not for direct public consumption
    """
    def __init__(self, controller, spi_port):
        self._controller = controller
        self._spi_port = spi_port

    def open(self, port, device):
        pass

    def writebytes(self, data):
        self._spi_port.write(data)

    def close(self):
        self._controller.terminate()


class __FTDI_WRAPPER_GPIO:
    """
    Adapter for FTDI to RPI.GPIO. Not for direct public consumption
    """
    LOW = 0
    HIGH = OUT = 1

    def __init__(self, gpio):
        self._gpio = gpio
        self._data = 0

    def setup(self, pin, direction):
        pass

    def output(self, pin, value):
        mask = _ftdi_pin(pin)
        self._data &= ~mask
        if value:
            self._data |= mask

        self._gpio.write(self._data)

    def cleanup(self):
        pass


class __FTDI_WRAPPER_I2C:
    """
    Adapter for FTDI to I2C smbus. Not for direct public consumption
    """

    def __init__(self, controller, i2c_port):
        self._controller = controller
        self._i2c_port = i2c_port

    def write_i2c_block_data(self, address, register, data):
        self._i2c_port.write_to(register, data)

    def i2c_rdwr(self, message):
        address, data = message
        register = data[0]
        self.write_i2c_block_data(address, register, data[1:])

    def close(self):
        self._controller.terminate()


def ftdi_spi(device='ftdi://::/1', bus_speed_hz=12000000, gpio_CS=3, gpio_DC=5, gpio_RST=6):
    """
    Bridges an `SPI <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>`_
    (Serial Peripheral Interface) bus over an FTDI USB device to provide :py:func:`data` and
    :py:func:`command` methods.

    :param device: A URI describing the location of the FTDI device. If ``None`` is
        supplied (default), ``ftdi://::/1`` is used. See `pyftdi <https://pypi.python.org/pypi/pyftdi>`_
        for further details of the naming scheme used.
    :type device: string
    :param bus_speed_hz: SPI bus speed, defaults to 12MHz.
    :type bus_speed_hz: int
    :param gpio_CS: The ADx pin to connect chip select (CS) to (defaults to 3).
    :type gpio_CS: int
    :param gpio_DC: The ADx pin to connect data/command select (DC) to (defaults to 5).
    :type gpio_DC: int
    :param gpio_RST: The ADx pin to connect reset (RES / RST) to (defaults to 6).
    :type gpio_RST: int

    .. versionadded:: 1.9.0
    """
    from pyftdi.spi import SpiController

    controller = SpiController(cs_count=1)
    controller.configure(device)

    slave = controller.get_port(cs=gpio_CS - 3, freq=bus_speed_hz, mode=0)
    gpio = controller.get_gpio()

    # RESET and DC configured as outputs
    pins = _ftdi_pin(gpio_RST) | _ftdi_pin(gpio_DC)
    gpio.set_direction(pins, pins & 0xFF)

    serial = spi(
        __FTDI_WRAPPER_SPI(controller, slave),
        __FTDI_WRAPPER_GPIO(gpio),
        gpio_DC=gpio_DC,
        gpio_RST=gpio_RST)
    serial._managed = True
    return serial


def ftdi_i2c(device='ftdi://::/1', address=0x3C):
    """
    Bridges an `I²C <https://en.wikipedia.org/wiki/I%C2%B2C>`_ (Inter-Integrated
    Circuit) interface over an FTDI USB device to provide :py:func:`data` and
    :py:func:`command` methods.

    :param device: A URI describing the location of the FTDI device. If ``None`` is
        supplied (default), ``ftdi://::/1`` is used. See `pyftdi <https://pypi.python.org/pypi/pyftdi>`_
        for further details of the naming scheme used.
    :type device: string
    :param address: I²C address, default: ``0x3C``.
    :type address: int
    :raises luma.core.error.DeviceAddressError: I2C device address is invalid.

    .. versionadded:: 1.9.0
    """
    from pyftdi.i2c import I2cController

    try:
        addr = int(str(address), 0)
    except ValueError:
        raise luma.core.error.DeviceAddressError(
            'I2C device address invalid: {}'.format(address))

    controller = I2cController()
    controller.configure(device)

    port = controller.get_port(addr)

    serial = i2c(bus=__FTDI_WRAPPER_I2C(controller, port))
    serial._managed = True
    serial._i2c_msg_write = lambda address, data: (address, data)
    return serial
