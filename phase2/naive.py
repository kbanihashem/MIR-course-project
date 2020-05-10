import json
import numpy as np

from corpus import Corpus
from document import Doc

class Naive_classifier:

    def __init__(self, corpus):
        self.corpus = corpus

    def set_valid(self, path):
        with open(path, 'r') as f:
            self.valid = json.load(f)

    def eval_query(self, i, alpha=0.01):
        q_doc = self.corpus.doc_from_dict(self.valid[i], is_query=True)
        score = np.log(self.corpus.class_doc_count / self.corpus.class_doc_count.sum())
        for word in q_doc.word_iterator:
            word_score = np.log(
                    (self.corpus.number_of_occurences[word,:] + alpha) /
                    (self.corpus.class_total_occurences + alpha * len(self.corpus.word_to_num))
                    )
            score += word_score
        best = np.argmax(score)
        self.query_ans[i] = Doc.int_to_category(best)

    def eval_many_queries(self, query_nums, alpha=0.01):
        for i in query_nums:
            self.eval_query(i, alpha=alpha)

    def evaluate(self, limit=None, division_factor=3, alpha=0.01):
        if limit is None:
            limit = len(self.valid)
        self.query_ans = [None] * limit
        self.eval_many_queries(range(limit), alpha=alpha)
        log = []
        for i, query in enumerate(self.valid[:limit]):
            log.append(query['category'] == self.query_ans[i])

        return log
