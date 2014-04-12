#!/usr/bin/env python2.7

import parse
import question_answer_util as qau
import util

difficulties = ['too easy', 'easy', 'medium', 'hard', 'too hard']

def get_easy_questions():
    def easy_question(qa):
        ans_diff = qa['qns_difficulty_by_answerer']
        ques_diff = qa['qns_difficulty_by_questioner']
        return difficulties.index(ans_diff) + difficulties.index(ques_diff) <= 3
    return [qa for qa in util.load_team_qa() if easy_question(qa)]

def get_medium_questions():
    def medium_question(qa):
        ans_diff = qa['qns_difficulty_by_answerer']
        ques_diff = qa['qns_difficulty_by_questioner']
        return 3 <= difficulties.index(ans_diff) + difficulties.index(ques_diff) <= 5
    return [qa for qa in util.load_team_qa() if medium_question(qa)]

def get_hard_questions():
    def hard_question(qa):
        ans_diff = qa['qns_difficulty_by_answerer']
        ques_diff = qa['qns_difficulty_by_questioner']
        return difficulties.index(ans_diff) + difficulties.index(ques_diff) >= 5
    return [qa for qa in util.load_team_qa() if hard_question(qa)]

def main():
    easy_questions = get_easy_questions()
    articles = {}
    count = 0
    correct = 0
    for qa in easy_questions:
        if qa['path'] not in articles:
            doc = util.load_article('data/' + qa['path'] + '.txt')
            database = parse.basic_parse(doc)
            articles[qa['path']] = (doc, database)
        doc, database = articles[qa['path']]
        question = qa['qns_text']
        correct_answer = qa['answer']
        our_answer = qau.parse_question(question, database, doc)
        print 'Question: %s' % question
        print 'Correct answer: %s' % correct_answer
        print 'Our answer: %s' % our_answer
        if correct_answer.lower().strip() == our_answer.lower().strip():
            correct += 1
        count += 1
        print
    print 'Proportion correct: %.3f' % (float(correct) / count)


if __name__ == '__main__':
    main()
