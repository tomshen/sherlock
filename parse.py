import nltk
import re

import grammars

def preprocess(doc):
    sentences = nltk.sent_tokenize(doc)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def parse_sentence(sentence, grammar, draw=False):
    cp = nltk.RegexpParser(grammar)
    tree = cp.parse(sentence)
    if draw:
        result.draw()
    return tree

def tree_node_to_text(node):
    return ' '.join([w for w, pos in node.leaves()])

def basic_parse(doc):
    sentences = preprocess(doc)
    database = {}
    for sentence in sentences:
        tree = parse_sentence(sentence, grammars.noun_phrase)
        if len(tree) < 3:
            continue
        if hasattr(tree[0], 'node') and tree[0].node == 'NP':
            i = 1
            seen_verb = False
            while i < len(tree):
                if not seen_verb:
                    if len(tree[i]) == 2 and 'VB' in tree[i][1]:
                        seen_verb = True
                elif seen_verb:
                    if hasattr(tree[i], 'node') and tree[i].node == 'NP':
                        key = tree_node_to_text(tree[0])
                        value = tree_node_to_text(tree[i])
                        if key not in database:
                            database[key] = []
                        database[key].append(value)
                        break
                i += 1
    return database

if __name__ == '__main__':
    with open('data/set4/a1.txt') as f:
        doc = f.read()
        database = basic_parse(doc)
        question = None
        while question != 'STOP':
            question = raw_input('Ask a question of the form "Is <_> a[n] <_>?\n')
            toks = re.split('<|>', question)
            key = toks[1]
            ask_value = toks[3]
            if key in database and ask_value in database[key]:
                print('Yes!')
            else:
                print('No!')
