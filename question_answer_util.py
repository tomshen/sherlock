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
Relations = util.enum('REL', 'ISA', 'HASA')


def compare_phrases(q_phrase, t_phrase, uncommon):
    q_words = [word.lemmatize() for word, tag in q_phrase]
    t_words = [word.lemmatize() for word, tag in t_phrase]
    def get_bigrams(words):
        return [words[i-1:i+1] for i in xrange(1, len(words))]
    q_grams = get_bigrams(q_words)
    t_grams = get_bigrams(t_words)
    print >> sys.stderr, q_grams
    print >> sys.stderr, t_grams
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

def parse_yn(q, database, raw):
    #get 25th percentile words by frequency
    #actually, just gets infrequent words
    bigblob = TextBlob(raw, np_extractor=extractor)
    freqdict = bigblob.word_counts
    backwards = [(c, w) for w, c in freqdict.iteritems()]
    cutoff = (0.25 * sum([c for c, w in backwards]))
    best = 0
    for c, w in sorted(backwards):
        best = c
        cutoff -= c
        if cutoff < 0:
            break
    uncommon = [w for c, w in sorted(backwards) if 1 < c < 4]#best]
    words = q.words.lower()
    #nps = q.noun_phrases
    #nps = sorted([(np_idx(np, q), np) for np in nps])
    #nps = [np for idx, np in nps]
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
        #is that part of its own noun phrase? (det. or noun)
        # nextword, nexttag = q.tags[nexti]
        # print >> sys.stderr, nextword, nexttag
        #nextnp = ""
        #for np in nps:
        #    if words.lower().index(np.split()[0]) == nexti:
        #        nextnp = np
        #        break
        subj_tags = n.get_np_tags(subj, q)
        '''
        if False:#len(nps) > 1:
            nextnp = nps[1]
            #if yes then look to see if they are related in the db
            print >> sys.stderr, "\tfound nextnp:", nextnp
            nextnp_tags = get_np_tags(nextnp, q)
            close = get_similar_np(subj_tags, database)
            print >> sys.stderr, "\t\tclose is:", close
            if close:
                closer = get_similar_np(nextnp_tags, database[close[0]])
                if closer:
                    return "Yes"
            close = get_similar_np(nextnp_tags, database)
            if close:
                closer = get_similar_np(subj_tags, database[close[0]])
                if closer:
                    return "Yes"
                    '''
        #otherwise, assume it's an adjective phrase
        #rebuild sentence fragments from database
        closest = n.get_similar_np(subj_tags, database)
        if closest == None:
            #retry with partial noun phrases
            closest = n.get_similar_np(subj_tags[0:1], database)
            nexti = nexti + 1 - len(subj_tags)
        #else:
        #    more = n.get_similar_np(subj_tags[0:1], database)
        #    closest += more if more != None else []
        #    nexti = nexti + 1 - len(subj_tags)
        if closest == None:
            closest = n.get_similar_np(subj_tags[0:2], database)
            nexti = nexti + 1
        if closest != None:
            q_phrase = tags[nexti:]
            print >> sys.stderr, q_phrase
            if len(q_phrase) <= 1:
                q_phrase = tags
            rel_tags = [database[close][e]["relation"]
                        + database[close][e]["pos"]
                        for close in closest
                        for e in database[close]]
            #rel = [[word for word, tag in e] for e in rel_tags]
            #compare to the AP
            #best, relation = edit.distance(q_phrase, rel_tags)
            bestrels = edit.distance(q_phrase, rel_tags)
            comp1, comp2, rel = max([compare_phrases(q_phrase, relation, uncommon)
                                     for best, relation in bestrels])
            print >> sys.stderr, comp1, comp2
            if comp1 >= -2 and comp2 >= 0:
                return "Yes"
            elif comp1 >= -2 and comp2 >= -1:
                print >> sys.stderr, q_phrase
                print >> sys.stderr, rel
                for word, tag in q_phrase:
                    if (word, tag) not in rel:
                        if tag in ['IN', 'NNP', 'CD']:
                            return "No"
                return "Yes"

            #if comp == -1 and len(q_phrase) != 2:
            #    return "No"
                #if len(nps) <= 1:
                #    return "Yes"
                #rel = [word for word, tag in relation]
                #for np in nps[1:]:
                #    if np in rel:
                #        return "Yes"
        return ""

    elif first.lower() in ['does','did','will']:
        #question is a "does/did/will ___ VP"
        return "No"
    return "No"

def parse_wh(q, database):
    return ""

def parse_question(question, database, raw):
    q = question
    q = q[0:1].lower() + q[1:]

    q = TextBlob(q, np_extractor=extractor)
    n.init_nps(q)

    first_attempt = parse_yn(q, database, raw)
    if first_attempt != "":
        return first_attempt
    second_attempt = b.backup_answer(q, n.nps, raw)
    return second_attempt
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
