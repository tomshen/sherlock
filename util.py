import json
import os

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
        return json.load(f)

def load_article(article_path):
    with open(os.path.join('data', article_path + '.txt')) as f:
        return f.read()