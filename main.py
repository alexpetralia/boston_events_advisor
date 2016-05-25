# author: alexpetralia
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import sklearn 
import ast
import re 
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime as dt
from deco import *

@concurrent
def scrape(i, link):
    print('starting link {}...'.format(i))
    response = requests.get(ROOT_URL + link, timeout=5)
    soup = BeautifulSoup(response.text, 'lxml')
    description = soup.find(id='event_description').get_text().replace('\n', '').replace('\t', '').replace('\r', '')
    title = soup.find_all('h1')[0].get_text()
    cost_container = [x for x in soup.find_all('p') if 'Admission:' in x.get_text()]
    cost = cost_container[0].find_all('span')[0].get_text().replace('\n','').replace('\t','')
    return title, cost, description
    
@synchronized
def populate_df():
    df = pd.DataFrame()
    for i, link in enumerate(links):
        title, cost, description = scrape(i, link)
        df = df.append( 
            {'title': title, 
            'description': description, 
            'link': ROOT_URL + link,
            'cost': cost}, 
        ignore_index=True)
    return df

if __name__ == '__main__':
    
    ROOT_URL = 'http://www.thebostoncalendar.com'
    TAGS = ['Business', 'Innovation', 'Lectures & Conferences', 'Tech', 'University']
    
    today = dt.now().date()
    
    tag_string = ''
    for tag in TAGS:
        tag = tag.replace(' ', '+').replace('&','%26')
        tag_string += '&tags%5B%5D={}'.format(tag)
        
    URL = ROOT_URL + 'year={}&month={}&day={}'.format(today.year, today.month, today.day) + tag_string
    
    d = {'year': today.year, 'month': today.month, 'day': today.day, 'tags[]': TAGS}
    
    response = requests.get(ROOT_URL + '/events', params=d, timeout=5)
    soup = BeautifulSoup(response.text, 'lxml')
    
    map_js = soup.find_all('script', {'charset': 'utf-8'})[0].get_text()
    map_js = map_js.replace('\n', ' ')

    result = re.search('Gmaps.map.markers = (.*); Gmaps.map.create_markers', map_js)
    x = ast.literal_eval( result.group(1) )
    
    links = []
    for event in x:
        for k, v in event.items():
            if k == 'description':
                link = re.search('<a href=\'(.*)\'>', v)
                links += [link.group(1)]
        
    x = populate_df()
        
    df = df[['title', 'cost', 'link', 'description']]
