#!/usr/bin/env python
import sys
import nltk
import inflect
import re
import string
from textblob import TextBlob

import grammars as g
import util
import backup_answer as b
import parse as p
import sentence_edit_distance as edit

extractor = p.SuperNPExtractor()
Relations = util.enum('REL', 'ISA', 'HASA')

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
        return [word for word, tag in tags if tag[0] == "N"]
    def sim(np1words, np2):
        c = 0.0
        #print >> sys.stderr, "\t\t\tdatabase keys:", np2
        for word in np1words:
            if word in np2:
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
    best, l, entry = min(sim_scores)
    if best != 0:
        return entry
    return None

def get_np_tags(np, q):
    words = np.split()
    loc = q.words.lower().index(words[0])
    return q.tags[loc:loc+len(words)]

def parse_yn(q, database):
    words = q.words.lower()
    nps = q.noun_phrases
    tags = q.tags
    if len(nps) == 0:
        print >> sys.stderr, "No subject found"
        return "No"
    subj = nps[0] #assuming subject is the first noun phrase
    print >> sys.stderr, "\tSubject:", subj
    first = words[0]

    if first.lower() in ['is','was']: #is this everything?
        #question is an "is/was ___ NP/AP"
        print >> sys.stderr, "\tis/was"
        #get index of the first word after the noun phrase
        subj_words = subj.split()
        loc = words.index(subj_words[0])
        nexti = loc + len(subj_words)
        #is that part of its own noun phrase? (det. or noun)
        # nextword, nexttag = q.tags[nexti]
        # print >> sys.stderr, nextword, nexttag
        nextnp = ""
        for np in nps:
            if words.lower().index(np.split()[0]) == nexti:
                nextnp = np
                break
        subj_tags = get_np_tags(subj, q)
        if nextnp != "":
            #if yes then look to see if they are related in the db
            print >> sys.stderr, "\tfound nextnp:", nextnp
            nextnp_tags = get_np_tags(nextnp, q)
            close = get_similar_np(subj_tags, database)
            print >> sys.stderr, "\t\tclose is:", close
            if close:
                closer = getsimilar_np(nextnp_tags, database[close])
                if closer:
                    return "Yes."
                else:
                    return "No."
            close = get_similar_np(nextnp_tags, database)
            if close:
                closer = getsimilar_np(subj_tags, database[close])
                if closer:
                    return "Yes."
                else:
                    return "No."
            return "No."
        #otherwise, assume it's an adjective phrase
        else:
            print >> sys.stderr, "\tAP/VP"
            #rebuild sentence fragments from database
            close = get_similar_np(subj_tags, database)
            print >> sys.stderr, "\tclose is:", close
            if close == None:
                return "No."
            rel_tags = [database[close][e]["relation"]
                        + database[close][e]["pos"] for e in database[close]]
            #rel = [[word for word, tag in e] for e in rel_tags]
            #compare to the AP
            best, relation = edit.distance(tags[nexti:], rel_tags)
            if best < 7:
                return "Yes."
            return "No."
    elif first.lower() in ['does','did','will']:
        #question is a "does/did/will ___ VP"
        return "No"
    return "No"

def parse_wh(q, database):
    return ""

def parse_question(q, database, raw):
    '''
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
    '''
    return parse_yn(TextBlob(q, np_extractor=extractor), database)
    #print >> sys.stderr, 'error parsing question, resorting to backup'
    #return b.backup_answer(q, raw)

if __name__ == "__main__":
    q = raw_input("Ask a question\n")
    q = TextBlob(q, np_extractor=extractor)
    print q.noun_phrases
    first =  q.noun_phrases[0]
    firstsp = first.split()
    loc = q.words.lower().index(firstsp[0])
    print q.tags[loc:loc+len(firstsp)]
    print q.parse()
    print p.extract_generic_relations(q)
