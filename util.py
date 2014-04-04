import json
import os
import unicodedata

from nltk.stem import WordNetLemmatizer

__wnl = WordNetLemmatizer()

def enum(*sequential, **named):
    '''
    Source: http://stackoverflow.com/a/1695250
    '''
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def lists_overlap(A, B):
    '''
    Source: http://stackoverflow.com/a/17735466

    Note that this is *faster* that using set intersection, despite
    worse big-O runtime.
    '''
    return any(i in A for i in B)

def is_plural(word):
    '''
    true if plural
    '''
    words = word.split(" ")
    result = False
    for word in words:
        lemma = __wnl.lemmatize(word, 'n')
        plural = True if word is not lemma else False
        result = result or plural
    return result


def load_team_qa():
    with open('qa.json') as f:
        tqa = [qa for qa in json.load(f)[::2]]
        for qa in tqa:
            qa['is_bad_qns?'] = qa['is_bad_qns?'] == u'True'
            qa['is_disfluent?'] = qa['is_disfluent?'] == u'True'
            qa['qns_id'] = int(qa['qns_id'])
            ans = qa['answer']
            if ans in ['No', 'no', 'NO']:
                qa['answer'] = 'No'
            elif ans in ['Yes', 'yes', 'YES']:
                qa['answer'] = 'Yes'
        return [qa for qa in tqa if not qa['is_bad_qns?'] and not qa['is_disfluent?']]

def load_article(filename):
    with open(filename) as f:
        doc = f.read()
        return unicodedata.normalize('NFKD', doc.decode('utf8')).encode('ascii', 'ignore')

def synonyms(word, expanded):
    '''
    if expanded, gives extensive set of synonyms
    '''
    s = Set()
    syn_set = wn.synsets(word, pos=wn.NOUN)
    if (not len(syn_set) == 0):
        for set in syn_set:
            for lemma in set.lemmas:
                if (expanded): s.add(lemma.name.replace("_", " "))
                else:
                    sim = wn.path_similarity(set, syn_set[0])
                    if lemma.name != word and sim != None and sim > 0.3:
                        s.add(lemma.name.replace("_", " "))
    return s

def antonyms(word):
    s = Set()
    syn_set = wn.synsets(word, pos=wn.NOUN)
    if (not len(syn_set) == 0):
        L = [lemma.antonyms() for lemma in syn_set[0].lemmas]
        s = Set([i.name.replace("_", " ") for sublist in L for i in sublist])
    return s
