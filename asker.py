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


def ask_questions(filename, numQuestions, debug=False):
    nltk_tagger = NLTKTagger()
    p = inflect.engine()
    try:
        doc = util.load_article(filename)
        database = parse.basic_parse(doc)
    except:
        print "Invalid filename: " + filename
        sys.exit()
    art = ("the", "an", "a", "The")
    pairs = []
    result = []
    for key in database:
        if key[0] in string.punctuation: continue
        for entry in database[key]:
            pairs += [(key, entry)]
    if (numQuestions > len(pairs)):
        selected = random.sample(pairs, len(pairs))
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
        #print verb_phrase
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
            det_option = " the" if not key[0].isupper() else ""

            for (w, tag) in verbs:
                question3 = "What does%s %s %s?" % (det_option, key,  w.lemmatize("v"))
                #print question3
            det_option = " the" if not key[0].isupper() else ""
            question2 = "%s%s %s %s %s?" % (is_verb, det_option, key, blob, value)
            #print question2
            question = "%s%s %s related to %s?" % (is_verb, det_option, key, value)
        if (question != ""):
            print question
            result += [question]
    return result
        
        
if __name__ == "__main__":

    try:
        filename = sys.argv[1]
        numQuestions = int(sys.argv[2])
    except:
        #print "Invalid filename or numQuestions, using default values"
        filename = 'set4/a1'
        numQuestions = 30
        
    #print "Generating %d questions from %s" % (numQuestions, filename)
    ask_questions(filename, numQuestions)
