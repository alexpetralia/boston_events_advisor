from run import app
from flask import render_template, redirect, request, url_for
from datetime import datetime as dt, timedelta as td
import json
import os
import sqlite3
import random

@app.route("/get_historical_events")
def get_historical_events():
	
	cnxn = sqlite3.connect('events.db')
	c = cnxn.cursor()
	today = dt.now().date()

	c.execute("""
		SELECT * FROM events
		WHERE creation_date <= ?
		GROUP BY title;
	""", [today + td(1000)])
	results = c.fetchall()

	data = []
	columns = ['id', 'title', 'cost', 'description', 'link', 'liked', 'creation_date', 'modification_date']
	for result in results:
		t = {}
		for i, column in enumerate(columns):
			t[column] = result[i]
		data.append(t)
	return json.dumps(data)

@app.route("/post_homework", methods=['GET', 'POST'])
def post_homework():

	if request.method == 'POST':
		if request.form.get('pin') == os.environ.get('PIN'):
			results = request.values
			for event_id, liked in results.items():
				if not event_id.startswith('event_id'):
					continue
				event_id = int(event_id.split('_')[-1])
				cnxn = sqlite3.connect('events.db')
				c = cnxn.cursor()
				c.execute("""
				UPDATE events
				SET
					liked = ?,
					modification_date = DATE('now')
				WHERE title = (
					SELECT title FROM events WHERE event_id = ?
				);
				""", [liked, event_id])
				cnxn.commit()
			return redirect(url_for('get_template_homework'))
		else:
			return "PIN invalid!"
	else: 
		return redirect(url_for('get_template_homework'))

@app.route("/homework")
def get_template_homework():
	context = json.loads(get_historical_events())
	random.shuffle(context)

	return render_template('homework.jinja', events=context)