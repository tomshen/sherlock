import re
import sys
import string
import unicodedata

import nltk

import parse as p

if len(sys.argv) < 2:
    print 'Usage: ./answer.py [datafile]'
    sys.exit()
datafile = sys.argv[1]
with open(datafile) as f:
    doc = f.read()
    database = p.basic_parse(doc)
    question = None
    while True:
        question = raw_input('Ask a question of the form "Is _ a[n] _?\n')
        if question == 'STOP':
            break
        print 'Answering question...'
        print p.qau.parse_question(question, doc)
