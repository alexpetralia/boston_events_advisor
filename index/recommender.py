# author: alexpetralia
# -*- coding: utf-8 -*-

import sqlalchemy
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn import cross_validation
from datetime import datetime as dt

def predict():

	cnxn = sqlalchemy.create_engine('sqlite:///events.db')
	df = pd.read_sql_table('events', cnxn)
	events, score = [], 1

	insample = df[df['creation_date'] <= dt.now().date()]#.dropna(how='any')
	oos = df[df['creation_date'] > dt.now().date()]

	if not oos.empty:

		# Training data
		count_vect, tfidf = CountVectorizer(), TfidfTransformer()
		X_train_tokens = count_vect.fit_transform(insample['description'])
		X_train_tfidf = tfidf.fit_transform(X_train_tokens)
		insample_dummies = insample['categories'].str.get_dummies(sep=', ')
		X_train_all = hstack([X_train_tfidf, insample_dummies])
		X_train, X_test, y_train, y_test = cross_validation.train_test_split(X_train_all, insample['liked'], test_size=.3, random_state=0)
		clf = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5, random_state=42).fit(X_train, y_train)
		score = clf.score(X_test, y_test)

		# Out of sample data
		X_oos_tokens = count_vect.transform(oos['description'])
		X_oos_tfidf = tfidf.transform(X_oos_tokens)

			# Match dummy matrix shapes
		oos_dummies = oos['categories'].str.get_dummies(sep=', ')
		missing_cols = list(set(insample_dummies.columns) - set(oos_dummies.columns))
		if missing_cols:
			oos_dummies[missing_cols] = 0

		X_oos = hstack([X_oos_tfidf, oos_dummies])
		events = tuple(zip(oos['event_id'], oos['title'], clf.predict(X_oos)))

	# for event_id, title, liked in events:
	# 	if liked == 1:
	# 		print('%s: %r => %s' % (event_id, title, liked))
	return events, score

if __name__ == '__main__':

   predict()