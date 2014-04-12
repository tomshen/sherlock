_noun_phrase = r'''
  NP: {<DT|PP\$>?<JJ>*<NN|NNP>+}   # chunk determiner/possessive, adjectives and nouns
      {<NNP>+}                # chunk sequences of proper nouns
'''

#taken from https://gist.github.com/alexbowe/879414
noun_phrase = r"""
  NBAR:
    {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

  NP:
    {<NBAR>}
    {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""

verb_phrase = r'''
  VP: {.*<VB|VBD|VBG|VBN|VBP|VBZ>+.*}

'''
