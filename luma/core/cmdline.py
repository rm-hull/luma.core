# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import atexit
import inspect
import argparse
import importlib
from collections import OrderedDict


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
            return [name for name, _ in inspect.getmembers(module, inspect.isclass)
                    if name != "device"]
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
    return get_choices('luma.core.interface.serial')


def get_display_types():
    """
    Get ordered dict containing available display types from available luma
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
        from luma.core.interface.serial import i2c
        return i2c(port=self.opts.i2c_port, address=self.opts.i2c_address)

    def spi(self):
        from luma.core.interface.serial import spi

        if hasattr(self.opts, 'gpio') and self.opts.gpio is not None:
            GPIO = importlib.import_module(self.opts.gpio)
            GPIO.setmode(GPIO.BCM)
            atexit.register(GPIO.cleanup)
        else:
            GPIO = None

        return spi(port=self.opts.spi_port,
                   device=self.opts.spi_device,
                   bus_speed_hz=self.opts.spi_bus_speed,
                   gpio_DC=self.opts.gpio_data_command,
                   gpio_RST=self.opts.gpio_reset,
                   gpio=self.gpio or GPIO)


def create_device(args, display_types=None):
    """
    Create and return device.

    :type args: object
    :type display_types: dict
    """
    device = None
    if display_types is None:
        display_types = get_display_types()

    if args.display in display_types.get('oled'):
        import luma.oled.device
        Device = getattr(luma.oled.device, args.display)
        Serial = getattr(make_serial(args), args.interface)
        device = Device(Serial(), **vars(args))

    elif args.display in display_types.get('lcd'):
        import luma.lcd.device
        import luma.lcd.aux
        Device = getattr(luma.lcd.device, args.display)
        spi = make_serial(args).spi()
        device = Device(spi, **vars(args))
        luma.lcd.aux.backlight(gpio=spi._gpio, gpio_LIGHT=args.gpio_backlight, active_low=args.backlight_active == "low").enable(True)

    elif args.display in display_types.get('led_matrix'):
        import luma.led_matrix.device
        from luma.core.serial import noop
        Device = getattr(luma.led_matrix.device, args.display)
        spi = make_serial(args, gpio=noop()).spi()
        device = Device(serial_interface=spi, **vars(args))

    elif args.display in display_types.get('emulator'):
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
    framebuffer_choices = get_choices('luma.core.framebuffer')
    rotation_choices = [0, 1, 2, 3]
    block_orientation_choices = [0, 90, -90, 180]
    color_choices = ['1', 'RGB', 'RGBA']

    general_group = parser.add_argument_group('General')
    general_group.add_argument('--config', '-f', type=str, help='Load configuration settings from a file')
    general_group.add_argument('--display', '-d', type=str, default=display_choices[0], help='Display type, supports real devices or emulators. Allowed values are: {0}'.format(', '.join(display_choices)), choices=display_choices, metavar='')
    general_group.add_argument('--width', type=int, default=128, help='Width of the device in pixels')
    general_group.add_argument('--height', type=int, default=64, help='Height of the device in pixels')
    general_group.add_argument('--rotate', '-r', type=int, default=0, help='Rotation factor. Allowed values are: {0}'.format(', '.join([str(x) for x in rotation_choices])), choices=rotation_choices, metavar='')
    general_group.add_argument('--interface', '-i', type=str, default=interface_types[0], help='Serial interface type. Allowed values are: {0}'.format(', '.join(interface_types)), choices=interface_types, metavar='')

    i2c_group = parser.add_argument_group('I2C')
    i2c_group.add_argument('--i2c-port', type=int, default=1, help='I2C bus number')
    i2c_group.add_argument('--i2c-address', type=str, default='0x3C', help='I2C display address')

    spi_group = parser.add_argument_group('SPI')
    spi_group.add_argument('--spi-port', type=int, default=0, help='SPI port number')
    spi_group.add_argument('--spi-device', type=int, default=0, help='SPI device')
    spi_group.add_argument('--spi-bus-speed', type=int, default=8000000, help='SPI max bus speed (Hz)')

    gpio_group = parser.add_argument_group('GPIO')
    gpio_group.add_argument('--gpio', type=str, default=None, help='Alternative RPi.GPIO compatible implementation (SPI devices only)')
    gpio_group.add_argument('--gpio-data-command', type=int, default=24, help='GPIO pin for D/C RESET (SPI devices only)')
    gpio_group.add_argument('--gpio-reset', type=int, default=25, help='GPIO pin for RESET (SPI devices only)')
    gpio_group.add_argument('--gpio-backlight', type=int, default=18, help='GPIO pin for backlight (PCD8544, ST7735 devices only)')

    misc_group = parser.add_argument_group('Misc')
    misc_group.add_argument('--block-orientation', type=int, default=0, help='Fix 90° phase error (MAX7219 LED matrix only). Allowed values are: {0}'.format(', '.join([str(x) for x in block_orientation_choices])), choices=block_orientation_choices, metavar='')
    misc_group.add_argument('--mode', type=str, default='RGB', help='Colour mode (SSD1322, SSD1325 and emulator only). Allowed values are: {0}'.format(', '.join(color_choices)), choices=color_choices, metavar='')
    misc_group.add_argument('--framebuffer', type=str, default=framebuffer_choices[0], help='Framebuffer implementation (SSD1331, SSD1322, ST7735 displays only). Allowed values are: {0}'.format(', '.join(framebuffer_choices)), choices=framebuffer_choices, metavar='')
    misc_group.add_argument('--bgr', dest="bgr", action="store_true", help='Set if LCD pixels laid out in BGR (ST7735 displays only).')
    misc_group.set_defaults(bgr=False)
    misc_group.add_argument('--h-offset', type=int, default=0, help='Horizontal offset (in pixels) of screen to display memory (ST7735 displays only)')
    misc_group.add_argument('--v-offset', type=int, default=0, help='Vertical offset (in pixels) of screen to display memory (ST7735 displays only)')
    misc_group.add_argument('--backlight-active', type=str, default="low", help='Set to \"low\" if LCD backlight is active low, else \"high\" otherwise (PCD8544, ST7735 displays only). Allowed values are: low, high', choices=["low", "high"], metavar='')

    if len(display_types["emulator"]) > 0:
        transformer_choices = get_transformer_choices()

        emulator_group = parser.add_argument_group('Emulator')
        emulator_group.add_argument('--transform', type=str, default='scale2x', help='Scaling transform to apply (emulator only). Allowed values are: {0}'.format(', '.join(transformer_choices)), choices=transformer_choices, metavar='')
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
