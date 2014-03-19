#!/usr/bin/env python
import nltk
import inflect
import re
import string

import grammars
import util
import backup_answer

Relations = util.enum('REL', 'ISA', 'HASA')

def parse_question(q, raw):
    print >> sts.stderr, 'error parsing question, resorting to backup'
    return backup_answer(q, raw)

    #toks = nltk.word_tokenize(q)
    #toks[0] = toks[0].lower()
    #tags = nltk.pos_tag(toks)
    #cp = nltk.RegexpParser(grammars.noun_phrase)
    #tree = cp.parse(tags)
    #subject = tree_node_to_text(tree[1])
    #query = tree_node_to_text(tree[2])
    #relation = ''
    #return (subject, query, relation)

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
