#!/usr/bin/env python
import sys
import nltk
import inflect
import re
import string
from collections import defaultdict
from textblob import TextBlob

import grammars
import util
import np_util as n
import parse as p
extractor = p.SuperNPExtractor()

#object -> sentence list dict
back_data_obj = defaultdict(list)
#sentence -> object list dict
back_data_sen = defaultdict(list)

#generator that yields noun phrases of a chunked sentence
#from https://gist.github.com/alexbowe/879414
def leaves(tree):
    for subtree in tree.subtrees(filter = lambda t: t.node=='NP'):
        yield ' '.join([w for w, pos in subtree.leaves()])

def backup_answer(q, nps, raw):
    global back_data_keys
    global back_data_sen

    raw = raw.split('See also')[0]

    #chunker = nltk.RegexpParser(grammars.noun_phrase)
    if len(back_data_sen) == 0:
        # populate backup database
        paragraphs = raw.split('\n')
        sentences = [s for p in paragraphs for s in nltk.sent_tokenize(p) if s]
        #sentences = [nltk.word_tokenize(sent) for sent in sentences]
        #sentences = [nltk.tag.pos_tag(s) for s in sentences]
        for s in sentences:
            #identify objects
            #tree = chunker.parse(s)
            #s = ' '.join([word for word, tag in s])
            #noun_objects = leaves(tree)
            s = TextBlob(s, np_extractor=extractor)
            noun_objects, idxs = n.get_nps_from_blob(s)
            noun_objects += s.noun_phrases
            for np in noun_objects:
                if np not in back_data_sen[s]:
                    #append to _obj[n] for n in objects
                    back_data_obj[np].append(s)
                    #populate _sen[s]
                    back_data_sen[s].append(np)

    #chunk question, look for related sentences
    related_sents = []
    objs = []
    #tree = chunker.parse(nltk.tag.pos_tag(nltk.word_tokenize(q)))
    #noun_objects = leaves(tree)
    noun_objects = nps + q.noun_phrases
    for np in noun_objects:
        related_sents.extend(back_data_obj[np])
        objs.append(np)
    #rank related sentences by # of similar nouns
    num_related = []
    for s in related_sents:
        sent_nouns = back_data_sen[s]
        num_related.append(len([o for o in objs if o in sent_nouns]))
    if len(num_related) == 0:
        #found nothing related, guess "No"
        return "len(num_related) == 0"
    best, sent = sorted(zip(num_related, related_sents))[0]
    print >> sys.stderr, best, sent
    #print >> sys.stderr, "Best sentence was:"
    #print >> sys.stderr, best[0], best[1]
    best_nouns = back_data_sen[sent]
    if len(filter(lambda x: x in q.words, ['who', 'what', 'when', 'where'])) > 0:
        print >> sys.stderr, "wh-word"
        #find a new noun
        new_nouns = filter(lambda x: x not in noun_objects, best_nouns)
        if len(new_nouns) > 0:
            #arbitrarily choose the first
            return new_nouns[0]
        else:
            #uh, what?
            return best_nouns[0]
    else:
        #assume yes/no question (not why/how, because that's complicated)
        neg_sen = re.search("(not)|(n\'t)", sent.raw_sentences[0]) == None
        neg_q = re.search("(not)|(n\'t)", q.raw_sentences[0]) == None
        if best >= 2 and neg_sen == neg_q:
            #both the sentence and the question have/don't have a negator
            return "Yes"
        else:
            #one of them has a negator, the other doesn't
            return "No"
    return "end"

