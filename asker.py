#!/usr/bin/env python2.7
import inflect
import util
import parse
import sys
import random
from sets import Set
#from dateutil import parser
from textblob import TextBlob, Word
from nltk.corpus import wordnet as wn
import string
from textblob.taggers import NLTKTagger

def is_date(s):
    months = ("January", "February", "March", "April", \
              "May", "June", "July", "August", "September", \
              "October", "November", "December")
    if any(month in s for month in months): return True
    else: return False

def conjugate(rel):
    try:
        split = rel.split(" ", 1)
        return Word(split[0]).lemmatize("v") + " " + split[1]
    except:
        return Word(rel).lemmatize("v")

def ask_questions(filename, numQuestions, debug=False):
    nltk_tagger = NLTKTagger()
    p = inflect.engine()

    doc = util.load_article(filename)
    database = parse.basic_parse(doc)

    names = open("names.txt")
    name_set = set()
    for name in names.read().split(" "):
        name_set.add(name.capitalize())
    art = ("the", "an", "a", "The")
    pairs = []
    result = []
    q_count = 0
    for key in database:
        if key[0] in string.punctuation: continue
        if "." in key: continue
        for entry in database[key]:
            pairs += [(key, entry)]
    
    randomized = random.sample(pairs, len(pairs))
    for (key, value) in randomized:
        entry = database[key][value]
                        
        relation = entry['relation']

        question = ""       
        rel = ""
        rel_tag = ""
        #print key, "KEY"
        add = True
        contains_in = False
        for i in xrange(len(relation)):
            (word, tag) = relation[i]
            if tag[0] == "V" and word[0].islower():
                rel += word
                rel_tag = tag
                if i+1 != len(relation):
                    count = 1
                    (nextword, nexttag) = relation[i+1]
                    while ((nexttag.startswith(("IN", "TO", "V", "RB"))) \
                        and (nextword not in ("that", "at", "also", "to", "in")) \
                        and (nextword[0].islower())):
                        if i+2 == len(relation) and (nexttag == "RB"):
                            break
                        elif nexttag == "IN": contains_in = True
                        rel += " " + nextword
                        count += 1
                        if count + i >= len(relation): break
                        (nextword, nexttag) = relation[i+count]
                    if rel != "": break
            elif ((tag in ("NNP", "NNS", "NN")) \
                   and rel == "" and (word not in key) and add):
                key += " " + word
            else: add = False

            
        #print key, "NEW KEY"
        #print value, "VALUE"
        val_name = False
        for word in value.split(" "):
            if word in name_set:
                #print word, "FOUND NAME"
                val_name = True
        key_plural = util.is_plural(key)
        #print relation
        #print rel
        if rel == "": continue
        #print [(word, tag) for (word, tag) in relation], "RELATION"
        det_option = " the" if not key[0].isupper() and key[0].isalpha() \
                     else ""
         
        try:
            value_tag = TextBlob(value).tags[0][1]
            c_rel = conjugate(rel)
            #print c_rel
            
            w_verb = "When" if is_date(value) else ("Who" if val_name else "What")
            if is_date(key):
                x = "in"
                if any(char.isdigit() for char in key): x = "on"
                question = "What happened %s %s?" % (x, key)
            elif c_rel != "be":
                if " " in rel:
                    split = c_rel.split(" ", 1)
                    be_rel = split[0] == "be"
                    if contains_in and not be_rel: c_rel = rel

                    if rel_tag == "VBD":
                        c_rel = rel
                        does_verb = "did"
                    elif key_plural:
                        does_verb = "are"
                    else: does_verb = "is"
                    if rel_tag == "VB":
                        does_verb = ""
                        det_option = ""
                    if (split[0] in ("can", "have")):
                        if split[0] == "have": does_verb = "has"
                        else: does_verb = "can"
                        c_rel = split[1]
                    if be_rel:
                        c_rel = split[1]
                        does_verb = "are" if key_plural else "is"
                else:
                    if rel_tag in ("VBD"):
                        does_verb = "did"
                    elif key_plural: does_verb = "do"
                    else: does_verb = "does"
                
                question = "%s %s%s %s %s?" % \
                           (w_verb, does_verb, det_option, key, c_rel)                
                
            else:
                verb_option = "" if (rel_tag != "VBN") else (" " + rel)
                is_verb = "are" if key_plural else "is"
                val_det_option = " the" if not value[0].isupper() else ""
                question = "What %s%s %s%s?" %  (is_verb, det_option, key, verb_option)
            #print w, tag, value
            print question
            #print "\n"
        except:
            is_verb = "Are" if key_plural else "Is"
            question = "%s%s %s related to %s?" % (is_verb, det_option, key, value)
            print question
            #print "\n"
        if (question != ""):
            q_count += 1
            result += [question]
        if q_count == numQuestions: break
    #print len(result)
    return result
        
        
if __name__ == "__main__":

    try:
        filename = sys.argv[1]
        numQuestions = int(sys.argv[2])
    except:
        #print "Invalid filename or numQuestions, using default values"
        filename = 'data/set1/a7.txt'
        numQuestions = 30
        
    #print "Generating %d questions from %s" % (numQuestions, filename)
    ask_questions(filename, numQuestions)
