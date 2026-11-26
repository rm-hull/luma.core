# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import os
import glob

from typing import Union
from typing import Final

import gpiod
import gpiod.line

from luma.core.error import UnsupportedPlatform


__all__ = ["GPIO", "global_instance"]


class GPIO:
    """
    A compatibility layer provides a subset of used RPi.GPIO
    library interface to the modern standard libgpiod.

    :param path: Path to ``/dev/gpiochipN``, default is ``/dev/gpiochip0``
        or auto-detect on Raspberry Pi 5 (and some others). All old boards
        use ``/dev/gpiochip0``.
    :type bus: str

    :param consumer: Name of consumer of pins (see ``gpioinfo`` output),
        default ``luma``.
    :param consumer: str
    """

    BCM:  Final[int] = 11
    OUT:  Final[int] = 0

    LOW:  Final[int] = 0
    HIGH: Final[int] = 1

    def __init__(
        self,
        path: str = "",
        consumer: str = "luma",
    ) -> None:

        if not path:
            path = self.__find_device()

        self.__path: Final[str] = path
        self.__consumer: Final[str] = consumer
        self.__lines: dict[int, gpiod.LineRequest] = {}

    def __find_device(self) -> str:
        known_drivers = frozenset([
            "raspberrypi,rp1-gpio",
            "raspberrypi,bcm2835-gpio",
            "raspberrypi,bcm2711-gpio",
        ])
        for path in glob.glob("/sys/bus/gpio/devices/gpiochip*"):
            try:
                with open(os.path.join(path, "of_node/compatible")) as file:
                    lines = file.read().split("\0")
                    drivers = set(filter(None, map(str.strip, lines)))
            except FileNotFoundError:
                pass
            if drivers & known_drivers:
                return os.path.join("/dev", os.path.basename(path))
        return "/dev/gpiochip0"

    def setwarnings(self, enabled: bool) -> None:
        _ = enabled  # Nothing to do

    def setmode(self, mode: int) -> None:
        if mode != self.BCM:  # pragma: no cover
            raise NotImplementedError("Non-BCM modes are not supported")

    def setup(
        self,
        channel: int,
        direction: int,
        initial: Union[bool, int] = False,
    ) -> None:

        if direction != self.OUT:  # pragma: no cover
            raise NotImplementedError("Reading from GPIO is not supported")

        if channel in self.__lines:
            lr = self.__lines.pop(channel)
            lr.release()

        try:
            lr = gpiod.request_lines(
                self.__path,
                consumer=self.__consumer,
                config={(channel,): gpiod.LineSettings(
                    output_value=gpiod.line.Value(bool(initial or False)),
                )},
            )
        except FileNotFoundError as e:
            raise UnsupportedPlatform(f"GPIO access not available: {self.__path}"
                                      f": {type(e).__name__}: {str(e)}")
        self.__lines[channel] = lr

    def output(
        self,
        channel: int,
        value: Union[bool, int],
    ) -> None:

        if channel not in self.__lines:
            self.setup(channel, self.OUT)

        lr = self.__lines[channel]
        lr.set_value(channel, gpiod.line.Value(bool(value or False)))

    def cleanup(
        self,
        channel: Union[int, list[int], tuple[int], None] = None,
    ) -> None:

        if channel is None:
            channel = list(self.__lines)
        elif isinstance(channel, int):
            channel = [channel]

        for ch in channel:
            lr = self.__lines.pop(ch)
            try:
                lr.release()
            except Exception:
                pass

    def __del__(self) -> None:
        self.cleanup()


global_instance = GPIO()
