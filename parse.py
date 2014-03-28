#!/usr/bin/env python
import re
import sys
import string
import unicodedata

from textblob import TextBlob
from textblob.en.np_extractors import ConllExtractor

import grammars
import util

def preprocess(doc, np_extractor):
    paragraphs = [s.strip() for s in doc.split('\n') if s.strip()][1:] # strip out title
    if np_extractor == 'conll':
        return TextBlob('\n'.join(paragraphs), np_extractor=ConllExtractor())
    else:
        return TextBlob('\n'.join(paragraphs))

def extract_generic_relations(sentence):
    relations = []
    noun_phrases = sentence.noun_phrases
    words = sentence.words
    new_noun_phrases = []
    for np in noun_phrases:
        try:
            if ' ' in np:
                nnp = ' '.join([words[words.lower().index(w)]
                    for w in str(np).split(' ')])
            else:
                nnp = words[words.lower().index(np)]
            new_noun_phrases.append(nnp)
        except:
            continue
    noun_phrases = new_noun_phrases
    sentiment = sentence.sentiment.polarity
    verbs = [w for w, pos in sentence.tags if pos[0] == 'V']

    for i in xrange(len(noun_phrases)-1):
        np = noun_phrases[i]
        next_np = noun_phrases[i+1]
        cur_idx = words.index(np.split(' ')[0])
        next_idx = words.index(next_np.split(' ')[0])
        is_verb = False
        for verb in verbs:
            if cur_idx < words.index(verb) < next_idx:
                is_verb = True
        if not is_verb: continue
        verb_relation = words[cur_idx+len(np.split(' ')):next_idx]
        if len(verb_relation) > 0:
            relations.append((np, next_np, verb_relation,
                sentiment, 1.0, sentence.tags[next_idx:next_idx+len(next_np.split(' '))]))
    return relations

BAD_PUNC = set(string.punctuation) - set([',', ';', ':', '.', '!', '?'])
def basic_parse(doc, np_extractor='conll'):
    blob = preprocess(doc, np_extractor)
    sentences = blob.sentences
    database = {}
    for sentence in sentences:
        rels = extract_generic_relations(sentence)
        for key, val, relation, sentiment, certainty, pos in rels:
            database[key] = database.get(key, {})
            database[key][val] = {
                'relation': relation,
                'certainty': certainty,
                'sentiment': sentiment,
                'pos': pos
            }
    return database


