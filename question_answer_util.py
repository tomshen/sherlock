##Under construction

import backup_answer.py

def parse_question(q):
    toks = nltk.word_tokenize(q)
    toks[0] = toks[0].lower()
    tags = nltk.pos_tag(toks)
    cp = nltk.RegexpParser(grammars.noun_phrase)
    tree = cp.parse(tags)
    subject = tree_node_to_text(tree[1])
    query = tree_node_to_text(tree[2])
    relation = ''
    return (subject, query, relation)

def related(subject, query, relation, database):
    if subject in database

#ignore relation for now
    #return subject in database and query in database[subject]
