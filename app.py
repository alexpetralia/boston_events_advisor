from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime as dt, timedelta as td
from recommender import predict
import sqlite3
import json
import random

app = Flask(__name__)

# GET

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

@app.route("/get_recommendations")
def get_recommendations():
	
	predictions = predict()
	recommended_events = []
	for event_id, __, liked in predictions:
		if int(liked) == 1:
			recommended_events.append(int(event_id))
	
	data = []
	if recommended_events:
		cnxn = sqlite3.connect('events.db')
		c = cnxn.cursor()
		c.execute("""
			SELECT *, 1 FROM events
			WHERE event_id IN %s
		""" % (tuple(recommended_events), ))
		results = c.fetchall()
		columns = ['id', 'title', 'cost', 'description', 'link', 'liked', 'creation_date', 'modification_date', 'suggested']
		for result in results:
			t = {}
			for i, column in enumerate(columns):
				t[column] = result[i]
			data.append(t)
	return json.dumps(data)

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

# POST

@app.route("/post_recommendations", methods=['GET', 'POST'])
def post_recommendations():

	if request.method == 'POST':
		results = request.values
		for event_id, liked in results.items():
			event_id = int(event_id.split('_')[-1])
			cnxn = sqlite3.connect('events.db')
			c = cnxn.cursor()
			c.execute("""
			UPDATE events
			SET
				liked = ?,
				modification_date = DATE('now')
			WHERE
				event_id = ?;
			""", [liked, event_id])
			cnxn.commit()
		return redirect(url_for('get_template_main'))

	else: 
		return redirect(url_for('get_template_main'))

@app.route("/post_homework", methods=['GET', 'POST'])
def post_homework():

	if request.method == 'POST':
		results = request.values
		for event_id, liked in results.items():
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
		return redirect(url_for('get_template_homework'))

# Templates

@app.route("/")
def get_template_main():
	context = json.loads(get_recommendations())

	num_events = 18
	if len(context) > num_events:
		random.shuffle(context)
		context = context[0:num_events]
	elif len(context) <= num_events:
		unseen_events = json.loads(get_new_events())
		random.shuffle(unseen_events)
		context += unseen_events[0:(num_events - len(context))]

	return render_template('main.jinja', events=context)

@app.route("/homework")
def get_template_homework():
	context = json.loads(get_historical_events())
	random.shuffle(context)

	return render_template('homework.jinja', events=context)

@app.route("/about")
def get_template_about():

    return render_template('about.jinja')

if __name__ == "__main__":

	app.run(debug=True)