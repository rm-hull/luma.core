# -*- coding: utf-8 -*-
# Copyright (c) 2019 Richard Hull
# See LICENSE.rst for details.


def ftdi_pin(pin):
    return 1 << pin


class FTDI_WRAPPER_SPI:
    def __init__(self, controller, spi_port):
        self._controller = controller
        self._spi_port = spi_port

    def open(self, port, device):
        pass

    def writebytes(self, data):
        self._spi_port.write(data)

    def close(self):
        self._controller.terminate()


class FTDI_WRAPPER_I2C:
    def __init__(self, controller, i2c_port):
        self._controller = controller
        self._i2c_port = i2c_port

    def write_i2c_block_data(self, address, register, data):
        self._i2c_port.write_to(register, data)

    def close(self):
        self._controller.terminate()


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
