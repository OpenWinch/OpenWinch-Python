#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.controller import Winch
from openwinch.display_config import LCD_MODE
from openwinch.display import Lcd
from openwinch.logger import logger

from abc import ABC, abstractmethod
from enum import Enum, unique


@unique
class SpeedMode(Enum):
    """ Speed Mode. """
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class Board(ABC):

    _winch = None
    _reverse = False
    _speed_mode = SpeedMode.LOW
    _rotation_from_init = 0

    def __init__(self, winch: Winch):
        self._winch = winch
        if (LCD_MODE != 0):
            self._lcd = Lcd(self._winch)
            self._lcd.boot()

    @abstractmethod
    def initialize(self):
        self._rotation_from_init = 0

    @abstractmethod
    def emergency(self):
        pass

    @abstractmethod
    def setThrottleValue(self, value):
        pass

    @abstractmethod
    def getThrottleValue(self):
        pass

    @abstractmethod
    def setReverse(self, enable):
        self._reverse = enable
        logger.debug("IO : Change Reverse mode to : %s" % self.isReverse())

    def isReverse(self):
        return self._reverse

    @abstractmethod
    def setSpeedMode(self, speed_mode):
        self._speed_mode = speed_mode
        logger.debug("IO : Change Speed mode to %s" % self.getSpeedMode())

    def getSpeedMode(self) -> SpeedMode:
        return self._speed_mode

    def getBattery(self) -> int:
        return 100

    def getRotationFromInit(self):
        return self._rotation_from_init

    def getRotationFromExtend(self):
        return 60


class Emulator(Board):
    __value = 0
    __init = False

    def initialize(self):
        super().initialize()
        self.__init = True
        logger.info("IO : Emulator Initialized !")

    def emergency(self):
        self.__init = False
        logger.info("IO : Emulator Emergency mode !")

    def setThrottleValue(self, value):
        if (self.__value > 0):
            self._rotation_from_init -= 1
        elif (self.__init):
            self._rotation_from_init += 1

        if (self.__value != value):
            self.__value = value
            logger.debug("IO : Throttle to %s" % self.__value)

    def getThrottleValue(self):
        logger.debug("IO : Throttle to %s" % self.__value)

    def setSpeedMode(self, speed_mode):
        super().setSpeedMode(speed_mode)

    def setReverse(self, enable):
        super().setReverse(enable)
