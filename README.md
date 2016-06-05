# Boston events advisor

Every Sunday, I look for upcoming events in Boston I'd like to attend using [www.thebostoncalendar.com](www.thebostoncalendar.com). This is not only a time-consuming task, but also a tedious one: I have to wade through dozens of events which do not interest me to find the few that do. The objective of this project is to automate getting the signal from the noise.

# Installation and run instructions

1. git clone <repo>
2. python3 -m venv .venv
3. source .venv/bin/activate
4. sudo redis-server (start the redis server)
4. python3 manage.py runserver (start the webpage)
5. celery -A celeryd worker -l info -B (start the celery beat scheduled task)

# To do

* configure nginx/uWSGI (http://flask.pocoo.org/docs/0.11/deploying/uwsgi/)
* migrate to production

* incorporate distance from Home as a feature (lat, long) + include all listed Categories in the feature list [http://stackoverflow.com/questions/15257674/scikit-learn-add-features-to-a-vectorized-set-of-documents] + confidence in our predictions: 80% + use cross-validation as fitting method