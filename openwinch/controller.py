#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>


from openwinch.config import config
from openwinch.constantes import (SPEED_INIT, SPEED_MAX, SPEED_MIN)
from openwinch.display import Gui
from openwinch.keyboard import Keyboard
from openwinch.logger import logger
from openwinch.mode import ModeFactory, ModeType
from openwinch.state import State
from openwinch.utils import loadClass
from openwinch.version import __version__

import atexit
import threading


class Winch(object):
    """ Winch controller class. """

    __board = None
    __controlLoop = None
    __gui = None
    __input = None
    __mode = None

    __state = State.UNKNOWN
    __speed_target = SPEED_INIT

    def __init__(self):
        """ Constructor of Winch class. """

        # Always pass in emergency mode when Application halt/exit !!!
        atexit.register(self.emergency)
        threading.currentThread().setName("Main")

        self.__banner()
        self.__loadConfig()
        self.__initControlLoop()

    # def __del__(self):
    #     """ Destructor of Winch class. """

    #     self.__controlLoop.do_run = False
    #     self.__controlLoop.join()

    def __banner(self):
        logger.info("""
   ____                 _       ___            __
  / __ \____  ___  ____| |     / (_)___  _____/ /_
 / / / / __ \/ _ \/ __ \ | /| / / / __ \/ ___/ __ \\
/ /_/ / /_/ /  __/ / / / |/ |/ / / / / / /__/ / / /
\____/ .___/\___/_/ /_/|__/|__/_/_/ /_/\___/_/ /_/
    /_/                                            Ver. %s""" % __version__) # noqa

    def __loadConfig(self):
        logger.debug("Gui config : %s" % config.GUI)
        self.__gui = Gui(self)
        self.__gui.boot()
        self._input = Keyboard(self, self.__gui)

        logger.debug("Board config : %s" % config.BOARD)
        self.__board = loadClass(config.BOARD, self)
        logger.info("Board : %s" % type(self.__board).__name__)

        logger.debug("Mode config : %s" % config.MODE)
        self.__mode = ModeFactory.modeFactory(self, self.__board, config.MODE)
        logger.info("Mode : %s" % self.getMode())

    def __initControlLoop(self):
        """ Initialize Control Loop thread. """

        logger.debug("Initialize Control Loop...")
        self.__controlLoop = threading.Thread(target=self.__mode.runControlLoop, name="Ctrl", args=(), daemon=True)
        self.__controlLoop.start()
        self.__changeState(State.BOOTED)

    def initialize(self):
        """ Initialise Hardware.

        Step :
        - Initialise Sensor
        - Position at origin
        """

        logger.debug("Initialize Winch hardware...")
        self.__changeState(State.INIT)

    def initialized(self):
        """ Call when hardware stop completely. """

        if (self.__state.isInit):
            self.__changeState(State.IDLE)

    def start(self):
        """ Command Start winch. """

        logger.info("Press Start")

        if (self.__state.isStop):
            self.__changeState(State.START)

        elif (self.__state == State.START):
            logger.warning("Switch mode alway enable !")

        else:
            logger.error("Not possible to start, re-initialize Winch !")

    def started(self):
        """ Call when hardware process start completely. """

        if (self.__state == State.START):
            self.__changeState(State.RUNNING)

    def stop(self):
        """ Command Stop winch """

        logger.info("Press Stop")

        if (self.__state.isRun):
            self.__changeState(State.STOP)

        elif (self.__state == State.STOP):
            logger.warning("Switch mode alway enable !")

        else:
            logger.error("Not possible to stop, re-initialize Winch !")

    def stopped(self):
        """ Call when hardware stop completely. """

        if (self.__state == State.STOP):
            self.__changeState(State.IDLE)

    def emergency(self):
        """ Command Emergency winch. """

        logger.fatal("HALT EMERGENCY")
        self.__changeState(State.ERROR)

    def display(self):
        """ Process display in console. """

        print("State\t: %s\nTarget Speed\t: %s\nCurrent speed\t: %s" % (self.__state,
                                                                        self.__speed_target,
                                                                        self.__mode.getSpeedCurrent()))

    def __changeState(self, state):
        """ Change State of machine-state

        Parameters
        ----------
        mode : State Enum
            Mode to enable.
        """
        if (self.__state != state):
            logger.debug("Switch state : %s", state)
            self.__state = state

    def getMode(self) -> ModeType:
        """ """
        return ModeFactory.getMode(self.__mode)

    def getSpeedTarget(self):
        """ Get Target speed of winch."""
        return self.__speed_target

    def getState(self) -> State:
        """ Get actual state of winch. """
        return self.__state

    def getBattery(self):
        """ Get actual state of Battery. """
        return self.__board.getBattery()

    def getRemote(self):
        return 15

    def getDistance(self):
        return self.__mode.getDistance()

    def speedUp(self, value=1):
        """ Up speed.

        Parameters
        ----------
        value : int, optional
            Value to increment speed (default is 1)
        """
        if (self.__speed_target < SPEED_MAX):
            self.__speed_target += value

    def speedDown(self, value=1):
        """ Down speed.

        Parameters
        ----------
        value : int, optional
            Value to decrement speed (default is 1)
        """
        if (self.__speed_target > SPEED_MIN):
            self.__speed_target -= value

    def speedValue(self, value):
        """ Set speed. """
        if (value >= SPEED_MIN or value < SPEED_MAX):
            self.__speed_target = value
