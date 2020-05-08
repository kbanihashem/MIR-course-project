from Corpus import corpus
from helper import cosine

class KNN:

    def __init__(self, corpus):
        self.corpus = corpus 
    
    def closest(self, query, k=1):
        metric = cosine
        q_vec = corpus.process_query(query)
        def dist(vec):
            return metric(vec, q_vec)
        dist_vec = [(i, dist(vec, q_vex)) for i, vec in enumerate(corpus.vecs)]
        dist_vec.sort(key=lambda x: x[1])
#        top_guesses = list(map(lambda x: 
#        return most_repeated(list(map(lambda x: 
