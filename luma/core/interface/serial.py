# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Encapsulates sending commands and data over a serial interface, whether that
is I²C, SPI or bit-banging GPIO.
"""

import errno
from time import sleep

import luma.core.error
from luma.core import lib


__all__ = ["i2c", "noop", "spi", "gpio_cs_spi", "bitbang", "ftdi_spi", "ftdi_i2c", "pcf8574"]

#: Default amount of time to wait for a pulse to complete if the device the
#: interface is connected to requires a pin to be 'pulsed' from low to high
#: to low for it to accept data or a command.
PULSE_TIME = 1e-6 * 50


class i2c(object):
    """
    Wrap an `I²C <https://en.wikipedia.org/wiki/I%C2%B2C>`_ (Inter-Integrated
    Circuit) interface to provide :py:func:`data` and :py:func:`command` methods.

    :param bus: A *smbus* implementation, if ``None`` is supplied (default),
        `smbus2 <https://pypi.org/project/smbus2>`_ is used.
        Typically this is overridden in tests, or if there is a specific
        reason why `pysmbus <https://pypi.org/project/pysmbus>`_ must be used
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
                f'I2C device address invalid: {address}')

        try:
            self._managed = bus is None
            self._i2c_msg_write = smbus2.i2c_msg.write if bus is None else None
            self._bus = bus or smbus2.SMBus(port)
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                # FileNotFoundError
                raise luma.core.error.DeviceNotFoundError(
                    f'I2C device not found: {e.filename}')
            elif e.errno in [errno.EPERM, errno.EACCES]:
                # PermissionError
                raise luma.core.error.DevicePermissionError(
                    f'I2C device permission denied: {e.filename}')
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
        If the bus is in managed mode backed by smbus2, the ``i2c_rdwr``
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

    :param gpio: GPIO interface (must be compatible with `RPi.GPIO <https://pypi.org/project/RPi.GPIO>`__).
        For slaves that don't need reset or D/C functionality, supply a
        :py:class:`noop` implementation instead.
    :param transfer_size: Max bytes to transfer in one go. Some implementations
        only support maximum of 64 or 128 bytes, whereas RPi/py-spidev supports
        4096 (default).
    :type transfer_size: int
    :param reset_hold_time: The number of seconds to hold reset active. Some devices may require
        a duration of 100ms or more to fully reset the display (default:0)
    :type reset_hold_time: float
    :param reset_release_time: The number of seconds to delay afer reset. Some devices may require
        a duration of 150ms or more after reset was triggered before the device can accept the
        initialization sequence (default:0)
    :type reset_release_time: float
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
    def __init__(self, gpio=None, transfer_size=4096, reset_hold_time=0, reset_release_time=0, **kwargs):

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
            sleep(reset_hold_time)
            self._gpio.output(self._RST, self._gpio.HIGH)  # Keep RESET pulled high
            sleep(reset_release_time)

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

    :param spi: SPI implementation (must be compatible with `spidev <https://pypi.org/project/spidev>`_)
    :param gpio: GPIO interface (must be compatible with `RPi.GPIO <https://pypi.org/project/RPi.GPIO>`__).
        For slaves that don't need reset or D/C functionality, supply a
        :py:class:`noop` implementation instead.
    :param port: SPI port, usually 0 (default) or 1.
    :type port: int
    :param device: SPI device, usually 0 (default) or 1.
    :type device: int
    :param bus_speed_hz: SPI bus speed, defaults to 8MHz.
    :type bus_speed_hz: int
    :param transfer_size: Maximum amount of bytes to transfer in one go. Some implementations
        only support a maximum of 64 or 128 bytes, whereas RPi/py-spidev supports
        4096 (default).
    :type transfer_size: int
    :param gpio_DC: The GPIO pin to connect data/command select (DC) to (defaults to 24).
    :type gpio_DC: int
    :param gpio_RST: The GPIO pin to connect reset (RES / RST) to (defaults to 25).
    :type gpio_RST: int
    :param spi_mode: SPI mode as two bit pattern of clock polarity and phase [CPOL|CPHA], 0-3 (default:None)
    :type spi_mode: int
    :param reset_hold_time: The number of seconds to hold reset active. Some devices may require
        a duration of 100ms or more to fully reset the display (default:0)
    :type reset_hold_time: float
    :param reset_release_time: The number of seconds to delay afer reset. Some devices may require
        a duration of 150ms or more after reset was triggered before the device can accept the
        initialization sequence (default:0)
    :type reset_release_time: float
    :raises luma.core.error.DeviceNotFoundError: SPI device could not be found.
    :raises luma.core.error.UnsupportedPlatform: GPIO access not available.
    """
    def __init__(self, spi=None, gpio=None, port=0, device=0,
                 bus_speed_hz=8000000, transfer_size=4096,
                 gpio_DC=24, gpio_RST=25, spi_mode=None,
                 reset_hold_time=0, reset_release_time=0, **kwargs):
        assert(bus_speed_hz in [mhz * 1000000 for mhz in [0.5, 1, 2, 4, 8, 16, 20, 24, 28, 32, 36, 40, 44, 48, 50, 52]])

        bitbang.__init__(self, gpio, transfer_size, reset_hold_time, reset_release_time, DC=gpio_DC, RST=gpio_RST)

        try:
            self._spi = spi or self.__spidev__()
            self._spi.open(port, device)
            if spi_mode:
                self._spi.mode = spi_mode
            if "cs_high" in kwargs:
                import warnings
                warnings.warn(
                    "SPI cs_high is no longer supported in kernel 5.4.51 and beyond, so setting parameter cs_high is now ignored!",
                    RuntimeWarning
                )
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


class gpio_cs_spi(spi):
    """
    Wraps the `spi` class to allow the Chip Select to be used with any GPIO pin.
    The gpio pin to use is defined during instantiation with the keyword argument `gpio_CS`.

    Behaviour is otherwise the same, refer to the documentation on the `spi` class
    for information on other parameters and raised exceptions.

    :param gpio_CS: The GPIO pin to connect chip select (CS / CE) to (defaults to None).
    :type gpio_CS: int
    """
    def __init__(self, *args, **kwargs):
        gpio_CS = kwargs.pop("gpio_CS", None)
        cs_high = kwargs.pop("cs_high", None)
        super(gpio_cs_spi, self).__init__(*args, **kwargs)

        if gpio_CS:
            self._gpio_CS = gpio_CS
            self._cs_high = cs_high
            self._spi.no_cs = True  # disable spidev's handling of the chip select pin
            self._gpio.setup(self._gpio_CS, self._gpio.OUT, initial=self._gpio.LOW if self._cs_high else self._gpio.HIGH)

    def _write_bytes(self, *args, **kwargs):
        if self._gpio_CS:
            self._gpio.output(self._gpio_CS, self._gpio.HIGH if self._cs_high else self._gpio.LOW)

        super(gpio_cs_spi, self)._write_bytes(*args, **kwargs)

        if self._gpio_CS:
            self._gpio.output(self._gpio_CS, self._gpio.LOW if self._cs_high else self._gpio.HIGH)


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


def ftdi_spi(device='ftdi://::/1', bus_speed_hz=12000000, gpio_CS=3, gpio_DC=5, gpio_RST=6,
        reset_hold_time=0, reset_release_time=0):
    """
    Bridges an `SPI <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>`_
    (Serial Peripheral Interface) bus over an FTDI USB device to provide :py:func:`data` and
    :py:func:`command` methods.

    :param device: A URI describing the location of the FTDI device. If ``None`` is
        supplied (default), ``ftdi://::/1`` is used. See `pyftdi <https://pypi.org/project/pyftdi>`_
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
        :param reset_hold_time: The number of seconds to hold reset active. Some devices may require
        a duration of 100ms or more to fully reset the display (default:0)
    :type reset_hold_time: float
    :param reset_release_time: The number of seconds to delay afer reset. Some devices may require
        a duration of 150ms or more after reset was triggered before the device can accept the
        initialization sequence (default:0)
    :type reset_release_time: float

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
        gpio_RST=gpio_RST,
        reset_hold_time=reset_hold_time,
        reset_release_time=reset_release_time)
    serial._managed = True
    return serial


def ftdi_i2c(device='ftdi://::/1', address=0x3C):
    """
    Bridges an `I²C <https://en.wikipedia.org/wiki/I%C2%B2C>`_ (Inter-Integrated
    Circuit) interface over an FTDI USB device to provide :py:func:`data` and
    :py:func:`command` methods.

    :param device: A URI describing the location of the FTDI device. If ``None`` is
        supplied (default), ``ftdi://::/1`` is used. See `pyftdi <https://pypi.org/project/pyftdi>`_
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
            f'I2C device address invalid: {address}')

    controller = I2cController()
    controller.configure(device)

    port = controller.get_port(addr)

    serial = i2c(bus=__FTDI_WRAPPER_I2C(controller, port))
    serial._managed = True
    serial._i2c_msg_write = lambda address, data: (address, data)
    return serial


class pcf8574(i2c):
    """
    I²C interface to provide :py:func:`data` and :py:func:`command` methods
    for a device using a pcf8574 backpack.

    :param bus: A *smbus* implementation, if ``None`` is supplied (default),
        `smbus2 <https://pypi.org/project/smbus2>`_ is used.
        Typically this is overridden in tests, or if there is a specific
        reason why `pysmbus <https://pypi.org/project/pysmbus>`_ must be used
        over smbus2.
    :type bus:
    :param port: I²C port number, usually 0 or 1 (default).
    :type port: int
    :param address: I²C address, default: ``0x3C``.
    :type address: int
    :param pulse_time: length of time in seconds that the enable line should be
        held high during a data or command transfer (default: 50μs)
    :type pulse_time: float
    :param backlight_enabled: Determines whether to activate the display's backlight
    :type backlight_enabled: bool
    :param RS: where register/select is connected to the backpack (default: 0)
    :type RS: int
    :param E: where enable pin is connected to the backpack (default: 2)
    :type E: int
    :param PINS: The PCF8574 pins that form the data bus in LSD to MSD order
    :type PINS: list[int]
    :param BACKLIGHT: Pin number of the pcf8574 (counting from zero) that the
        backlight is controlled from (default: 3)
    :type BACKLIGHT: int
    :param COMMAND: determines whether RS high sets device to expect a command
        byte or a data byte.  Must be either ``high`` (default) or ``low``
    :type COMMAND: str

    :raises luma.core.error.DeviceAddressError: I2C device address is invalid.
    :raises luma.core.error.DeviceNotFoundError: I2C device could not be found.
    :raises luma.core.error.DevicePermissionError: Permission to access I2C device
        denied.

    .. note::
       1. Only one of ``bus`` OR ``port`` arguments should be supplied;
          if both are, then ``bus`` takes precedence.
       2. If ``bus`` is provided, there is an implicit expectation
          that it has already been opened.
       3. Default wiring:

       * RS - Register Select
       * E - Enable
       * RW - Read/Write (note: unused by this driver)
       * D4-D7 - The upper data pins

       ========= === === === === === === === =========
       Device     RS  RW   E  D4  D5  D6  D7 BACKLIGHT
       Display     4   5   6  11  12  13  14
       Backpack   P0  P1  P2  P4  P5  P6  P7        P3
       ========= === === === === === === === =========

       If your PCF8574 is wired up differently to this you will need to provide
       the correct values for the RS, E, COMMAND, BACKLIGHT parameters.
       RS, E and BACKLIGHT are set to the pin numbers of the backpack pins
       they are connect to from P0-P7.

       COMMAND is set to 'high' if the Register Select (RS) pin needs to be high
       to inform the device that a command byte is being sent or 'low' if RS low
       is used for commands.

       PINS is a list of the pin positions that match where the devices data
       pins have been connected on the backpack (P0-P7).  For many devices this
       will be d4->P4, d5->P5, d6->P6, and d7->P7 ([4, 5, 6, 7]) which is the
       default.

       Example:

       If your data lines D4-D7 are connected to the PCF8574s pins P0-P3 with
       the RS pin connected to P4, the enable pin to P5, the backlight pin
       connected to P7, and the RS value to indicate command is low, your
       initialization would look something like:

       ``pcf8574(port=1, address=0x27, PINS=[0, 1, 2, 3], RS=4, E=5,
       COMMAND='low', BACKLIGHT=7)``

       Explanation:
       PINS are set to ``[0, 1, 2, 3]`` which assigns P0 to D4, P1 to D5, P2 to D6,
       and P3 to D7.  RS is set to 4 to associate with P4. Similarly E is set
       to 5 to associate E with P5.  BACKLIGHT set to 7 connects it to pin P7
       of the backpack.  COMMAND is set to ``low`` so that RS will be set to low
       when a command is sent and high when data is sent.

    .. versionadded:: 1.15.0
    """

    _BACKLIGHT = 3
    _ENABLE = 2
    _RS = 0
    _OFFSET = 4
    _CMD = 'low'

    def __init__(self, pulse_time=PULSE_TIME, backlight_enabled=True, *args, **kwargs):
        super(pcf8574, self).__init__(*args, **kwargs)

        self._pulse_time = pulse_time
        self._bitmode = 4  # PCF8574 can only be used to transfer 4 bits at a time

        self._PINS = kwargs.get('PINS', list((4, 5, 6, 7)))
        self._datalines = len(self._PINS)
        assert self._datalines == 4, f'You\'ve provided {len(self._PINS)} data pins but the PCF8574 only supports four'

        self._rs = self._mask(kwargs.get("RS", self._RS))
        self._cmd = 0xFF if kwargs.get("COMMAND", self._CMD).lower() == 'high' else 0x00
        self._data = 0x00 if self._cmd else 0xFF
        self._cmd_mode = self._rs & self._cmd
        self._data_mode = self._rs & self._data
        self._enable = self._mask(kwargs.get("ENABLE", self._ENABLE))
        self._backlight_enabled = self._mask(kwargs.get("BACKLIGHT", self._BACKLIGHT)) if backlight_enabled else 0x00

    def command(self, *cmd):
        """
        Sends a command or sequence of commands through to the I²C address
        - maximum allowed is 32 bytes in one go.

        :param cmd: A spread of commands in high_bits, low_bits order.
        :type cmd: int
        :raises luma.core.error.DeviceNotFoundError: I2C device could not be found.

        IMPORTANT: the PCF8574 only supports four bit transfers.  It is the
        devices responsibility to break each byte sent into a high bit
        and a low bit transfer.

        Example:
            To set an HD44780s cursor to the beginning of the first line requires
            sending 0b10000000 (0x80).  This is 0b1000 (0x08) at the high side of
            the byte and 0b0000 (0x00) on the low side of the byte.

            For example, to send this using the pcf8574 interface::

              d = pcf8574(bus=1, address=0x27)
              d.command([0x08, 0x00])
        """
        self._write(list(cmd), self._cmd_mode)

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes to the I²C address.

        :param data: A data sequence.
        :type data: list, bytearray

        IMPORTANT: the PCF8574 only supports four bit transfers.  It is the
        devices responsibility to break each byte sent into a high bit
        and a low bit transfer.

        Example:
            To send an ascii 'A' (0x41) to the display you need to send binary
            01000001.  This is 0100 (0x40) at the high side of the byte
            and 0001 (0x01) on the low side of the byte.

            For example, to send this using the pcf8574 interface::

              d = pcf8574(bus=1, address=0x27)
              d.command([0x04, 0x01])
        """
        self._write(data, self._data_mode)

    def _mask(self, pin):
        """
        Return a mask that contains a 1 in the pin position.
        """
        return 1 << pin

    def _compute_pins(self, value):
        """
        Set bits in value according to the assigned pin positions on the PCF8574.
        """
        retv = 0
        for i in range(self._datalines):
            retv |= ((value >> i) & 0x01) << self._PINS[i]
        return retv

    def _write(self, data, mode):
        try:
            for value in data:
                self._bus.write_byte(self._addr, self._backlight_enabled | mode | self._compute_pins(value))
                self._bus.write_byte(self._addr, self._backlight_enabled | mode | self._compute_pins(value) | self._enable)
                sleep(self._pulse_time)
                self._bus.write_byte(self._addr, self._backlight_enabled | mode | self._compute_pins(value))
        except (IOError, OSError) as e:
            if e.errno in [errno.EREMOTEIO, errno.EIO]:
                # I/O error
                raise luma.core.error.DeviceNotFoundError(
                    'I2C device not found on address: 0x{0:02X}'.format(self._addr))
            else:  # pragma: no cover
                raise
