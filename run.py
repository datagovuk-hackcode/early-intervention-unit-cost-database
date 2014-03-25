# coding: utf-8
import sys
import cdecimal
sys.modules["decimal"] = cdecimal

from app import app
from api import api

app.register_blueprint(api)

if __name__ == '__main__':
    app.run()
