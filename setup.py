#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
from io import open
from setuptools import setup, find_packages


def read_file(*parts):
    with open(os.path.join(os.path.dirname(__file__), *parts), encoding='utf-8') as r:
        return r.read()


def find_version(*file_paths):
    version_file = read_file(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


README = read_file("README.rst")
CONTRIB = read_file("CONTRIBUTING.rst")
CHANGES = read_file("CHANGES.rst")
version = find_version("luma", "core", "__init__.py")

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []
test_deps = [
    'mock;python_version<"3.3"',
    "pytest==4.5",
    "pytest-cov"
]

install_deps = [
    'pillow>=4.0.0',
    'smbus2',
    'pyftdi;python_version>="3.5"'
]

setup(
    name="luma.core",
    version=version,
    author="Richard Hull",
    author_email="richard.hull@destructuring-bind.org",
    description=("A component library to support SBC display drivers"),
    long_description="\n\n".join([README, CONTRIB, CHANGES]),
    license="MIT",
    keywords="raspberry orange banana pi rpi opi sbc oled lcd led display screen spi i2c ftdi usb",
    url="https://github.com/rm-hull/luma.core",
    download_url="https://github.com/rm-hull/luma.core/tarball/" + version,
    packages=find_packages(),
    namespace_packages=["luma"],
    install_requires=install_deps,
    setup_requires=pytest_runner,
    tests_require=test_deps,
    extras_require={
        ':platform_system=="Linux"': [
            'spidev', 'RPI.GPIO'
        ],
        ':python_version<"3.3"': [
            'monotonic'
        ],
        'docs': [
            'sphinx>=1.5.1'
        ],
        'test': test_deps,
        'qa': [
            'flake8',
            'rstcheck'
        ]
    },
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: System :: Hardware",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
