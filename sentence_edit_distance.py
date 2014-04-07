import re
import operator
import nltk
import sys
import unicodedata
import util

di = []

def makeDict(raw):
    global di
    paragraphs = unicodedata.normalize('NFKD', raw.decode('utf8')).encode('ascii', 'ignore').split('\n')
    sentences = [s for p in paragraphs for s in nltk.sent_tokenize(p) if s]
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    di = sentences

def distance(target, data):
    di = data
    return (0, "nope")

def editDistance(target):
    global di
    def compareTokens(t1, t2):
        return t1 == t2
    target = target.split()
    best = ("N/A", 100)
    scores = []
    grid = [[-1]*(100) for j in range(1+len(target))]
    for i in range(1+len(target)):
        grid[i][0] = i*10
    for j in range(100):
        grid[0][j] = j*10
    grid[0][0] = 0
    for sentence in di:
        if len(sentence) < 5:
            continue
        for i in range(1, len(target)+1):
            prev = i
            for j in range(1, len(sentence)+1):
                if compareTokens(target[i-1], sentence[j-1]):
                    grid[i][j] = grid[i-1][j-1]
                    continue
                if (i > 1 and j > 1 and
                    target[i-2] == sentence[j-1] and
                    target[i-1] == sentence[j-2]):
                    grid[i][j] = grid[i-2][j-2] + 100
                    continue
                #insert, delete, substitute
                d1 = grid[i-1][j] + 10
                d2 = prev + 10
                d3 = grid[i-1][j-1] + 10
                prev = min([d1, d2, d3])
                grid[i][j] = prev
        score = grid[len(target)][len(sentence)]
        scores.append((score, sentence))
        #if best[1] >= score:
        #    best = (sentence, score)
    return sorted(scores)[:10]#best[0], best[1]

def getBestSentence(target, raw=None):
    if raw:
        makeDict(raw)
    return editDistance(target)

if __name__ == "__main__":
    makeDict(util.load_article(sys.argv[1]))
    sentence = raw_input('Ask a question of the form "Is _ a[n] _?\n')
    print getBestSentence(sentence)
