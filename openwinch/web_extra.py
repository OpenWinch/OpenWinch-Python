#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from flask import (Blueprint, render_template)
from openwinch.constantes import SPEED_UNIT
from openwinch.singleton import winch

web_extra = Blueprint('web_extra', __name__)


def render_extra():
    return render_template("extra.html",
                           mode=winch.getMode(),
                           battery=winch.getBattery(),
                           speed_target=winch.getSpeedTarget(),
                           speed_unit=SPEED_UNIT,
                           enable="white")


@web_extra.route("/extra")
def extra():
    return render_extra()


@web_extra.route("/reset")
def reset():
    winch.initialize()
    return render_extra()


@web_extra.route("/left")
def left():
    return render_extra()


@web_extra.route("/right")
def right():
    return render_extra()
