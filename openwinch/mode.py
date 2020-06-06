#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.logger import logger
from openwinch.constantes import (MOTOR_MAX, LOOP_DELAY)
from openwinch.utils import rotate2distance

from enum import Enum, unique
from abc import ABC, abstractmethod

import threading
import time


@unique
class ModeType(Enum):
    """ Mode of Winch. """
    OneWay = 1
    TwoWay = 2
    Infinity = 3

    def list() -> dict:
        return list(ModeType)


class ModeEngine(ABC):

    __security_begin = 20
    __speed_ratio = 1
    __velocity_start = 1
    __velocity_stop = 3

    _board = None
    _winch = None
    _speed_current = 0

    def __init__(self, winch, board):
        self._winch = winch
        self._board = board
        self.__speed_ratio = 1 / MOTOR_MAX

    def __initialize(self):
        logger.debug("Initialize mode.")
        self._speed_current = 0
        self._board.initialize()
        self._winch.initialized()

    def __starting(self):
        # Increment speed
        if (self._speed_current < self._winch.getSpeedTarget()):
            self._speed_current += self.__velocity_start

            if (self._speed_current >= self._winch.getSpeedTarget()):
                self._winch.started()

        # Decrement speed
        if (self._speed_current > self._winch.getSpeedTarget()):
            vel_stop = self.__velocity_stop
            diff_stop = self._speed_current - self._winch.getSpeedTarget()

            if (vel_stop > diff_stop):
                vel_stop = diff_stop

            if (self._speed_current > vel_stop):
                self._speed_current -= vel_stop
            else:
                self._speed_current = 0

    def __stopping(self):
        if (self._speed_current > 0):
            vel_stop = self.__velocity_stop
            diff_stop = self._speed_current - 0

            if (vel_stop > diff_stop):
                vel_stop = diff_stop

            if (self._speed_current > vel_stop):
                self._speed_current -= vel_stop
            else:
                self._speed_current = 0
                self._winch.stopped()

        elif (self._speed_current < 0):
            self._speed_current = 0
            self._winch.stopped()

    def __fault(self):
        self._board.emergency()
        self._speed_current = 0

    @abstractmethod
    def _extraMode(self):
        pass

    def _isBeginSecurity(self) -> bool:
        return (self._board.getRotationFromBegin() - self.__security_begin <= 0)

    def applyThrottleValue(self):
        logger.debug("Calculate & apply throttle value.")
        value = self.__speed_ratio * self._speed_current
        self._board.setThrottleValue(value)

    # Move to Board or Winch
    def getDistance(self) -> float:
        logger.debug("Calculate distance.")
        return rotate2distance(self._board.getRotationFromBegin())

    def getSpeedCurrent(self) -> int:
        return self._speed_current

    def runControlLoop(self):
        """ Main Loop to control hardware. """

        t = threading.currentThread()
        logger.debug("Starting Control Loop.")

        while getattr(t, "do_run", True):
            logger.debug("Current state : %s - speed : %s - limit : %s" % (self._winch.getState(),
                                                                           self._speed_current,
                                                                           self._board.getRotationFromBegin()))

            # INIT
            if (self._winch.getState().isInit):
                self.__initialize()

            # STARTING or RUNNING
            if (self._winch.getState().isRun):
                self.__starting()

            # STOP
            if (self._winch.getState().isStop):
                self.__stopping()

            # Specifical mode
            self._extraMode()

            # EMERGENCY
            if (self._winch.getState().isFault):
                self.__fault()

            self.applyThrottleValue()

            # CPU idle
            time.sleep(LOOP_DELAY)

        logger.debug("Stopping Control Loop.")


class OneWayMode(ModeEngine):

    def _extraMode(self):
        if (self._winch.getState().isRun and self._isBeginSecurity()):  # Limit position START
            self._winch.stop()


class TwoWayMode(ModeEngine):

    __security_end = 20
    __standby_duration = 5
    __current_duration = 0

    def _isEndSecurity(self) -> bool:
        return (self._board.getRotationFromInit() >= self._board.getRotationFromExtend() - self.__security_end)

    def _extraMode(self):
        if (self._winch.getState().isRun and self._isBeginSecurity()):  # Limit Position BEGIN
            self._board.setReverse(True)
            self.__current_duration = self.__standby_duration

        if (self._winch.getState().isRun and self._isEndSecurity()):  # Limit Position END
            self._board.setReverse(False)
            self.__current_duration = self.__standby_duration

        if (self.__current_duration >= 0):
            self.__current_duration -= 1
            self._speed_current = 0


class InfinityMode(ModeEngine):

    def _extraMode(self):
        pass


class ModeFactory(ABC):
    """Factory to manipulate Mode"""

    @staticmethod
    def modeFactory(winch, board, mode) -> ModeEngine:
        """ """
        if (mode == str(ModeType.OneWay)):
            return OneWayMode(winch, board)
        elif (mode == str(ModeType.TwoWay)):
            return TwoWayMode(winch, board)
        elif (mode == str(ModeType.Infinity)):
            return InfinityMode(winch, board)
        else:
            raise NameError('Bad Mode config')

    @staticmethod
    def getMode(modeEngine: ModeEngine) -> ModeType:
        """ """
        if (isinstance(modeEngine, OneWayMode)):
            return ModeType.OneWay
        elif (isinstance(modeEngine, TwoWayMode)):
            return ModeType.TwoWay
        elif (isinstance(modeEngine, InfinityMode)):
            return ModeType.Infinity
