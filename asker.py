import inflect
import util
import parse

p = inflect.engine()

def ask_questions(database, numQuestions):
    count = 0
    art = ("the", "an", "a", "The")
    for key in database:
        if (count >= numQuestions): break
        else:
            for value in database[key]:
                entry = database[key][value]
                if (count < numQuestions):                   
                    key_plural = util.is_plural(key)
                    is_verb = "Are" if key_plural else "Is"
                    rel_type = entry['type']
                    if (rel_type == parse.Relations.ISA):
                        if not value.startswith(art):
                            value = p.a(value)
                        string = "%s %s %s?" % (is_verb, key, value)
                        print string
                    elif (rel_type == parse.Relations.REL):
                        string = "%s %s related to %s?" % (is_verb, key, value)
                        print string
                    elif (rel_type == parse.Relations.HASA):
                        has_verb = "Do" if key_plural else "Does"
                        if not value.startswith(art):
                            value = p.a(value)
                        string = "%s %s have %s?" % (has_verb, key, value)
                    else:
                        print ("question of unknown relation type: " + str(entry['type']))
                    count += 1
