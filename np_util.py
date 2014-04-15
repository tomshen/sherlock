#!/usr/bin/env python

'''
Contains some helper functions I use for noun phrase extraction.
Maintains global lists of noun phrases and indices.
MAKE SURE TO CALL init_nps(blob) FOR EACH NEW SENTENCE!!
Also make sure to save your local copies of the lists if you want to use them later.
This isn't written with multiple concurrent uses in mind. There's no time for that.
'''

import sys
import nltk
import inflect
import re
import string
from textblob import TextBlob

import parse as p
extractor = p.SuperNPExtractor()

nps = []
idxs = []

def get_nps_from_blob(q):
    parse = q.parse()
    words = parse.split()[0]
    nps = []
    idxs = []
    i = 0
    curr = ""
    flag = 0
    quoteflag = 0
    newwords = []
    for w in words:
        if "'" == w[0]:
            if quoteflag == 1:
                quoteflag == 0
                continue
            flag = 2
        if flag > 0:
            flag = flag - 1
            if(len(newwords) == 0):
                quoteflag = 1
                continue
            newwords[-1][0] += w[0]
        else:
            newwords.append(w)

    words = newwords
    newwords = []
    flag = 0
    for w in words:
        if "n'" == w[0][:2]:
            flag = 2
        if flag > 0:
            flag = flag - 1
            newwords[-1][0] += w[0]
        else:
            newwords.append(w)

    flag = 0
    for w in newwords:
        if w[2] == u'B-NP' and flag == 0:
            curr = w[0]
            idxs.append(i)
            flag = 1
        elif w[2] == u'I-NP' and flag == 1:
            curr += " " + w[0]
        elif flag == 1:
            flag = 0
            nps.append(curr.lower())
        i += 1

    return nps, idxs

def init_nps(q):
    global nps
    global idxs
    nps, idxs = get_nps_from_blob(q)

def get_similar_np(np_tags, data):
    #requires pos for top-level entries
    print >> sys.stderr, "\t\tgetting similar for:", " ".join([
            word for word, tag in np_tags])
    def db_pos(entry):
        tags = []
        if "pos" in data[entry]:
            tags = data[entry]["pos"]
        else:
            tags = TextBlob(entry, np_extractor=extractor).tags
        return [word.lower() for word, tag in tags if tag[0] == "N"]
    def sim(np1words, np2):
        c = 0.0
        #print >> sys.stderr, "\t\t\tdatabase keys:", np2
        for word in np1words:
            if word.lower() in np2:
                c -= 1.0
        return c
    np = np_tags
    np_filter = [word for (word, tag) in np if tag[0] == "N"]
    print >> sys.stderr, "\t\tfiltered:", " ".join(np_filter)
    if len(np_filter) == 0:
        print >> sys.stderr, "\t\tNoun phrase without nouns:", np_tags
        np = [word for word, tag in np]
        if " ".join(np) in data:
            return " ".join(np)
        print >> sys.stderr, "\t\tNot in dictionary"
        return None
    sim_scores = [(sim(np_filter, db_pos(entry)), entry) for entry in data]
    sim_scores = [(score, len(entry), entry) for score, entry in sim_scores]
    result = sorted(sim_scores)[:4]
    best, l, entry = result[0]
    if best != 0:
        return [entry for best, l, entry in result]
    return None

def smartsplit(word):
    if "'" in word:
        word = word.replace("'", " '")
    return word.split()

def get_np_tags(np, q):
    #words = smartsplit(np)
    #loc = q.words.lower().index(words[0])
    #extra = 1 if "'" in np else 0
    #return q.tags[loc:loc+len(words) + extra]
    tags = q.tags
    t = []
    flag = 0
    rem = np
    for word, tag in tags:
        if word.lower() == rem[:len(word)].strip():
            flag = 1
            t.append((word, tag))
            rem = rem[len(word):].strip()
        elif flag == 1:
            break
    return t

def np_idx(np, q):
    #words = smartsplit(np)
    #loc = q.words.lower().index(words[0])
    #return loc
    global nps
    global idxs
    return idxs[nps.index(np)]
