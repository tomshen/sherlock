#!/usr/bin/env python
import re
import string
import unicodedata

import nltk

import grammars
import util
import question_answer_util

# Usage: Relations.REL, Relations.ISA, etc.
Relations = util.enum('REL', 'ISA', 'HASA')

def preprocess(doc):
    paragraphs = unicodedata.normalize('NFKD', doc.decode('utf8')).encode('ascii', 'ignore').split('\n')
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
def extract_is_a_relations(sentence, tree):
    relations = []
    last_noun_phrase = None
    seen_is = False
    negative = False
    for i, el in enumerate(tree):
        if type(el) is nltk.tree.Tree and el.node == 'NP':
            if last_noun_phrase is not None and seen_is:
                lnp = tree_node_to_text(last_noun_phrase)
                np = tree_node_to_text(el)
                relations.append((lnp, np, Relations.ISA, negative, 1.0))
                last_noun_phrase = None
                seen_is = False
                negative = False
            else:
                if tree_node_to_text(el) not in string.punctuation:
                    last_noun_phrase = el
        elif el[0] in IS_WORDS:
            seen_is = True
            if 'n\'t' in el[0]:
                negative = True
        elif seen_is and el[0] == 'not':
            negative = True
        elif seen_is and el[1][0] == 'V' and tree[i-1][0] in IS_WORDS:
            seen_is = False

    return relations

HAS_WORDS = set(['has', 'have', 'hasn\'t', 'haven\'t'])
def extract_has_a_relations(sentence, tree):
    relations = []
    last_noun_phrase = None
    seen_has = False
    negative = False
    for i, el in enumerate(tree):
        if type(el) is nltk.tree.Tree and el.node == 'NP':
            if last_noun_phrase is not None and seen_has:
                lnp = tree_node_to_text(last_noun_phrase)
                np = tree_node_to_text(el)
                relations.append((lnp, np, Relations.HASA, negative, 1.0))
                last_noun_phrase = None
                seen_has = False
                negative = False
            else:
                if tree_node_to_text(el) not in string.punctuation:
                    last_noun_phrase = el
        elif el[0] in HAS_WORDS:
            seen_has = True
            if 'n\'t' in el[0]:
                negative = True
        elif seen_has and el[0] == 'not':
            negative = True
        elif seen_has and el[1][0] == 'V' and tree[i-1][0] in HAS_WORDS:
            seen_has = False
    return relations

def extract_generic_relations(sentence, tree):
    def is_special_verb(v):
        return v not in IS_WORDS and v not in HAS_WORDS
    relations = []
    last_noun_phrase = None
    seen_verb = False
    for el in tree:
        if type(el) is nltk.tree.Tree and el.node == 'NP':
            if last_noun_phrase is not None and seen_verb:
                lnp = tree_node_to_text(last_noun_phrase)
                np = tree_node_to_text(el)
                relations.append((lnp, np, Relations.REL, False, 1.0))
                last_noun_phrase = None
                seen_verb = False
            else:
                if tree_node_to_text(el) not in string.punctuation:
                    last_noun_phrase = el
        elif el[1][0] == 'V' and not is_special_verb(el[0]):
            seen_verb = True
    return relations

BAD_PUNC = set(string.punctuation) - set([',', ';', ':', '.', '!', '?'])
def basic_parse(doc):
    sentences = preprocess(doc)
    database = {}
    for sentence in sentences:
        tagged_sentence = [(w.lower() if t[:3] != 'NNP' else w, t) for w, t in
                nltk.pos_tag(sentence)]
        tagged_sentence = [(w, t) for w, t in tagged_sentence if len(set(w) & BAD_PUNC) == 0]
        tree = parse_sentence(tagged_sentence, grammars.noun_phrase)
        rels = extract_is_a_relations(sentence, tree)
        rels += extract_has_a_relations(sentence, tree)
        rels += extract_generic_relations(sentence, tree)
        for key, val, rel_type, negative, certainty in rels:
            database[key] = database.get(key, {})
            database[key][val] = {
                'type': rel_type,
                'certainty': certainty,
                'negative': negative
            }
    return database

if __name__ == '__main__':
    with open('data/set4/a2.txt') as f:
        doc = f.read()
        database = basic_parse(doc)
        question = None
        while True:
            question = raw_input('Ask a question of the form "Is _ a[n] _?\n')
            if question == 'STOP':
                break
            try:
                print parse_question(question)
            except (RuntimeError, TypeError, NameError):
                print "Error parsing."
