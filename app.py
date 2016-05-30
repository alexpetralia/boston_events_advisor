from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime as dt, timedelta as td
import sqlite3
import json

app = Flask(__name__)

@app.route("/get_events")
def get_weeks_events():
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
	
	pass

@app.route("/get_historical_events")
def get_historical_events():
	
	cnxn = sqlite3.connect('events.db')
	c = cnxn.cursor()
	today = dt.now().date()

	c.execute("""
		SELECT * FROM events
		WHERE creation_date <= ?
		AND liked <> 1
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

@app.route("/post_updates", methods=['GET', 'POST'])
def post_updates():

	if request.method == 'POST':
		results = request.values
		for event_id, liked in results.items():
			event_id = int(event_id.split('_')[-1])
			print(event_id, liked)
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

@app.route("/")
def get_template_main():
	context = json.loads(get_weeks_events()) # this should be get_recommendations

	return render_template('main.jinja', events=context)

@app.route("/homework")
def get_template_homework():
	context = json.loads(get_historical_events())

	return render_template('homework.jinja', events=context)

@app.route("/about")
def get_template_about():
    return render_template('about.jinja')

if __name__ == "__main__":

    app.run(debug=True)