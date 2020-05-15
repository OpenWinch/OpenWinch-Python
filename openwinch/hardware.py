#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.logger import logger

from abc import ABC, abstractmethod
from enum import Enum, unique

@unique
class SpeedMode(Enum):
    """ Speed Mode. """
    LOW     = 0
    MEDIUM  = 1
    HIGH    = 2

class Board(ABC):

    _reverse = False
    _speed_mode = SpeedMode.LOW

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def setThrottleValue(self, value):
        pass

    @abstractmethod
    def getThrottleValue(self):
        pass

    def setReverse(self, enable):
        self._reverse = enable
        logger.debug("IO : Change Reverse mode to : %s" % self.isReverse())

    def isReverse(self):
        return self._reverse

    def setSpeedMode(self, speed_mode):
        self._speed_mode = speed_mode
        logger.debug("IO : Change Speed mode to %s" % self.getSpeedMode())

    def getSpeedMode(self):
        return self._speed_mode


class Emulator(Board):
    __value = 0
    
    def initialize(self):
        logger.info("IO : Emulator Initialized !")

    def setThrottleValue(self, value):
        if (self.__value != value):
            self.__value = value
            logger.debug("IO : Throttle to %s" % self.__value)

    def getThrottleValue(self):
        logger.debug("IO : Throttle to %s" % self.__value)
