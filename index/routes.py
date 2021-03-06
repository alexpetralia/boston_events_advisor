from app import app, cache
from flask import render_template, request, redirect, url_for
from datetime import datetime as dt, timedelta as td
from overhead.functions import sql_execute
from index.recommender import predict
import json
import sqlite3
import random
import os

#####################
# GET JSON CONTEXTS #
#####################

@app.route("/get_events")
def get_new_events():
	today = dt.now().date()

	results = sql_execute("""
		SELECT * FROM events
		WHERE creation_date BETWEEN ? and ?;
	""", [today, today + td(7)] )

	data = []
	columns = ['id', 'title', 'cost', 'description', 'link', 'liked', 'creation_date', 'modification_date']
	for result in results:
		t = {}
		for i, column in enumerate(columns):
			t[column] = result[i]
		data.append(t)
	return json.dumps(data)

@app.route("/get_recommendations")
@cache.cached(timeout=3600)
def get_recommendations():
	predictions, score = predict()
	recommended_events = []
	for event_id, __, liked in predictions:
		if int(liked) == 1:
			recommended_events.append(int(event_id))
	
	data = []
	if recommended_events:
		results = sql_execute("""
			SELECT *, 1
			FROM events
			WHERE event_id IN (%s)
		""" % (', '.join('?' for i in recommended_events) ), recommended_events)
		columns = ['id', 'title', 'cost', 'description', 'link', 'liked', 'creation_date', 'modification_date', 'latitude', 'longitude', 'categories', 'suggested']
		for result in results:
			t = {}
			for i, column in enumerate(columns):
				t[column] = result[i]
			data.append(t)

	data.append(score)
	return json.dumps(data)


#########
# VERBS #
#########

@app.route("/")
def get_template_main():
	context = json.loads(get_recommendations())
	score = "%0.2f" % (context.pop() * 100)

	num_events = 24
	if len(context) > num_events:
		random.shuffle(context)
		context = context[0:num_events]
	elif len(context) <= num_events:
		unseen_events = json.loads(get_new_events())
		random.shuffle(unseen_events)
		recommended_titles = [x['title'] for x in context]
		c = 0
		while len(context) < num_events:
			if unseen_events[c]['title'] not in recommended_titles:
				context += [unseen_events[c]]
			c += 1

	random.shuffle(context)

	return render_template('main.jinja', events=context, score=score)

@app.route("/post_upcoming", methods=['GET', 'POST'])
def post_upcoming():
	if request.method == 'POST':
		if request.form.get('pin') == os.environ.get('PIN'):
			results = request.values
			for event_id, liked in results.items():
				if not event_id.startswith('event_id'):
					continue
				event_id = int(event_id.split('_')[-1])
				sql_execute("""
					UPDATE events
					SET
						liked = ?,
						modification_date = DATE('now')
					WHERE
						event_id = ?;
					""", [liked, event_id]
				)
		else:
			return redirect(url_for('get_template_403'))
	
	return redirect(url_for('get_template_main'))

#############
# TEMPLATES #
#############

@app.route("/about")
def get_template_about():
    return render_template('about.jinja')

@app.route("/403")
def get_template_403():
    return render_template('403.jinja')