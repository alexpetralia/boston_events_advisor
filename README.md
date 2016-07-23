# Boston Events

Every Sunday, I look for upcoming events in Boston I'd like to attend using [www.thebostoncalendar.com](http://www.thebostoncalendar.com). This is not only a time-consuming task, but also a tedious one: I have to wade through dozens of events which do not interest me to find the few that do. The objective of this project is to automate getting the signal from the noise.

**You can now view this project live <a href="http://52.2.13.97:8001/" target="_blank">here</a>.**

### Installation and run instructions

1. Clone the repo: `git clone github.com/alexpetralia/boston_events_advisor`
2. Create a virtual environment: `python3 -m venv .venv`
3. Activate the virtual environment: `source .venv/bin/activate`
4. Install the required packages: `pip install -r requirements.txt`
5. Start the redis server: `sudo redis-server`
6. Start the celerybeat and uWSGI processes in tmux sessions: `tmux new -s <session>`, `tmux attach -t <target>`
7. Start the celerybeat worker: `celery -A celeryd worker -l info -B`
8. Start the uWSGI server to run Flask: `uwsgi --socket 0.0.0.0:8001 --protocol=http --module app --callable app` or `uwsgi --socket /tmp/uwsgi_boston_events.sock --module app --callable app --processes 4 --threads 2`
9. If using Unix sockets and not HTTP, link your system nginx folder to the repo's nginx.conf: `sudo ln -s overhead/nginx_boston_events.conf /etc/nginx/sites-enabled` 
10. Start/restart nginx: `sudo service nginx start/reload`

### To do

* reduce feature space (suffering from curse of dimensionality)
