# author: alexpetralia
# -*- coding: utf-8 -*-

import sqlalchemy
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

cnxn = sqlalchemy.create_engine('sqlite:///events.db')
df = pd.read_sql('SELECT * FROM events', cnxn)

df = pd.read_sql_table('events', cnxn)
df.loc[120, 'liked'] = 1
df.loc[149, 'liked'] = 1

# The cuttoff should be creation_dates before this week as the training set
train = df.head(150)
test = df.tail(df.shape[0] - 150)

text_clf = Pipeline([('vect',   CountVectorizer()),
                     ('tfidf',  TfidfTransformer()),
                     ('clf',    SGDClassifier(loss='hinge', penalty='l2',
                                              alpha=1e-3, n_iter=5, random_state=42)) 
                    ])
            
clf = text_clf.fit(train['description'].values, train['liked'].values)
predicted = clf.predict(test['description'].values)

for title, liked in zip(test['title'].values, predicted):
    print('%r => %s' % (title, liked))