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
            
class Scraper(ScraperConfig):
    
    def __init__(self):
        
        super(Scraper, self).__init__()

    def get_links(self):
        cnxn = sqlite3.connect(self.database)
        c = cnxn.cursor()
        c.execute("""
            SELECT DISTINCT link
            FROM events
            WHERE categories IS NULL;
        """)
        self.links = [x[0] for x in c.fetchall()]
    
    def writeToSql(self, data):
        
        cnxn = sqlite3.connect(self.database)
        c = cnxn.cursor()
        
        c.execute("""
            UPDATE events
            SET
                categories = ?,
                latitude = ?,
                longitude = ?
            WHERE link = ?
        """, [data['categories'], data['latitude'], data['longitude'], data['link']])
        cnxn.commit()
            
    def scrapeLinks(self):
        
        self.get_links()
        
        for i, link in enumerate(self.links):
            scraperLogger.info("Scraping detail page %s..." %i)
            detailScraper = DetailPageScraper(link)
            try:
                data = detailScraper.getData()
            except:
                continue
            self.writeToSql( data )
                    
class DetailPageScraper(ScraperConfig):
    
    def __init__(self, link):
        
        super(DetailPageScraper, self).__init__()
        self.link = link

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

    def getCategories(self):

        categoriesDiv = [x for x in self.soup.find_all('p') if 'Categories:' in x.get_text()][0]
        categories = categoriesDiv.get_text().replace('\n', '').replace('\t', '').split(':')[-1]
        self.categories = categories

    def getCoordinates(self):

        DOMelem = self.soup.find('script', {'charset': 'utf-8'}).get_text()
        self.lng, self.lat = re.search(r'"lng": "(-[\d]+.[\d]+)", "lat": "([\d]+.[\d]+)"', DOMelem).groups()
    
    def getData(self):
        
        self.getSoup()
        self.getTitle()
        self.getCost()
        self.getDescription()
        self.getCategories()
        self.getCoordinates()
        
        return { 'title': self.title, 
                 'cost': self.cost, 
                 'description': self.description,
                 'link': self.link,
                 'latitude': float(self.lat),
                 'longitude': float(self.lng),
                 'categories': self.categories,
                }

@celery.task
def main():
    
    scraper = Scraper()
    scraper.scrapeLinks()

if __name__ == '__main__':
    
    main()