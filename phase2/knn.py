import json
import multiprocessing

from corpus import Corpus
from helper import cosine, most_repeated

class KNN:

    def __init__(self, corpus):
        self.corpus = corpus 
    
    def closest(self, query, k=1):
        metric = cosine
        q_doc = self.corpus.doc_from_dict(query, is_query=True)
        q_vec = self.corpus.get_vector(q_doc)
        dist_vec = [(i, metric(vec, q_vec)) for i, vec in enumerate(self.corpus.vecs)]
        dist_vec.sort(key=lambda x: x[1])
        top_guesses = list(map(lambda x: self.corpus.docs[x[0]].category, dist_vec[:k]))
        return most_repeated(top_guesses)

    def set_valid(self, path):
        with open(path, 'r') as f:
            self.valid = json.load(f)

    def eval_query(self, i, k):
        self.query_ans[i] = self.closest(self.valid[i], k)

    def evaluate(self, k=1, limit=None):
        if limit is None:
            limit = len(self.valid)
        self.query_ans = [None] * len(self.valid)
        p = [None] * len(self.valid)
        for i, query in enumerate(self.valid):
            p[i] = multiprocessing.Process(target=self.eval_query, args=(i, k))

        print("starting")
        for i in range(limit):
            p[i].start()
        for i in range(limit):
            print(f"got {i}")
            p[i].join()
       
        log = []
        for i, query in enumerate(self.valid):
            log.append(query['category'] == self.query_ans[i])

        return log
