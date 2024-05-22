# -*- coding: utf-8 -*-
# Copyright (c) 2017-2022 Richard Hull and contributors
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
    return ['oled', 'lcd', 'led_matrix', 'emulator', 'core']


def get_library_for_display_type(display_type):
    """
    Get library name for ``display_type``, e.g. ``ssd1306`` should return
    ``oled``.

    .. versionadded:: 1.2.0

    :param display_type: Display type, e.g. ``ssd1306``.
    :type display_type: str
    :rtype: str or None
    """
    display_types = get_display_types()
    for key in display_types.keys():
        if display_type in display_types[key]:
            return key


def get_library_version(module_name):
    """
    Get version number from ``module_name``'s ``__version__`` attribute.

    .. versionadded:: 1.2.0

    :param module_name: The module name, e.g. ``luma.oled``.
    :type module_name: str
    :rtype: str
    """
    try:
        module = importlib.import_module('luma.' + module_name)
        if hasattr(module, '__version__'):
            return module.__version__
        else:
            return None
    except ImportError:
        return None


def get_interface_types():
    """
    Get list of available interface types, e.g. ``['spi', 'i2c']``.

    :rtype: list
    """
    return get_choices('luma.core.interface.serial') + get_choices('luma.core.interface.parallel')


def get_display_types():
    """
    Get ordered dict containing available display types from available luma
    sub-projects.

    :rtype: collections.OrderedDict
    """
    display_types = OrderedDict()
    for namespace in get_supported_libraries():
        display_types[namespace] = get_choices(f'luma.{namespace}.device')

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


class make_interface(object):
    """
    Serial factory.
    """

    def __init__(self, opts, gpio=None):
        self.opts = opts
        self.gpio = gpio

    def noop(self):
        from luma.core.interface.serial import noop
        return noop()

    def i2c(self):
        from luma.core.interface.serial import i2c
        return i2c(port=self.opts.i2c_port, address=self.opts.i2c_address)

    def bitbang(self):
        from luma.core.interface.serial import bitbang
        GPIO = self.__init_alternative_GPIO()
        return bitbang(transfer_size=self.opts.spi_transfer_size,
                       reset_hold_time=self.opts.gpio_reset_hold_time,
                       reset_release_time=self.opts.gpio_reset_release_time,
                       gpio=self.gpio or GPIO)

    def spi(self):
        from luma.core.interface.serial import spi
        GPIO = self.__init_alternative_GPIO()
        return spi(port=self.opts.spi_port,
                   device=self.opts.spi_device,
                   bus_speed_hz=self.opts.spi_bus_speed,
                   transfer_size=self.opts.spi_transfer_size,
                   spi_mode=self.opts.spi_mode,
                   reset_hold_time=self.opts.gpio_reset_hold_time,
                   reset_release_time=self.opts.gpio_reset_release_time,
                   gpio_DC=self.opts.gpio_data_command,
                   gpio_RST=self.opts.gpio_reset,
                   gpio=self.gpio or GPIO)

    def gpio_cs_spi(self):
        from luma.core.interface.serial import gpio_cs_spi
        GPIO = self.__init_alternative_GPIO()
        return gpio_cs_spi(port=self.opts.spi_port,
                           device=self.opts.spi_device,
                           bus_speed_hz=self.opts.spi_bus_speed,
                           cs_high=self.opts.spi_cs_high,
                           transfer_size=self.opts.spi_transfer_size,
                           spi_mode=self.opts.spi_mode,
                           reset_hold_time=self.opts.gpio_reset_hold_time,
                           reset_release_time=self.opts.gpio_reset_release_time,
                           gpio_DC=self.opts.gpio_data_command,
                           gpio_RST=self.opts.gpio_reset,
                           gpio_CS=self.opts.gpio_chip_select,
                           gpio=self.gpio or GPIO)

    def ftdi_spi(self):
        from luma.core.interface.serial import ftdi_spi
        return ftdi_spi(device=self.opts.ftdi_device,
                        bus_speed_hz=self.opts.spi_bus_speed,
                        gpio_DC=self.opts.gpio_data_command,
                        gpio_RST=self.opts.gpio_reset)

    def ftdi_i2c(self):
        from luma.core.interface.serial import ftdi_i2c
        return ftdi_i2c(address=self.opts.i2c_address)

    def pcf8574(self):
        from luma.core.interface.serial import pcf8574
        return pcf8574(port=self.opts.i2c_port, address=self.opts.i2c_address)

    def bitbang_6800(self):
        from luma.core.interface.parallel import bitbang_6800
        GPIO = self.__init_alternative_GPIO()
        return bitbang_6800(gpio=self.gpio or GPIO)

    def __init_alternative_GPIO(self):
        if hasattr(self.opts, 'gpio') and self.opts.gpio is not None:
            GPIO = importlib.import_module(self.opts.gpio)

            if hasattr(self.opts, 'gpio_mode') and self.opts.gpio_mode is not None:
                (packageName, _, attrName) = self.opts.gpio_mode.rpartition('.')
                pkg = importlib.import_module(packageName)
                mode = getattr(pkg, attrName)
                GPIO.setmode(mode)
            else:
                GPIO.setmode(GPIO.BCM)

            atexit.register(GPIO.cleanup)
        else:
            GPIO = None

        return GPIO


def create_device(args, display_types=None):
    """
    Create and return device.

    :type args: object
    :type display_types: dict
    """
    device = None
    if display_types is None:
        display_types = get_display_types()

    if args.display in display_types.get('core', []):
        import luma.core.device
        Device = getattr(luma.core.device, args.display)
        framebuffer = getattr(luma.core.framebuffer, args.framebuffer)(num_segments=args.num_segments, debug=args.debug)
        params = dict(vars(args), framebuffer=framebuffer)
        device = Device(device=args.framebuffer_device, **params)

    elif args.display in display_types.get('oled', []):
        import luma.oled.device
        Device = getattr(luma.oled.device, args.display)
        interface = getattr(make_interface(args), args.interface)
        framebuffer = getattr(luma.core.framebuffer, args.framebuffer)(num_segments=args.num_segments, debug=args.debug)
        params = dict(vars(args), framebuffer=framebuffer)
        device = Device(serial_interface=interface(), **params)

    elif args.display in display_types.get('lcd', []):
        import luma.lcd.device
        Device = getattr(luma.lcd.device, args.display)
        interface = getattr(make_interface(args), args.interface)()
        backlight_params = dict(gpio=interface._gpio, gpio_LIGHT=args.gpio_backlight, active_low=args.backlight_active == "low")
        framebuffer = getattr(luma.core.framebuffer, args.framebuffer)(num_segments=args.num_segments, debug=args.debug)
        params = dict(vars(args), framebuffer=framebuffer, **backlight_params)
        device = Device(serial_interface=interface, **params)
        try:
            import luma.lcd.aux
            luma.lcd.aux.backlight(**backlight_params).enable(True)
        except ImportError:  # pragma: no cover
            pass

    elif args.display in display_types.get('led_matrix', []):
        import luma.led_matrix.device
        from luma.core.interface.serial import noop
        Device = getattr(luma.led_matrix.device, args.display)
        interface = getattr(make_interface(args, gpio=noop()), args.interface)
        device = Device(serial_interface=interface(), **vars(args))

    elif args.display in display_types.get('emulator', []):
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
    display_choices_repr = ', '.join(display_choices)
    interface_types = get_interface_types()
    interface_types_repr = ', '.join(interface_types)
    framebuffer_choices = get_choices('luma.core.framebuffer')
    framebuffer_choices_repr = ', '.join(framebuffer_choices)
    rotation_choices = [0, 1, 2, 3]
    rotation_choices_repr = ', '.join([str(x) for x in rotation_choices])
    block_orientation_choices = [0, 90, -90, 180]
    block_orientation_choices_repr = ', '.join([str(x) for x in block_orientation_choices])
    color_choices = ['1', 'RGB', 'RGBA']
    color_choices_repr = ', '.join(color_choices)

    general_group = parser.add_argument_group('General')
    general_group.add_argument('--config', '-f', type=str, help='Load configuration settings from a file')
    general_group.add_argument('--display', '-d', type=str, default=display_choices[0], help=f'Display type, supports real devices or emulators. Allowed values are: {display_choices_repr}', choices=display_choices, metavar='DISPLAY')
    general_group.add_argument('--width', type=int, default=128, help='Width of the device in pixels')
    general_group.add_argument('--height', type=int, default=64, help='Height of the device in pixels')
    general_group.add_argument('--rotate', '-r', type=int, default=0, help=f'Rotation factor. Allowed values are: {rotation_choices_repr}', choices=rotation_choices, metavar='ROTATION')
    general_group.add_argument('--interface', '-i', type=str, default=interface_types[0], help=f'Interface type. Allowed values are: {interface_types_repr}', choices=interface_types, metavar='INTERFACE')

    i2c_group = parser.add_argument_group('I2C')
    i2c_group.add_argument('--i2c-port', type=int, default=1, help='I2C bus number')
    i2c_group.add_argument('--i2c-address', type=str, default='0x3C', help='I2C display address')

    spi_group = parser.add_argument_group('SPI')
    spi_group.add_argument('--spi-port', type=int, default=0, help='SPI port number')
    spi_group.add_argument('--spi-device', type=int, default=0, help='SPI device')
    spi_group.add_argument('--spi-bus-speed', type=int, default=8000000, help='SPI max bus speed (Hz)')
    spi_group.add_argument('--spi-transfer-size', type=int, default=4096, help='SPI bus max transfer unit (bytes)')
    spi_group.add_argument('--spi-mode', type=int, default=None, help='SPI mode (0-3)')
    spi_group.add_argument('--spi-cs-high', type=bool, default=False, help='SPI chip select is high (gpio_cs_spi driver only)')

    ftdi_group = parser.add_argument_group('FTDI')
    ftdi_group.add_argument('--ftdi-device', type=str, default='ftdi://::/1', help='FTDI device')

    linux_framebuffer_group = parser.add_argument_group('Linux framebuffer')
    linux_framebuffer_group.add_argument('--framebuffer-device', type=str, default='/dev/fd0', help='Linux framebuffer device')

    gpio_group = parser.add_argument_group('GPIO')
    gpio_group.add_argument('--gpio', type=str, default=None, help='Alternative RPi.GPIO compatible implementation (SPI interface only)')
    gpio_group.add_argument('--gpio-mode', type=str, default=None, help='Alternative pin mapping mode (SPI interface only)')
    gpio_group.add_argument('--gpio-data-command', type=int, default=24, help='GPIO pin for D/C RESET (SPI interface only)')
    gpio_group.add_argument('--gpio-chip-select', type=int, default=24, help='GPIO pin for Chip select (GPIO_CS_SPI interface only)')
    gpio_group.add_argument('--gpio-reset', type=int, default=25, help='GPIO pin for RESET (SPI interface only)')
    gpio_group.add_argument('--gpio-backlight', type=int, default=18, help='GPIO pin for backlight (PCD8544, ST7735 devices only)')
    gpio_group.add_argument('--gpio-reset-hold-time', type=float, default=0, help='Duration to hold reset line active on startup (seconds) (SPI interface only)')
    gpio_group.add_argument('--gpio-reset-release-time', type=float, default=0, help='Duration to pause for after reset line was made active on startup (seconds) (SPI interface only)')

    misc_group = parser.add_argument_group('Misc')
    misc_group.add_argument('--block-orientation', type=int, default=0, help=f'Fix 90° phase error (MAX7219 LED matrix only). Allowed values are: {block_orientation_choices_repr}', choices=block_orientation_choices, metavar='ORIENTATION')
    misc_group.add_argument('--mode', type=str, default='RGB', help=f'Colour mode (SSD1322, SSD1325 and emulator only). Allowed values are: {color_choices_repr}', choices=color_choices, metavar='MODE')
    misc_group.add_argument('--framebuffer', type=str, default=framebuffer_choices[0], help=f'Framebuffer implementation (SSD1331, SSD1322, ST7735, ILI9341 displays only). Allowed values are: {framebuffer_choices_repr}', choices=framebuffer_choices, metavar='FRAMEBUFFER')
    misc_group.add_argument('--num-segments', type=int, default=4, help='Sets the number of segments to when using the diff-to-previous framebuffer implementation.')
    misc_group.add_argument('--bgr', dest='bgr', action='store_true', help='Set if LCD pixels laid out in BGR (ST7735 displays only).')
    misc_group.add_argument('--inverse', dest='inverse', action='store_true', help='Set if LCD has swapped black and white (ST7735 displays only).')
    misc_group.set_defaults(bgr=False)
    misc_group.add_argument('--h-offset', type=int, default=0, help='Horizontal offset (in pixels) of screen to display memory (ST7735 displays only).')
    misc_group.add_argument('--v-offset', type=int, default=0, help='Vertical offset (in pixels) of screen to display memory (ST7735 displays only).')
    misc_group.add_argument('--backlight-active', type=str, default='low', help='Set to \"low\" if LCD backlight is active low, else \"high\" otherwise (PCD8544, ST7735 displays only). Allowed values are: low, high', choices=["low", "high"], metavar='VALUE')
    misc_group.add_argument('--debug', dest='debug', action='store_true', help='Set to enable debugging.')

    if len(display_types['emulator']) > 0:
        transformer_choices = get_transformer_choices()
        transformer_choices_repr = ', '.join(transformer_choices)

        emulator_group = parser.add_argument_group('Emulator')
        emulator_group.add_argument('--transform', type=str, default='scale2x', help=f'Scaling transform to apply (emulator only). Allowed values are: {transformer_choices_repr}', choices=transformer_choices, metavar='TRANSFORM')
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
