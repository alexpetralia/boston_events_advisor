# author: alexpetralia
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import sklearn 
import ast
import re 
from bs4 import BeautifulSoup
from datetime import datetime as dt

if __name__ == '__main__':
    
    ROOT_URL = 'http://www.thebostoncalendar.com/events'
    TAGS = ['Business', 'Innovation', 'Lectures & Conferences', 'Tech', 'University']
    
    today = dt.now().date()
    
    tag_string = ''
    for tag in TAGS:
        tag = tag.replace(' ', '+').replace('&','%26')
        tag_string += '&tags%5B%5D={}'.format(tag)
        
    URL = ROOT_URL + 'year={}&month={}&day={}'.format(today.year, today.month, today.day) + tag_string
    
    d = {'year': today.year, 'month': today.month, 'day': today.day, 'tags[]': TAGS}
    
    response = requests.get(ROOT_URL, params=d,timeout=1)
    soup = BeautifulSoup(response.text, 'lxml')
    
    map_js = soup.find_all('script', {'charset': 'utf-8'})[0].get_text()
    map_js = map_js.replace('\n', ' ')

    result = re.search('Gmaps.map.markers = (.*); Gmaps.map.create_markers', map_js)
    x = ast.literal_eval( result.group(1) )
    
    links = []
    for event in x:
        print(event)
        for k, v in event.items():
            if k == 'description':
                link = re.search('<a href=\'(.*)\'>', v)
                print(link)
                links += [link.group(1)]