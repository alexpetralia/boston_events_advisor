# author: alexpetralia
# -*- coding: utf-8 -*-

import sqlalchemy
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from datetime import datetime as dt

def predict():
	cnxn = sqlalchemy.create_engine('sqlite:///events.db')
	df = pd.read_sql_table('events', cnxn)

	train = df[df['creation_date'] <= dt.now().date()]
	test = df[df['creation_date'] > dt.now().date()]

	text_clf = Pipeline([('vect',   CountVectorizer()),
	                     ('tfidf',  TfidfTransformer()),
	                     ('clf',    SGDClassifier(loss='hinge', penalty='l2',
	                                              alpha=1e-3, n_iter=5, random_state=42)) 
	                    ])
	clf = text_clf.fit(train['description'].values, train['liked'].values)

	events = zip(test['event_id'], test['title'].values, clf.predict(test['description'].values))
	# for event_id, title, liked in events: # remember, events is a generator - values disappear if this is run
	# 	if liked == 1:
	# 		print('%s: %r => %s' % (event_id, title, liked))
	return events

if __name__ == '__main__':

	predict()