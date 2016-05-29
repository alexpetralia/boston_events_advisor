# author: alexpetralia
# -*- coding: utf-8 -*-

import sqlalchemy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

cnxn = sqlalchemy.create_engine('sqlite:///events.db')
df = pd.read_sql('SELECT * FROM events', cnxn)

df = pd.read_sql_table('events', cnxn)

v = TfidfVectorizer(ngram_range=(2,2))
v.build_preprocessor()(df.ix[1,3])
v.build_tokenizer()(df.ix[1,3])
v.build_analyzer()(df.ix[1,3])
