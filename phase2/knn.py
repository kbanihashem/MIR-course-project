import json
import multiprocessing
import threading
import numpy as np

from corpus import Corpus
from helper import cosine, most_repeated, sparse_to_numpy

class KNN:

    def __init__(self, corpus):
        self.corpus = corpus 
    
    def closest(self, query, k=1):
        metric = cosine
        q_doc = self.corpus.doc_from_dict(query, is_query=True)
        q_vec = self.corpus.get_vector(q_doc)
        
        dist_vec = [(i, metric(vec, q_vec) / self.corpus.l2[i]) for i, vec in enumerate(self.corpus.vecs)]
        dist_vec.sort(key=lambda x: x[1])
        #print(dist_vec)
        top_guesses = list(map(lambda x: self.corpus.docs[x[0]].category, dist_vec[:k]))
        return most_repeated(top_guesses)

    def set_valid(self, path):
        with open(path, 'r') as f:
            self.valid = json.load(f)

    def eval_query(self, i, k):
        self.query_ans[i] = self.closest(self.valid[i], k)
    
    def build_matrix(self):
        q_li = []
        for query in self.valid:
            q_doc = self.corpus.doc_from_dict(query, is_query=True)
            q_vec = self.corpus.get_vector(q_doc)
            q_li.append(q_vec)
        self.q_matrix = sparse_to_numpy(q_li, self.corpus.word_to_num.keys())

    def eval_many_queries(self, query_nums, k):
        self.corpus.build_np_vecs()

    def evaluate(self, k=1, limit=None, division_factor=3):
        if limit is None:
            limit = len(self.valid)
        self.query_ans = [None] * limit
        self.eval_many_queries(range(limit), k)
        log = []
        for i, query in enumerate(self.valid[:limit]):
            log.append(query['category'] == self.query_ans[i])

        return log

