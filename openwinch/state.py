#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from enum import Enum, unique


@unique
class State(Enum):
    """ State of Winch. """
    UNKNOWN = -999
    BOOTED = -2
    ERROR = -1
    INIT = 0
    IDLE = 1
    START = 2
    RUNNING = 3
    STOP = 4

    @staticmethod
    def checkRun(current) -> bool:
        return (State.RUNNING == current or State.START == current)

    @staticmethod
    def checkStop(current) -> bool:
        return (State.STOP == current or State.IDLE == current)

    @staticmethod
    def checkFault(current) -> bool:
        return (State.ERROR == current)

    @staticmethod
    def checkInit(current) -> bool:
        return (State.INIT == current)

    @staticmethod
    def checkBoot(current) -> bool:
        return (State.UNKNOWN != current)

    @property
    def isRun(self) -> bool:
        return State.checkRun(self)

    @property
    def isStop(self) -> bool:
        return State.checkStop(self)

    @property
    def isFault(self) -> bool:
        return State.checkFault(self)

    @property
    def isInit(self) -> bool:
        return State.checkInit(self)

    @property
    def isBoot(self) -> bool:
        return State.checkBoot(self)
