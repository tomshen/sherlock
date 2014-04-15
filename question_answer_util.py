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
import np_util as n

extractor = p.SuperNPExtractor()

def compare_phrases(q_phrase, t_phrase, uncommon):
    q_words = [word.lemmatize() for word, tag in q_phrase]
    t_words = [word.lemmatize() for word, tag in t_phrase]
    def get_bigrams(words):
        return [words[i-1:i+1] for i in xrange(1, len(words))]
    q_grams = get_bigrams(q_words)
    t_grams = get_bigrams(t_words)
    def judge_gram(target):
        if target in uncommon:
            return 3.5 + (1 if target.istitle() else 0)
        else:
            return 1
    ans1 = sum([max([judge_gram(g[0]), judge_gram(g[1])])
                for g in q_grams if g in t_grams]) - float(len(q_words)) + 1
    ans2 = sum([judge_gram(i)
                for i in q_words if i in t_words]) - float(len(q_words))
    return (ans1, ans2, t_phrase)

def examine_rels(q, q_phrase, bestrels, uncommon, mode):
    def taglist(l):
        return [tag for word, tag in l]
    if mode == 'IS':
        comp1, comp2, rel = max([compare_phrases(q_phrase, relation, uncommon)
                                 for best, relation in bestrels])
        print >> sys.stderr, comp1, comp2
        if comp1 >= -2 and comp2 >= 0:
            #"at most 2 unmatched bigrams and 1 unmatched unigram"
            return "Yes"
        elif comp1 >= -2 and comp2 >= -1:
            #if there's an unmatched unigram, it's either a red herring
            #or good enough
            print >> sys.stderr, q_phrase
            print >> sys.stderr, rel
            for word, tag in q_phrase:
                if (word, tag) not in rel:
                    if tag in ['IN', 'NNP', 'CD']:
                        return "No"
            return "Yes"

    elif mode == 'WHAT':
        first_tags = taglist(q[:3])
        if (first_tags[1][:2] == 'VB' and
            (first_tags[2][1] == 'N' or
             first_tags[2] == 'DT')):
            #what VB NP VP (what will Jake do,..)
            #compare things
            return "sleep"

    #nothing found here
    return ""

def parse_first(q, database, uncommon, mode):
    words = q.words.lower()
    nps = n.nps
    tags = q.tags
    if len(nps) == 0:
        print >> sys.stderr, "No subject found"
        return "No"
    subj = nps[0] #assuming subject is the first noun phrase
    print >> sys.stderr, "\tSubject:", subj
    first = words[0]

    if True:#first.lower() in ['is','was']: #is this everything?
        #question is an "is/was ___ NP/AP"
        #get index of the first word after the noun phrase
        loc = n.np_idx(subj, q)
        nexti = loc + len(subj.split()) + (1 if "'" in subj else 0)
        subj_tags = n.get_np_tags(subj, q)

        #get potential relations from database
        closest = n.get_similar_np(subj_tags, database)
        if closest == None:
            #retry with partial noun phrases
            closest = n.get_similar_np(subj_tags[0:1], database)
            nexti = nexti + 1 - len(subj_tags)
        if closest == None:
            closest = n.get_similar_np(subj_tags[0:2], database)
            nexti = nexti + 1
        if closest == None:
            return ""
        q_phrase = tags[nexti:]
        print >> sys.stderr, q_phrase
        if len(q_phrase) <= 1:
            q_phrase = tags

        #construct possible relations
        rel_tags = [database[close][e]["relation"]
                    + database[close][e]["pos"]
                    for close in closest
                    for e in database[close]]

        #get the best, compare
        bestrels = edit.distance(q_phrase, rel_tags)

        return examine_rels(q, q_phrase, bestrels, uncommon, mode)

    elif first.lower() in ['does','did','will']:
        #question is a "does/did/will ___ VP"
        return "No"
    return "No"

def parse_second(q, blob, uncommon, mode):
    sents = blob.sentences
    q_phrase = q.tags[2:]
    if mode == 'IS':
        q_phrase = q.tags[1:0]
    bestrels = edit.distance(q_phrase, [s.tags for s in sents if len(s.tags) > 6])
    return examine_rels(q, q_phrase, bestrels, uncommon, mode)

    return ""

def parse_question(question, database, raw):
    q = question
    q = q[0:1].lower() + q[1:]

    q = TextBlob(q, np_extractor=extractor)
    n.init_nps(q)

    #get 25th percentile words by frequency
    #actually, just gets infrequent words
    bigblob = TextBlob(raw, np_extractor=extractor)
    freqdict = bigblob.word_counts
    backwards = [(c, w) for w, c in freqdict.iteritems()]
    cutoff = (0.25 * sum([c for c, w in backwards]))
    best = 0
    #for c, w in sorted(backwards):
    #    best = c
    #    cutoff -= c
    #    if cutoff < 0:
    #        break
    uncommon = [w for c, w in sorted(backwards) if 1 < c < 4]#best]

    mode = q.words[0].upper()
    if mode in ['IS', 'WAS', 'DO', 'DOES', 'DID', 'WILL']:
        mode = 'IS'
    else:
        mode = "_".join(q.words[:2].upper())
    print >> sys.stderr, mode

    first_attempt = parse_first(q, database, uncommon, mode)
    if first_attempt != "":
        return first_attempt
    second_attempt = parse_second(q, bigblob, uncommon, mode)
    if second_attempt != "":
        return second_attempt
    third_attempt = b.backup_answer(q, n.nps, raw)
    return third_attempt
    #print >> sys.stderr, 'error parsing question, resorting to backup'
    #return b.backup_answer(q, raw)

if __name__ == "__main__":
    q = raw_input("Ask a question\n")
    q = TextBlob(q, np_extractor=extractor)
    print q.noun_phrases
    noun_phrases, idxs = n.get_nps_from_blob(q)
    print noun_phrases
    print q.words
    first =  noun_phrases[0]
    print n.get_np_tags(first, q)
    print q.tags
    print q.parse()
    #print p.extract_generic_relations(q)
