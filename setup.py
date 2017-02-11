#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
CONTRIB = open(os.path.join(os.path.dirname(__file__), "CONTRIBUTING.rst")).read()
CHANGES = open(os.path.join(os.path.dirname(__file__), "CHANGES.rst")).read()
version = open(os.path.join(os.path.dirname(__file__), "VERSION.txt")).read().strip()

setup(
    name="luma.core",
    version=version,
    author="Richard Hull",
    author_email="richard.hull@destructuring-bind.org",
    description=("A component library to support SBC display drivers"),
    long_description="\n\n".join([README, CONTRIB, CHANGES]),
    license="MIT",
    keywords="raspberry orange banana pi rpi opi sbc oled lcd led display screen spi i2c",
    url="https://github.com/rm-hull/luma.core",
    download_url="https://github.com/rm-hull/luma.core/tarball/" + version,
    namespace_packages=["luma"],
    packages=["luma.core"],
    include_package_data=True,
    package_data={"luma.core.images": ["luma/core/images/led_on.png",
                                       "luma/core/images/led_off.png",
                                       "luma/core/images/7-segment.png"]},
    install_requires=["pillow>=4.0.0", "smbus2", "spidev", "RPi.GPIO"],
    setup_requires=["pytest-runner"],
    tests_require=["mock", "pytest", "pytest-cov", "python-coveralls"],
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: System :: Hardware",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Software Development :: Libraries :: pygame",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ]
)
