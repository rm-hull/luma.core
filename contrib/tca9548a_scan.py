#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
TCA9548A I2C Bus Scanner

Based on: https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout?view=all
Assumes the multiplexer is on address 0x70
"""

import smbus2

TCA_ADDR = 0x70


def mux_select(bus, tca_port):
    assert(0 <= tca_port <= 7)
    bus.write_byte(TCA_ADDR, 1 << tca_port)


def scan():
    port = 1   # Change to port 0 for orig Raspberry Pi, Orange Pi, etc
    bus = smbus2.SMBus(port)

    print("Scanning I2C devices on TCA984A Multiplexer")

    for tca_port in range(8):
        print("TCA Port {0}".format(tca_port))
        mux_select(bus, tca_port)

        for addr in range(0x03, 0x78):
            if addr == TCA_ADDR:
                continue

            try:
                bus.read_byte(addr)
                print("Found I2C 0x{0:02X}".format(addr))
            except:
                pass

    print("\ndone")
    bus.close()


if __name__ == "__main__":
    scan()
