from run import app
from flask import render_template, redirect, request, url_for
from predictions.recommender import predict
import os
import json
import sqlite3

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
			WHERE event_id IN (%s)
		""" % (', '.join('?' for i in recommended_events) ), recommended_events)
		results = c.fetchall()
		columns = ['id', 'title', 'cost', 'description', 'link', 'liked', 'creation_date', 'modification_date', 'suggested']
		for result in results:
			t = {}
			for i, column in enumerate(columns):
				t[column] = result[i]
			data.append(t)
	return json.dumps(data)

@app.route("/post_recommendations", methods=['GET', 'POST'])
def post_recommendations():

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
					WHERE
						event_id = ?;
					""", [liked, event_id]
				)
				cnxn.commit()
		else:
			return "PIN invalid!"
	
	return redirect(url_for('get_template_main'))

@app.route("/submit_pin", methods=['GET', 'POST'])
def submit_pin():

	if request.method == 'POST':
		if request.form.get('pin') == os.environ.get('PIN'):
			return redirect(url_for('get_template_main'))
		else:
			return redirect(url_for('get_template_main'))
	else:
		return redirect(url_for('get_template_main'))