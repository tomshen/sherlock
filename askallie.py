#!/usr/bin/env python2.7
import os

for s in range(1,5):
    for a in range(1,11):
        print 'Running on set %d, article %d...' % (s,a)
        os.system('./ask data/set%d/a%d.txt 10' % (s,a))
