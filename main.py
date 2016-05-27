# author: alexpetralia
# -*- coding: utf-8 -*-

import requests
import sklearn 
import ast
import re 
import sqlite3
import sqlalchemy
import pandas as pd
import time
from bs4 import BeautifulSoup
from datetime import datetime as dt, timedelta as td
from deco import concurrent, synchronized

@synchronized
def populate_df(links):
    x = [None] * 1000
    for i, link in enumerate(links):
        x[i] = scrape(link)
    return [y for y in x if y is not None]
    
@concurrent
def scrape(link):
    response = requests.get(ROOT_URL + link, timeout=5)
    soup = BeautifulSoup(response.text, 'lxml')

    title = soup.find_all('h1')[0].get_text().strip()
    cost = [x for x in soup.find_all('p') if 'Admission:' in x.get_text()][0].find_all('span')[0].get_text().replace('\n','').replace('\t','').strip()
    description = soup.find(id='event_description').get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip()    
    
    return { 'title': title, 
             'cost': cost, 
             'description': description }

if __name__ == '__main__':
    
    ROOT_URL = 'http://www.thebostoncalendar.com'
    TAGS = ['Business', 'Innovation', 'Lectures & Conferences', 'Tech', 'University']    
    
    
    for i in range(1,2):
        date = dt.now().date() + td(1)
        payload = {'year': date.year, 'month': date.month, 'day': date.day, 'tags[]': TAGS}
        response = requests.get(ROOT_URL + '/events', params=payload, timeout=5)
        
        soup = BeautifulSoup(response.text, 'lxml')
        js_urls = soup.find_all('script', {'charset': 'utf-8'})[0].get_text().replace('\n', ' ')
        result = re.search('Gmaps.map.markers = (.*); Gmaps.map.create_markers', js_urls)
        content = ast.literal_eval( result.group(1) )
        
        links = []
        for event in content:
            for k, v in event.items():
                if k == 'description':
                    link = re.search('<a href=\'(.*)\'>', v)
                    links += [link.group(1)]
            
        results = populate_df(links)
        
        cnxn = sqlite3.connect('events.db')
        c = cnxn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
            title TEXT NOT NULL,
            cost TEXT NOT NULL,
            description TEXT NOT NULL
            );
        """)
        
        for result in results:
            c.execute("""
                INSERT INTO events (title, cost, description)
                SELECT ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM events
                    WHERE title = ?
                )
            """, (result['title'], result['cost'], result['description'], result['title']))
            
        time.sleep(20)
        
        # Use classes
        # Iterate over many links
        # Apply sklearn to df.values training/test sets