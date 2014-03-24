import json

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
    lemma = __wnl.lemmatize(word, 'n')
    plural = word is not lemma
    return plural

def load_team_qa():
    with open('qa.json') as f:
        return json.load(f)