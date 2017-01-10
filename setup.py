#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

import luma.core

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
CONTRIB = open(os.path.join(os.path.dirname(__file__), "CONTRIBUTING.rst")).read()
CHANGES = open(os.path.join(os.path.dirname(__file__), "CHANGES.rst")).read()
version = luma.core.__version__

setup(
    name="luma.core",
    version=version,
    author="Richard Hull",
    author_email="richard.hull@destructuring-bind.org",
    description=("A component library small library to support SBC display drivers"
                 "SSD1306, SSD1325, SSD1331 or SH1106 chipset"),
    long_description="\n\n".join([README, CONTRIB, CHANGES]),
    license="MIT",
    keywords="raspberry pi rpi oled display screen ssd1306 ssd1325 ssd1331 sh1106 spi i2c 128x64 128x32 96x16",
    url="https://github.com/rm-hull/luma.core",
    download_url="https://github.com/rm-hull/luma.core/tarball/" + version,
    packages=["luma.core"],
    install_requires=["pillow", "smbus2", "spidev", "RPi.GPIO"],
    setup_requires=["pytest-runner"],
    tests_require=["mock", "pytest", "pytest-cov", "python-coveralls"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: System :: Hardware",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ]
)
