# Boston Events

Every Sunday, I look for upcoming events in Boston I'd like to attend using [www.thebostoncalendar.com](www.thebostoncalendar.com). This is not only a time-consuming task, but also a tedious one: I have to wade through dozens of events which do not interest me to find the few that do. The objective of this project is to automate getting the signal from the noise.

**You can now view this project live <a href='http://52.2.13.97:8001/' target='_blank'>here</a>.**

### Installation and run instructions

1. Clone the repo: `git clone github.com/alexpetralia/boston_events_advisor`
2. Create a virtual environment: `python3 -m venv .venv`
3. Activate the virtual environment: `source .venv/bin/activate`
4. Install the required packages: `pip install -r requirements.txt`
5. Start the redis server: `sudo redis-server`
6. Start the celerybeat worker: `celery -A celeryd worker -l info -B`
7. Start the uWSGI server to run Flask: `uwsgi --socket 0.0.0.0:8001 --protocol=http --module app --callable app`

### Notes
* Use `python3 manage.py runserver` to run the Flask development server

### To do

* incorporate distance from Home as a feature (lat, long) + include all listed Categories in the feature list [http://stackoverflow.com/questions/15257674/scikit-learn-add-features-to-a-vectorized-set-of-documents] + confidence in our predictions: 80% + use cross-validation as fitting method