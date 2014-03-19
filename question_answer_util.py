#!/usr/bin/env python
import nltk
import inflect
import re
import string

import grammars
import util
import backup_answer

Relations = util.enum('REL', 'ISA', 'HASA')

def parse_question(q):
    return ('', '', '')
    #toks = nltk.word_tokenize(q)
    #toks[0] = toks[0].lower()
    #tags = nltk.pos_tag(toks)
    #cp = nltk.RegexpParser(grammars.noun_phrase)
    #tree = cp.parse(tags)
    #subject = tree_node_to_text(tree[1])
    #query = tree_node_to_text(tree[2])
    #relation = ''
    #return (subject, query, relation)

def related(subject, query, relation, database):
    return ''
    #if subject in database:
    #    if query in database[subject]:
    #        if relation == database[subject][query]["type"]:
    #            if relation == Relations

#ignore relation for now
    #return subject in database and query in database[subject]
