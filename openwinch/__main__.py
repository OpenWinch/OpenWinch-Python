#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from flask import Flask
from openwinch.web_extra import web_extra
from openwinch.web_main import web_main

app = Flask(__name__)
app.register_blueprint(web_extra)
app.register_blueprint(web_main)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
