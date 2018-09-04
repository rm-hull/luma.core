# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

# declare_namespace(__name__) is required for setup.py to build a package
# that correctly specifies "luma" in both "packages" and "namespace_packages"
# Normally just adding "luma" as a regular package would suffice, but since
# the namespace packages use a period "." they share a parent directory under
# some circumstances and this file will be deleted when any one package is
# uninstalled- breaking any remaining packages that share the "luma" directory.
try:
    from pkg_resources import declare_namespace
    declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
