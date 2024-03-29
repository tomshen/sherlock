#!/usr/bin/env python2.7
import re
import sys
import string
import unicodedata

import nltk

import parse as p
import util
import question_answer_util as qau

if len(sys.argv) < 3:
    print 'Usage: ./answer [datafile] [questionfile]'
    sys.exit()
datafile = sys.argv[1]
qfile = sys.argv[2]
doc = util.load_article(datafile)
print >> sys.stderr, 'Generating article relation database...'
database = p.basic_parse(doc, np_extractor=p.SuperNPExtractor())
"""
for k in database.keys()[:5]:
    print k
    for e in database[k]:
        print "\t", e
        for v in database[k][e]:
            print "\t\t", database[k][e][v]
"""

question = None
for question in open(qfile, 'rb').readlines():
    print >> sys.stderr, 'Answering question:', question.strip()
    print qau.parse_question(question, database, doc)
