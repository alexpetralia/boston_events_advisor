from run import app
from flask import render_template
from predictions.routes import get_recommendations
from datetime import datetime as dt, timedelta as td
import json
import sqlite3
import random

@app.route("/get_events")
def get_new_events():
	cnxn = sqlite3.connect('events.db')
	c = cnxn.cursor()
	today = dt.now().date()

	c.execute("""
		SELECT * FROM events
		WHERE creation_date BETWEEN ? and ?;
	""", [today, today + td(7)])
	results = c.fetchall()

	data = []
	columns = ['id', 'title', 'cost', 'description', 'link', 'liked', 'creation_date', 'modification_date']
	for result in results:
		t = {}
		for i, column in enumerate(columns):
			t[column] = result[i]
		data.append(t)
	return json.dumps(data)

@app.route("/")
def get_template_main():
	context = json.loads(get_recommendations())

	num_events = 12
	if len(context) > num_events:
		random.shuffle(context)
		context = context[0:num_events]
	elif len(context) <= num_events:
		unseen_events = json.loads(get_new_events())
		random.shuffle(unseen_events)
		context += unseen_events[0:(num_events - len(context))]

	return render_template('main.jinja', events=context)

@app.route("/about")
def get_template_about():

    return render_template('about.jinja')