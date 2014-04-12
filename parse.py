#!/usr/bin/env python
import re
import sys
import string
import unicodedata

import nltk
from textblob import TextBlob
from textblob.base import BaseNPExtractor
from textblob.en.np_extractors import FastNPExtractor, ConllExtractor

import grammars
import util

class SuperNPExtractor(BaseNPExtractor):
    def __init__(self):
        super(SuperNPExtractor, self).__init__
        self.__fast = FastNPExtractor()
        self.__conll = ConllExtractor()

    def extract(self, text):
        return list(set(self.__fast.extract(text)) | set(self.__conll.extract(text)))

def preprocess(doc, np_extractor=None):
    paragraphs = [s.strip() for s in doc.split('\n') if s.strip()][1:] # strip out title
    if np_extractor == 'conll':
        return TextBlob('\n'.join(paragraphs), np_extractor=ConllExtractor())
    elif np_extractor == 'fast':
        return TextBlob('\n'.join(paragraphs))
    else:
        return TextBlob('\n'.join(paragraphs), np_extractor=SuperNPExtractor())

def extract_verb_phrases(blob):
    cp = nltk.RegexpParser(grammars.verb_phrase)
    tree = cp.parse(blob.tags)
    verb_phrases = []
    for child in tree:
        if type(child) == nltk.tree.Tree and child.node == 'VP':
            verb_phrases.append([w[0] for w in child.flatten()])
    return verb_phrases

def extract_generic_relations(sentence, verb_phrases_only):
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
    verb_phrases = extract_verb_phrases(sentence)

    for i in xrange(len(noun_phrases)-1):
        np = noun_phrases[i]
        next_np = noun_phrases[i+1]
        cur_idx = words.index(np.split(' ')[0])
        next_idx = words.index(next_np.split(' ')[0])

        if not verb_phrases_only:
            is_verb = False
            for verb in [w for w, pos in sentence.tags if pos[0] == 'V']:
                try:
                    if cur_idx < words.index(verb) < next_idx:
                        is_verb = True
                except:
                    continue
            if not is_verb: continue
            verb_relation = sentence.tags[cur_idx+len(np.split(' ')):next_idx]
            if len(verb_relation) > 0:
                sentiment = TextBlob(' '.join(words[cur_idx:next_idx])).sentiment.polarity
                relations.append((np, next_np, verb_relation,
                    sentiment, 1.0, sentence.tags[next_idx:next_idx+len(next_np.split(' '))]))
        else:
            for verb_phrase in verb_phrases:
                if cur_idx < sentence.index(verb_phrase[0]) < next_idx:
                    sentiment = TextBlob(' '.join(words[cur_idx:next_idx])).sentiment.polarity
                    relations.append((np, next_np, verb_phrase,
                        sentiment, 1.0, sentence.tags[next_idx:next_idx+len(next_np.split(' '))]))
                    break
    return relations

BAD_PUNC = set(string.punctuation) - set([',', ';', ':', '.', '!', '?'])
def basic_parse(doc, np_extractor=None, verb_phrases_only=False):
    blob = preprocess(doc, np_extractor)
    sentences = blob.sentences
    database = {}
    for sentence in sentences:
        rels = extract_generic_relations(sentence, verb_phrases_only)
        for key, val, relation, sentiment, certainty, pos in rels:
            database[key] = database.get(key, {})
            database[key][val] = {
                'relation': relation,
                'certainty': certainty,
                'sentiment': sentiment,
                'pos': pos
            }
    return database
