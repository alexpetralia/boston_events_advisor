import os
import sqlite3
import logging
from datetime import datetime as dt

def sql_execute(*args):
	cnxn = sqlite3.connect('events.db')
	c = cnxn.cursor()
	c.execute(*args)
	cnxn.commit()
	return c.fetchall()

def init_logger():

    logs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)

    fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    now = dt.now().strftime("%Y%m%dT%H%M%S")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    handler = logging.FileHandler(os.path.join(logs_path, 'scraper_%s.txt' % now))
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(fmt)
    
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger

scraperLogger = init_logger()

from overhead.gmail import GmailSender

def sendEmail(subject, body):
    Sender = GmailSender(os.path.join(os.path.dirname(__file__), 'client_secret.json'))
    Sender.sendMessage('alex.petralia@gmail.com', subject, body)