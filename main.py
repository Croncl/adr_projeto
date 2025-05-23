# -*- coding: utf-8 -*-
from flask import Flask
import secrets

app = Flask(__name__)
from views import *

app.config["SECRET_KEY"] = secrets.token_hex(16)


if __name__ == "__main__":
    app.run(debug=True)
