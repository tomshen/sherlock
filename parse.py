#!/usr/bin/env python
import re
import sys
import string
import unicodedata

import nltk

import grammars
import util

def preprocess(doc):
    paragraphs = doc.split('\n')
    sentences = [s for p in paragraphs for s in nltk.sent_tokenize(p) if s]
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    return sentences

def parse_sentence(sentence, grammar, draw=False):
    cp = nltk.RegexpParser(grammar)
    tree = cp.parse(sentence)
    if draw:
        tree.draw()
    return tree

def tree_node_to_text(node):
    return ' '.join([w for w, pos in node.leaves()])

IS_WORDS = set(['is', 'are', 'am', 'be', 'been', 'isn\'t', 'aren\'t'])
HAS_WORDS = set(['has', 'have', 'hasn\'t', 'haven\'t'])
def extract_generic_relations(sentence, tree):
    relations = []
    last_noun_phrase = None
    seen_verb = []
    for el in tree:
        if type(el) is nltk.tree.Tree and el.node == 'NP':
            if last_noun_phrase is not None and seen_verb:
                lnp = tree_node_to_text(last_noun_phrase)
                np = tree_node_to_text(el)
                relations.append((lnp, np, seen_verb, False, 1.0))
                last_noun_phrase = None
                seen_verb = []
            else:
                if tree_node_to_text(el) not in string.punctuation:
                    last_noun_phrase = el
        elif seen_verb or el[1][0] == 'V':
            seen_verb.append(el)
    return relations

BAD_PUNC = set(string.punctuation) - set([',', ';', ':', '.', '!', '?'])
def basic_parse(doc):
    sentences = preprocess(doc)
    database = {}
    for sentence in sentences:
        tagged_sentence = [(w.lower() if t[:3] != 'NNP' else w, t) for w, t in
                nltk.pos_tag(sentence)]
        tagged_sentence = [(w, t) for w, t in tagged_sentence if len(set(w) & BAD_PUNC) == 0]
        if len(tagged_sentence) == 0:
            continue
        tree = parse_sentence(tagged_sentence, grammars.noun_phrase)
        rels = extract_generic_relations(sentence, tree)
        for key, val, verb, negative, certainty in rels:
            database[key] = database.get(key, {})
            database[key][val] = {
                'verb': verb,
                'certainty': certainty,
                'negative': negative,
                'pos': nltk.pos_tag(nltk.word_tokenize(val))
            }
    return database


