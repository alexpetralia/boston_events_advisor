from flask import Flask, render_template, redirect, request
from flask_cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp/flask'})

from index.routes import *
from historical.routes import *

if __name__ == "__main__":

	app.run(debug=True)