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
		WHERE creation_date BETWEEN ? and ?
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

@app.route("/post_updates", methods=['GET', 'POST'])
def post_updates():

	if request.method == 'POST':
		print(request.form.get('event_id_1'))
		results = request.values
		for k, v in results.items():
			print(k,v)

		return redirect(url_for('get_template_main'))

	return redirect(url_for('get_template_main'))

@app.route("/")
def get_template_main():
	context = json.loads(get_weeks_events())

	return render_template('main.jinja', events=context)

@app.route("/homework")
def get_template_homework():
    return render_template('homework.jinja')

@app.route("/about")
def get_template_about():
    return render_template('about.jinja')

if __name__ == "__main__":

    app.run(debug=True)