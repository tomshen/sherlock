#!/usr/bin/env python2.7
import inflect
import util
import parse
import sys
import random
from sets import Set
from textblob import TextBlob, Word
from nltk.corpus import wordnet as wn
import string
from textblob.taggers import NLTKTagger

nltk_tagger = NLTKTagger()

def ask_questions():
    art = ("the", "an", "a", "The")
    pairs = []
    result = []
    for key in database:
        if key[0] in string.punctuation: continue
        for entry in database[key]:
            pairs += [(key, entry)]
    if (numQuestions > len(pairs)):
        print "Not enough entries... :("
        return
    else: 
        selected = random.sample(pairs, numQuestions)
    for (key, value) in selected:
        entry = database[key][value]
        """syn = util.synonyms(value, False)
        if (len(syn) != 0): 
            print "replaced " + value
            value = random.sample(syn, 1)[0]"""
        key_plural = util.is_plural(key)
        is_verb = "Are" if key_plural else "Is"
        verb_phrase = entry['relation']
        print verb_phrase
        try:
            verb = verb_phrase[0]
        except: verb = "related"
        question = ""
        if (verb == "is"):
            if not value.startswith(art):
                value = p.a(value)
            question = "%s %s %s?" % (is_verb, key, value)       
        elif (verb == "has"):
            has_verb = "Do" if key_plural else "Does"
            if not value.startswith(art):
                value = p.a(value)
            question = "%s %s have %s?" % (has_verb, key, value)
        else:
            blob = TextBlob(" ".join(verb_phrase), pos_tagger=nltk_tagger)
            tags = blob.pos_tags
            verbs = []
            for w,tag in blob.pos_tags:
                if tag[0] == "V":
                    verbs += [(w, tag)]
            action = [w for (w, tag) in verbs if tag != "VBZ"]
            try:
                w = Word(action[0])
                question3 = "What does %s %s?" % (key,  w.lemmatize("v"))
                print question3
            except: pass
            det_option = " the" if not key[0].isupper() else ""
            question2 = "%s%s %s %s %s?" % (is_verb, det_option, key, blob, value)
            print question2
            question = "%s%s %s related to %s?" % (is_verb, det_option, key, value)
        if (question != ""):
            print question, entry['sentiment']
            result += [question]
    return result
        
        
if __name__ == "__main__":
    p = inflect.engine()

    try:
        filename = sys.argv[1]
        numQuestions = int(sys.argv[2])
    except:
        print "Invalid filename or numQuestions, using default values"
        filename = 'set4/a1'
        numQuestions = 30
    try:
        doc = util.load_article(filename)
        database = parse.basic_parse(doc)
    except:
        print "Invalid filename: " + filename
        sys.exit()

    print "Generating %d questions from %s" % (numQuestions, filename)
    ask_questions()
