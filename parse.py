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
        numQuestions = 10
        vowels = ('a','e','i','o','u','A','E','I','O','U')
        art = ("the", "an", "a")
        for key in database:
            if (count >= numQuestions): break
            else:
                for value in database[key]:
                    if (count < numQuestions):
                        if value.lower().startswith(art): d = ""
                        elif value.startswith(vowels): d = " an"
                        else: d = " a"
                        string = "Is %s%s %s?" % (key, d, value)
                        print string
                        count += 1
