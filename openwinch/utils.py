#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.logger import logger
from openwinch.constantes import WINCH_DIAM

import importlib
import math


def loadClass(fullclass) -> object:
    """Return a class instance from a string reference"""
    module_name, class_name = fullclass.rsplit(".", 1)
    instance = None
    try:
        module = importlib.import_module(module_name)
        try:
            class_ = getattr(module, class_name)
            instance = class_()
        except AttributeError:
            logger.error('Class does not exist')
    except ImportError:
        logger.error('Module does not exist')
    return instance

def rotate2distance(rotate) -> float:
    return (WINCH_DIAM * math.pi) * rotate

def distance2rotate(distance) -> int:
    return distance / (WINCH_DIAM * math.pi)
