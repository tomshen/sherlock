noun_phrase = r'''
  NP: {<DT|PP\$>?<JJ>*<NN|NNP>+}   # chunk determiner/possessive, adjectives and nouns
      {<NNP>+}                # chunk sequences of proper nouns
'''
