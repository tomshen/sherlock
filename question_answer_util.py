#!/usr/bin/env python
import sys
import nltk
import inflect
import re
import string

import grammars as g
import util
import backup_answer as b

Relations = util.enum('REL', 'ISA', 'HASA')

def parse_question(q, database, raw):
    toks = nltk.word_tokenize(q)
    toks[0] = toks[0].lower()
    print toks
    tags = nltk.pos_tag(toks)
    print tags
    cp = nltk.RegexpParser(g.noun_phrase)
    tree = cp.parse(tags)
    noun_phrase_gen = b.leaves(tree)
    noun_phrases = [n for n in noun_phrase_gen]

    for n in noun_phrases:
        print n
        if n in database:
            for e in database[n]:
                print "\t", e
                if e in toks:
                    t = database[n][e]["type"]
                    s = "not " if database[n][e]["negative"] else ""
                    print "\t\t", t, s
                    if t == Relations.ISA:
                        return n + " is " + s + "a " + e + "."
                    elif t == Relations.HASA:
                        return n + " has " + s + "a " + e + "."
                    else:
                        return n + " is " + s + "related to " + e + "."

    print >> sys.stderr, 'error parsing question, resorting to backup'
    return b.backup_answer(q, raw)

#deprecated
def related(subject, query, relation, database):
    if subject in database:
        if query in database[subject]:
            if relation == database[subject][query]["type"]:
                if relation == Relations.ISA:
                    return subject + " is a " + query + "."
                elif relation == Relations.HASA:
                    return subject + " has a " + query + "."
                else:
                    return subject + " is related to " + query + "."
    else:
        return " ".join(["Database error on s/q/r:", subject, query, relation])

#ignore relation for now
    #return subject in database and query in database[subject]
