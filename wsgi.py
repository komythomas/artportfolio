# wsgi.py
import os
from portfolio import create_app

app = create_app()

application = app