#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from .web_extra import web_extra
from .web_main import web_main

from flask import Flask

app = Flask(__name__)
app.register_blueprint(web_extra)
app.register_blueprint(web_main)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
