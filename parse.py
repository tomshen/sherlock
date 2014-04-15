#!/usr/bin/env python
import re
import sys
import string
import unicodedata

import nltk
from textblob import TextBlob
from textblob.blob import WordList
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

def get_sentiment(blob):
    if util.lists_overlap(['no','not','never','neither',"n't"], blob.raw.split()):
        return -1
    else:
        return 1

def tb_parse(blob):
    return [w for s in blob.parse().split() for w in s]

def preprocess(doc, np_extractor=None):
    paragraphs = [s.strip() for s in doc.split('\n') if '.' in s.strip()]
    if np_extractor == 'conll':
        return TextBlob('\n'.join(paragraphs), np_extractor=ConllExtractor())
    elif np_extractor == 'fast':
        return TextBlob('\n'.join(paragraphs))
    else:
        return TextBlob('\n'.join(paragraphs), np_extractor=SuperNPExtractor())

def extract_named_entities(blob):
    if len(blob.tags) == 0:
        return {}
    nes = []
    ne_tree = nltk.chunk.ne_chunk(blob.tags)
    last_is_name = False
    for child in ne_tree:
        if type(child) == nltk.tree.Tree:
            named_entity = ' '.join(w for w,_ in child.leaves())
            if child.node == 'PERSON':
                if last_is_name:
                    nes[-1] = (nes[-1][0] + ' ' + named_entity, nes[-1][1])
                else:
                    nes.append((named_entity, child.node))
                last_is_name = True
            else:
                last_is_name = False
                nes.append((named_entity, child.node))
        else:
            last_is_name = False
    return dict(nes)

def named_entity_type(named_entities, np):
    for n in named_entities:
        if n in np or np in n:
            return named_entities[n]
    return None

def determine_question_type(question):
    if type(question) != WordList:
        question = TextBlob(question).words
    if len(question) < 2:
        return None
    if question[0].lower() == 'who':
        return 'PERSON'
    elif question[0].lower() == 'what':
        return 'OBJECT'
    elif question[0].lower() == 'where':
        return 'GPE'
    elif question[0].lower() == 'when':
        return 'DATETIME'
    elif question[0].lower() == 'why':
        return 'ABSTRACT'
    elif question[0].lower() == 'how':
        if question[1].lower() in ['many', 'much']:
            return 'NUMBER'
        else:
            return 'VERB PHRASE'
    else:
        return None

def extract_verb_phrases(blob):
    cp = nltk.RegexpParser(grammars.verb_phrase)
    if len(blob.tags) == 0:
        return []
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
    parsed_sentence = tb_parse(sentence)
    named_entities = extract_named_entities(sentence)

    for i in xrange(len(noun_phrases)-1):
        np = noun_phrases[i]
        ne_key = named_entity_type(named_entities, np)
        next_np = noun_phrases[i+1]
        ne_val = named_entity_type(named_entities, next_np)
        first_np_word = np.split(' ')[0]
        cur_idx = words.index(first_np_word)
        next_idx = words.index(next_np.split(' ')[0])

        for word,_,_,pps in parsed_sentence:
            if first_np_word in word and 'PNP' in pps:
                continue

        sentiment = get_sentiment(sentence)
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
                relations.append((np, next_np, verb_relation,
                    sentiment, 1.0, sentence.tags[next_idx:next_idx+len(next_np.split(' '))], ne_key, ne_val))
        else:
            for verb_phrase in verb_phrases:
                if cur_idx < sentence.index(verb_phrase[0]) < next_idx:
                    relations.append((np, next_np, verb_phrase,
                        sentiment, 1.0, sentence.tags[next_idx:next_idx+len(next_np.split(' '))], ne_key, ne_val))
                    break
    return relations

BAD_PUNC = set(string.punctuation) - set([',', ';', ':', '.', '!', '?'])
def basic_parse(doc, np_extractor=None, verb_phrases_only=False):
    blob = preprocess(doc, np_extractor)
    sentences = blob.sentences
    database = {}
    for sentence in sentences:
        rels = extract_generic_relations(sentence, verb_phrases_only)
        for key, val, relation, sentiment, certainty, pos, nek, nev in rels:
            database[key] = database.get(key, {})
            database[key][val] = {
                'relation': relation,
                'certainty': certainty,
                'sentiment': sentiment,
                'pos': pos,
                'named entity key': nek,
                'named entity value': nev
            }
    return database
