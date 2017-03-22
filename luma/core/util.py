# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import time
import inspect
import warnings
import argparse
import importlib
from collections import OrderedDict

try:
    # only available since python 3.3
    monotonic = time.monotonic
except AttributeError:
    from monotonic import monotonic


__all__ = ["deprecation", "monotonic", "get_choices", "get_supported_libraries",
    "get_interface_types", "get_display_types", "get_transformer_choices",
    "load_config", "make_serial", "create_device", "create_parser"]


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


def get_choices(module_name):
    """
    Retrieve members from ``module_name``'s ``__all__`` list.

    :rtype: list
    """
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, '__all__'):
            return module.__all__
        else:
            return [name for name, _ in inspect.getmembers(module,
                                                           inspect.isclass)]
    except ImportError:
        return []


def get_supported_libraries():
    """
    Get list of supported libraries for the parser.

    :rtype: list
    """
    return ['oled', 'lcd', 'led_matrix', 'emulator']


def get_interface_types():
    """
    Get list of available interface types, e.g. ``['spi', 'i2c']``.

    :rtype: list
    """
    return get_choices('luma.core.serial')


def get_display_types():
    """
    Get ordered dict containg available display types from available luma
    sub-projects.

    :rtype: OrderedDict
    """
    display_types = OrderedDict()
    for namespace in get_supported_libraries():
        display_types[namespace] = get_choices('luma.{0}.device'.format(
            namespace))

    return display_types


def get_transformer_choices():
    """
    :rtype: list
    """
    from luma.emulator.render import transformer
    return [fn for fn in dir(transformer) if fn[0:2] != "__"]


def load_config(path):
    """
    Load device configuration from file path and return list with parsed lines.

    :param path: Location of configuration file.
    :type path: str
    :rtype: list
    """
    args = []
    with open(path, 'r') as fp:
        for line in fp.readlines():
            if line.strip() and not line.startswith("#"):
                args.append(line.replace("\n", ""))

    return args


class make_serial(object):
    """
    Serial factory.
    """
    def __init__(self, opts, gpio=None):
        self.opts = opts
        self.gpio = gpio

    def i2c(self):
        from luma.core.serial import i2c
        return i2c(port=self.opts.i2c_port, address=self.opts.i2c_address)

    def spi(self):
        from luma.core.serial import spi
        return spi(port=self.opts.spi_port,
                   device=self.opts.spi_device,
                   bus_speed_hz=self.opts.spi_bus_speed,
                   gpio_DC=self.opts.gpio_data_command,
                   gpio_RST=self.opts.gpio_reset,
                   gpio=self.gpio)


def create_device(args, dtypes=None):
    """
    Create and return device.
    """
    device = None
    if dtypes is None:
        dtypes = get_display_types()

    if args.display in dtypes.get('oled'):
        import luma.oled.device
        Device = getattr(luma.oled.device, args.display)
        Serial = getattr(make_serial(args), args.interface)
        device = Device(Serial(), **vars(args))

    elif args.display in dtypes.get('lcd'):
        import luma.lcd.device
        import luma.lcd.aux
        Device = getattr(luma.lcd.device, args.display)
        Serial = getattr(make_serial(args), args.interface)
        luma.lcd.aux.backlight(gpio_LIGHT=args.gpio_backlight).enable(True)
        device = Device(Serial(), **vars(args))

    elif args.display in dtypes.get('led_matrix'):
        import luma.led_matrix.device
        from luma.core.serial import noop
        Device = getattr(luma.led_matrix.device, args.display)
        Serial = make_serial(args, gpio=noop()).spi
        device = Device(serial_interface=Serial(), **vars(args))

    elif args.display in dtypes.get('emulator'):
        import luma.emulator.device
        Device = getattr(luma.emulator.device, args.display)
        device = Device(**vars(args))

    return device


def create_parser(description):
    """
    Create and return command-line argument parser.
    """
    parser = argparse.ArgumentParser(description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    display_types = get_display_types()
    display_choices = [display for k, v in display_types.items() for display in v]
    interface_types = get_interface_types()
    framebuffer_choices = get_choices("luma.core.framebuffer")

    general_group = parser.add_argument_group('General')
    general_group.add_argument('--config', '-f', type=str, help='Load configuration settings from a file')
    general_group.add_argument('--display', '-d', type=str, default=display_choices[0], help='Display type, supports real devices or emulators', choices=display_choices)
    general_group.add_argument('--width', type=int, default=128, help='Width of the device in pixels')
    general_group.add_argument('--height', type=int, default=64, help='Height of the device in pixels')
    general_group.add_argument('--rotate', '-r', type=int, default=0, help='Rotation factor', choices=[0, 1, 2, 3])
    general_group.add_argument('--interface', '-i', type=str, default=interface_types[0], help='Serial interface type', choices=interface_types)

    i2c_group = parser.add_argument_group('I2C')
    i2c_group.add_argument('--i2c-port', type=int, default=1, help='I2C bus number')
    i2c_group.add_argument('--i2c-address', type=str, default='0x3C', help='I2C display address')

    spi_group = parser.add_argument_group('SPI')
    spi_group.add_argument('--spi-port', type=int, default=0, help='SPI port number')
    spi_group.add_argument('--spi-device', type=int, default=0, help='SPI device')
    spi_group.add_argument('--spi-bus-speed', type=int, default=8000000, help='SPI max bus speed (Hz)')

    gpio_group = parser.add_argument_group('GPIO')
    gpio_group.add_argument('--gpio-data-command', type=int, default=24, help='GPIO pin for D/C RESET (SPI devices only)')
    gpio_group.add_argument('--gpio-reset', type=int, default=25, help='GPIO pin for RESET (SPI devices only)')
    gpio_group.add_argument('--gpio-backlight', type=int, default=18, help='GPIO pin for backlight (PCD8544 devices only)')

    misc_group = parser.add_argument_group('Misc')
    misc_group.add_argument('--block-orientation', type=str, default='horizontal', help='Fix 90° phase error (MAX7219 LED matrix only)', choices=['horizontal', 'vertical'])
    misc_group.add_argument('--mode', type=str, default='RGB', help='Colour mode (SSD1322, SSD1325 and emulator only)', choices=['1', 'RGB', 'RGBA'])
    misc_group.add_argument('--framebuffer', type=str, default=framebuffer_choices[0], help='Framebuffer implementation (SSD1331, SSD1322, ST7735 displays only)', choices=framebuffer_choices)
    misc_group.add_argument('--bgr', type=bool, default=False, help='Set to True if LCD pixels laid out in BGR (ST7735 displays only)', choices=[True, False])

    if len(display_types["emulator"]) > 0:
        transformer_choices = get_transformer_choices()

        emulator_group = parser.add_argument_group('Emulator')
        emulator_group.add_argument('--transform', type=str, default='scale2x', help='Scaling transform to apply (emulator only)', choices=transformer_choices)
        emulator_group.add_argument('--scale', type=int, default=2, help='Scaling factor to apply (emulator only)')
        emulator_group.add_argument('--duration', type=float, default=0.01, help='Animation frame duration (gifanim emulator only)')
        emulator_group.add_argument('--loop', type=int, default=0, help='Repeat loop, zero=forever (gifanim emulator only)')
        emulator_group.add_argument('--max-frames', type=int, help='Maximum frames to record (gifanim emulator only)')

    try:  # pragma: no cover
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    return parser
