import json
import multiprocessing
import numpy as np

from corpus import Corpus
from helper import cosine, most_repeated

class KNN:

    def __init__(self, corpus):
        self.corpus = corpus 
    
    def closest(self, query, k=1):
        metric = cosine
        q_doc = self.corpus.doc_from_dict(query, is_query=True)
        q_vec = self.corpus.get_vector(q_doc)
        
#        keys = q_vec.keys()
        keys = self.corpus.word_to_num.keys()
        A_matrix = np.zeros((len(self.corpus.vecs), len(keys)))
        for i in range(len(self.corpus.vecs)):
            if i % 100 == 0:
                print(i)
            if i > 1000:
                break
            A_matrix[i] = np.array([self.corpus.vecs[i].get(key, 0) for key in keys])
        qv = np.array([q_vec.get(key, 0) for key in keys])
#        dist_vec = list(zip(range(len(self.corpus.vecs)), np.matmul(A_matrix, qv)))
#        dist_vec = [(i, metric(vec, q_vec)) for i, vec in enumerate(self.corpus.vecs)]
#        dist_vec.sort(key=lambda x: x[1])
#        top_guesses = list(map(lambda x: self.corpus.docs[x[0]].category, dist_vec[:k]))
#        return most_repeated(top_guesses)

    def set_valid(self, path):
        with open(path, 'r') as f:
            self.valid = json.load(f)

    def eval_query(self, i, k):
        self.query_ans[i] = self.closest(self.valid[i], k)

    def evaluate(self, k=1, limit=None):
        if limit is None:
            limit = len(self.valid)
        self.query_ans = [None] * len(self.valid)
        for i, query in enumerate(self.valid[:limit]):
            self.eval_query(i, k)
            print(f"{i} done")

        log = []
        for i, query in enumerate(self.valid):
            log.append(query['category'] == self.query_ans[i])

        return log
