# author: alexpetralia
# -*- coding: utf-8 -*-

"""
Scrapes upcoming events from www.thebostoncalendar.com.

Usage:
scraper.py [--days=<days>]

Basic example:
python3 scraper.py -d 5

Parameters:
-d <days>, --days=<username>    Number of days out to scrape. [default: 7]
"""

import requests
import ast
import re 
import sqlite3
import time
from docopt import docopt
from bs4 import BeautifulSoup
from datetime import datetime as dt, timedelta as td
from overhead.functions import sendEmail, scraperLogger
from celeryd import celery

def http_request(link, *args, **kwargs):

    while True:
        try: 
            response = requests.get(link, *args, **kwargs)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            scraperLogger.debug("Request timed out after %s seconds. Retrying in 30 seconds..." % kwargs['timeout'])
            time.sleep(30)
            continue
        break

    return response
             
class ScraperConfig(object):
    
    def __init__(self):
        
        self.rootURL = 'http://www.thebostoncalendar.com'
        self.database = 'events.db'
        self.timeOut = 2.5
        
class EventsScraper(ScraperConfig):
    
    def __init__(self, daysOut):
        
        self.events = {}
        self.daysOut = daysOut
        self.today = dt.now().date()
        
    def scrapeEvents(self, tags):

        for i in range(self.daysOut):
            scraperLogger.info("__Scraping results page %s__" %i)
            resultsScraper = ResultsPageScraper(self.today + td(i), tags)
            self.events[str(self.today)] = resultsScraper.scrapeLinks()

        sendEmail('Next week\'s events in Boston are ready for you.', 'Head to over to 52.2.13.97:8001 to check it out.')
            
class ResultsPageScraper(ScraperConfig):
    
    def __init__(self, date, tags):
        
        super(ResultsPageScraper, self).__init__()
        self.data = []
        self.links = []        
        self.tags = tags
        self.date = date
    
    def scrapeResults(self):
        
        payload = {
            'year': self.date.year, 
            'month': self.date.month, 
            'day': self.date.day, 
            'tags[]': self.tags
        }
        # response =  requests.get(self.rootURL + '/events', params=payload, timeout=self.timeOut)
        response =  http_request(self.rootURL + '/events', params=payload, timeout=self.timeOut)
        return response.text
        
    def parseResults(self):

        soup = BeautifulSoup(self.scrapeResults(), 'lxml')
        js_urls = soup.find_all('script', {'charset': 'utf-8'})[0].get_text().replace('\n', ' ')
        result = re.search('Gmaps.map.markers = (.*); Gmaps.map.create_markers', js_urls)
        return ast.literal_eval( result.group(1) )
        
    def getLinks(self):
        
        for event in self.parseResults():
            for k, v in event.items():
                if k == 'description':
                    link = re.search('<a href=\'(.*)\'>', v)
                    self.links += [link.group(1)]
                                
    def writeToSql(self):
        
        cnxn = sqlite3.connect(self.database)
        c = cnxn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                cost TEXT NOT NULL,
                description TEXT NOT NULL,
                link TEXT NOT NULL,
                liked INTEGER NOT NULL DEFAULT 0,
                creation_date DATE NOT NULL,
                modification_date DATE NOT NULL,
                UNIQUE (title, creation_date)
            );
        """)
        
        for r in self.data:
            c.execute("""
                INSERT INTO events (title, cost, description, link, liked, creation_date, modification_date)
                SELECT ?, ?, ?, ?, 0, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM events
                    WHERE title = ? AND creation_date = ?
                );
            """, [r['title'], r['cost'], r['description'], r['link'], self.date, self.date,
                  r['title'], self.date])
        cnxn.commit()
            
    def scrapeLinks(self):
        
        self.getLinks()
        
        for i, link in enumerate(self.links):
            scraperLogger.info("Scraping detail page %s..." %i)
            detailScraper = DetailPageScraper(link)
            self.data.append( detailScraper.getData() )
            
        self.writeToSql()
        
        return self.data
                    
class DetailPageScraper(ScraperConfig):
    
    def __init__(self, link):
        
        super(DetailPageScraper, self).__init__()
        self.link = self.rootURL + link

    def getSoup(self):

        response = http_request(self.link, timeout=self.timeOut)
        self.soup = BeautifulSoup(response.text, 'lxml')
    
    def getTitle(self):
        
        title = self.soup.find_all('h1')[0].get_text().strip()
        self.title = title
    
    def getCost(self):
        
        costDiv = [x for x in self.soup.find_all('p') if 'Admission:' in x.get_text()][0]
        costSpan = costDiv.find_all('span')[0].get_text()
        cost = costSpan.replace('\n','').replace('\t','').strip()
        self.cost = cost
    
    def getDescription(self):
        
        descDiv = self.soup.find(id='event_description').get_text()
        description = descDiv.replace('\n', '').replace('\t', '').replace('\r', '').strip()   
        self.description = description
    
    def getData(self):
        
        self.getSoup()
        self.getTitle()
        self.getCost()
        self.getDescription()
        
        return { 'title': self.title, 
                 'cost': self.cost, 
                 'description': self.description,
                 'link': self.link
                }

@celery.task
def main():
    
    tags = ['Business', 'Innovation', 'Lectures & Conferences', 'Tech', 'University', 'Date Idea']
    scraper = EventsScraper(daysOut = 7)
    scraper.scrapeEvents(tags)

if __name__ == '__main__':
    
    main.delay()