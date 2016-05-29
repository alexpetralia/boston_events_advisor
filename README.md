# Boston Events Advisor

Every Sunday, I look for upcoming events in Boston I'd like to attend using [www.thebostoncalendar.com](www.thebostoncalendar.com). This is not only a time-consuming task, but also a tedious one: I have to wade through dozens of events which do not interest me to find the few that do. The objective of this project is to automate finding the signal from the noise.

# Installation and run instructions

1. git clone <repo>
2. python3 -m venv .venv
3. source .venv/bin/activate
4. python3 manage.py runserver (runs the webpage)
5. celery -A scraper worker -l info -B (runs the beat task in the background)

# Next Steps

1. pandas/sklearn classification analysis 
2. Flask app

# To do

* add a wrapper for requests when it fails
* add logging
* add email notifications (once per week) to flask app
* use CRSF token
* scraper runs weekly
* include low probability + random in order to diversify events pool eg. showing 20 events of 54 this week
* (modal dropdown) Submit PIN to prove you're Alex (hashed server-side) -> Great, see you next week!
* Confidence in our predictions: 80%