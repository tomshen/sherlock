#!/usr/bin/env python
import sys

import asker

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: ./ask [path to article] [number of questions]')
    else:
        filename = sys.argv[1]
        nquestions = int(sys.argv[2])
        if nquestions <= 0:
            print('Number of questions must be positive.')
            sys.exit()
        try:
            f = open(filename)
            f.close()
        except:
            print 'No file found at "%s".' % filename
            sys.exit()
        asker.ask_questions(filename, nquestions, debug=False)
