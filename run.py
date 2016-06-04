from flask import Flask, render_template, redirect, request

app = Flask(__name__)

from main.routes import *
from historical.routes import *
from predictions.routes import *

if __name__ == "__main__":

	app.run(debug=True)