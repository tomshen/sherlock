#!/usr/bin/env python
import nltk
import re
import string

import grammars
import util
import inflect

p = inflect.engine()

# Usage: Relations.REL, Relations.ISA, etc.
Relations = util.enum('REL', 'ISA', 'HASA')

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

def basic_parse(doc):
    sentences = preprocess(doc)
    database = {}
    for sentence in sentences:
        tagged_sentence = nltk.pos_tag(sentence)
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

def parse_question(q):
    toks = nltk.word_tokenize(q)
    toks[0] = toks[0].lower()
    tags = nltk.pos_tag(toks)
    cp = nltk.RegexpParser(grammars.noun_phrase)
    tree = cp.parse(tags)
    subject = tree_node_to_text(tree[1])
    query = tree_node_to_text(tree[2])
    relation = ''
    return (subject, query, relation)

def related(subject, query, relation):
    #ignore relation for now
    return subject in database and query in database[subject]

if __name__ == '__main__':
    with open('data/set4/a1.txt') as f:
        doc = f.read()
        database = basic_parse(doc)
        print database
        question = None
        while True:
            question = raw_input('Ask a question of the form "Is _ a[n] _?\n')
            if question == 'STOP':
                break
            (subject, query, relation) = parse_question(question)
            if subject == '' or query == '': #or relation == '':
                print "Couldn't parse."
                continue
            if related(subject, query, relation):
                print('Yes!')
            else:
                print('No!')

        print("Generating questions...")
        count = 0
        numQuestions = 20
        art = ("the", "an", "a", "The")
        for key in database:
            if (count >= numQuestions): break
            else:
                for value in database[key]:
                    entry = database[key][value]
                    if (count < numQuestions):
                      key_plural = (p.compare(key, p.plural(key)) == "p:p")
                      is_verb = "Are" if key_plural else "Is"
                      rel_type = entry['type']
                      if (rel_type == Relations.ISA):
                        if not value.startswith(art):
                            value = p.a(value) 
                        string = "%s %s %s?" % (is_verb, key, value)
                        print string
                      elif (rel_type == Relations.REL):
                        string = "%s %s related to %s?" % (is_verb, key, value)
                        print string
                      elif (rel_type == Relations.HASA):
                        has_verb = "Do" if key_plural else "Does"
                        if not value.startswith(art):
                            value = p.a(value) 
                        string = "%s %s have %s?" % (has_verb, key, value)
                      else:
                        print ("question of unknown relation type: " + str(entry['type']))
                      count += 1
