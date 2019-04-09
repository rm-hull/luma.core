# -*- coding: utf-8 -*-
# Copyright (c) 2019 Richard Hull
# See LICENSE.rst for details.


def ftdi_pin(pin):
    return 1 << pin


class FTDI_WRAPPER_SPI:
    def __init__(self, spi_port):
        self._spi_port = spi_port

    def open(self, port, device):
        pass

    def writebytes(self, data):
        self._spi_port.write(data)

    def close(self):
        pass


class FTDI_WRAPPER_GPIO:

    LOW = 0
    HIGH = OUT = 1

    def __init__(self, gpio):
        self._gpio = gpio
        self._data = 0

    def setup(self, pin, direction):
        pass

    def output(self, pin, value):
        mask = ftdi_pin(pin)
        self._data &= ~mask
        if value:
            self._data |= mask

        self._gpio.write(self._data)
