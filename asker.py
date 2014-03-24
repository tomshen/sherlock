#!/usr/bin/env python2.7
import inflect
import util
import parse
import sys
import random
from nltk.corpus import wordnet as wn

def synonyms(word):
    syn_set = wn.synsets(word)
    if (not len(syn_set) == 0):
        return [lemma.name for lemma in syn_set[0].lemmas]
    else: return []
    
def antonyms(word):
    syn_set = wn.synsets(word)
    if (not len(syn_set) == 0):
        L = [lemma.antonyms() for lemma in syn_set[0].lemmas]
        return [i.name for sublist in L for i in sublist]
    else: return []


def ask_questions():
    art = ("the", "an", "a", "The")
    pairs = []
    result = []
    for key in database:
        for entry in database[key]:
            pairs += [(key, entry)]
    if (numQuestions > len(pairs)):
        print "Not enough entries... :("
        return
    else: 
        selected = random.sample(pairs, numQuestions)
    for (key, value) in selected:
        entry = database[key][value]          
        key_plural = util.is_plural(key)
        #print key, key_plural
        is_verb = "Are" if key_plural else "Is"
        rel_type = entry['type']
        string = ""
        if (rel_type == parse.Relations.ISA):
            if not value.startswith(art):
                value = p.a(value)
            string = "%s %s %s?" % (is_verb, key, value)
        elif (rel_type == parse.Relations.REL):
            string = "%s %s related to %s?" % (is_verb, key, value)
        elif (rel_type == parse.Relations.HASA):
            has_verb = "Do" if key_plural else "Does"
            if not value.startswith(art):
                value = p.a(value)
            string = "%s %s have %s?" % (has_verb, key, value)
        else:
            print ("question of unknown relation type: " + str(entry['type']))
        if (string != ""):
            print string
            result += [string]
    return result
        
        
if __name__ == "__main__":
    p = inflect.engine()

    try:
        filename = sys.argv[1]
        numQuestions = int(sys.argv[2])
    except:
        print "Invalid filename or numQuestions"
        filename = 'data/set4/a4.txt'
        numQuestions = 20
    try:
        doc = open(filename).read()
        database = parse.basic_parse(doc)
    except:
        print "Invalid filename: " + filename

    print "Generating %d questions from %s" % (numQuestions, filename)
    ask_questions()
