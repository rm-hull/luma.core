# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Encapsulates sending commands and data over a parallel-bus interface.
"""

from time import sleep
from luma.core import lib


__all__ = ["bitbang_6800"]

'''
Default amount of time to wait for a pulse to complete if the device the
interface is connected to requires a pin to be 'pulsed' from low to high to
low for it to accept data or a command
'''
PULSE_TIME = 1e-6 * 50


@lib.rpi_gpio
class bitbang_6800(object):
    """
    Implements a 6800 style parallel-bus interface that provides :py:func:`data`
    and :py:func:`command` methods. The default pin assignments provided are
    from `Adafruit <https://learn.adafruit.com/drive-a-16x2-lcd-directly-with-a-raspberry-pi/wiring>`_.

    :param gpio: GPIO interface (must be compatible with
        `RPi.GPIO <https://pypi.org/project/RPi.GPIO>`__)
    :param pulse_time: length of time in seconds that the enable line should be
        held high during a data or command transfer
    :type pulse_time: float
    :param RS: The GPIO pin register select (RS) line (low for command, high
        for data)
    :type RS: int
    :param E: The GPIO pin to connect the enable (E) line to.
    :type E: int
    :param PINS: The GPIO pins that form the data bus (a list of 4 or 8 pins
        depending upon implementation ordered from LSD to MSD)
    :type PINS: list[int]

    .. versionadded:: 1.16.2
    """

    def __init__(self, gpio=None, pulse_time=PULSE_TIME, **kwargs):
        self._managed = gpio is None
        self._gpio = gpio or self.__rpi_gpio__()
        self._gpio.setwarnings(False)
        self._pulse_time = pulse_time

        self._RS = self._configure(kwargs.get("RS", 22))
        self._E = self._configure(kwargs.get("E", 17))
        self._PINS = self._configure(kwargs.get('PINS', list((25, 24, 23, 18))))

        self._datalines = len(self._PINS)
        assert self._datalines in (4, 8), f'You\'ve provided {len(self._PINS)} pins but a bus must contain either four or eight pins'
        self._bitmode = self._datalines  # Used by device to autoset its own bitmode

        self._cmd_mode = self._gpio.LOW  # Command mode = Hold low
        self._data_mode = self._gpio.HIGH  # Data mode = Pull high

    def _configure(self, pin):
        pins = pin if type(pin) == list else [pin] if pin else []
        for p in pins:
            self._gpio.setup(p, self._gpio.OUT)
        return pin

    def command(self, *cmd):
        """
        Sends a command or sequence of commands through the bus
        If the bus is in four bit mode, only the lowest 4 bits of the data
        value will be sent.

        This means that the device needs to send high and low bits separately
        if the device is operating using a 4 bit bus (e.g. to send a 0x32 in
        4 bit mode the device would use ``command(0x03, 0x02)``).

        :param cmd: A spread of commands.
        :type cmd: int
        """
        self._write(list(cmd), self._cmd_mode)

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes through to the bus.
        If the bus is in four bit mode, only the lowest 4 bits of the data
        value will be sent.

        This means that the device needs to send high and low bits separately
        if the device is operating using a 4 bit bus (e.g. to send a 0x32 in
        4 bit mode the device would use ``data([0x03, 0x02])``).

        :param data: A data sequence.
        :type data: list, bytearray
        """
        self._write(data, self._data_mode)

    def _write(self, data, mode):
        gpio = self._gpio
        gpio.output(self._RS, mode)
        gpio.output(self._E, gpio.LOW)
        for value in data:
            for i in range(self._datalines):
                gpio.output(self._PINS[i], (value >> i) & 0x01)
            gpio.output(self._E, gpio.HIGH)
            sleep(self._pulse_time)
            gpio.output(self._E, gpio.LOW)

    def cleanup(self):
        """
        Clean up GPIO resources if managed.
        """
        if self._managed:
            self._gpio.cleanup()
