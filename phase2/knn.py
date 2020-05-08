import json

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

    def evaluate(self, k=1, print_every=1, verbose=False, limit=None):
        log = []
        for i, query in enumerate(self.valid):
            if limit is not None and i > limit:
                break
            if verbose and i % print_every == 0:
                print(i)
            y = query['category']
            y_hat = self.closest(query, k)
            log.append(y == y_hat) 
        return log
