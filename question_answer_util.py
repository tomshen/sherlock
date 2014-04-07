#!/usr/bin/env python
import sys
import nltk
import inflect
import re
import string
from textblob import TextBlob
from textblob.np_extractors import ConllExtractor
extractor = ConllExtractor()

import grammars as g
import util
import backup_answer as b
import parse as p

Relations = util.enum('REL', 'ISA', 'HASA')

def parse_yn(q, database):
    words = q.words
    nps = q.noun_phrases
    subj = nps[0] #assuming subject is the first noun phrase
    first = words[0]

    if first.lower() in ['is','was']: #is this everything?
        #question is an "is/was ___ NP/AP"
        #get index of the first word after the noun phrase
        n = len(subj.split())
        next = ""
        nexti = 0
        for i in xrange(0, len(words) - n - 1):
            if subj == " ".join(words[i:i+n]):
                next = words[i+n]
                nexti = i+n
                break
        if next == "":
            print >> sys.stderr, "something bad happened."
        #is that part of its own noun phrase? (det. or noun)
        nextword, nexttag = q.tags[nexti]
        print >> sys.stderr, nextword, nexttag
        nextnp = ""
        for np in nps:
            if np.start == nexti:
                nextnp = np
                break
        if nextnp != "":
            #if yes then look to see if they are related in the db
            return "placeholder!"
        #otherwise, assume it's an adjective phrase
        else:
            #rebuild sentence fragments from database
            #compare to the AP
            #if one matches, -> yes
            #else -> no
            return "No"
    elif first.lower() in ['does','did','will']:
        #question is a "does/did/will ___ VP"
        return "No"
    return "No"

def parse_wh(q, database):
    return ""

def parse_question(q, database, raw):
    toks = nltk.word_tokenize(q)
    toks[0] = toks[0].lower()
    #print toks
    tags = nltk.pos_tag(toks)
    #print tags
    cp = nltk.RegexpParser(g.noun_phrase)
    tree = cp.parse(tags)
    noun_phrase_gen = b.leaves(tree)
    noun_phrases = [n for n in noun_phrase_gen]

    for n in noun_phrases:
        #print n
        if n in database:
            for e in database[n]:
                #print "\t", e
                if e in toks:
                    t = database[n][e]["type"]
                    s = "not " if database[n][e]["negative"] else ""
                    #print "\t\t", t, s
                    if t == Relations.ISA:
                        return n + " is " + s + "a " + e + "."
                    elif t == Relations.HASA:
                        return n + " has " + s + "a " + e + "."
                    else:
                        return n + " is " + s + "related to " + e + "."

    print >> sys.stderr, 'error parsing question, resorting to backup'
    return b.backup_answer(q, raw)

if __name__ == "__main__":
    q = raw_input("Ask a question\n")
    q = TextBlob(q, np_extractor=extractor)
    print q.noun_phrases
    print q.parse()
    print p.extract_generic_relations(q)
