import json
import numpy as np

from corpus import Corpus
from helper import cosine, most_repeated, sparse_to_numpy, l2_norm

class K_eval:

    def __init__(self, corpus):
        self.corpus = corpus 
        self.parameters = dict()
    
    def set_valid(self, path):
        with open(path, 'r') as f:
            self.valid = json.load(f)
        self.q_start = 0
        self.q_end = len(self.valid)
        self.build_valid()

    def build_valid(self):
        pass

    def eval_queries(self):
        pass

    @property
    def active_query_count(self):
        return self.q_end - self.q_start

    def evaluate(self):
        self.query_ans = [None] * self.active_query_count
        self.eval_queries()
        self.log = []
        for i, query in enumerate(self.valid[self.q_start:self.q_end]):
            self.log.append(query['category'] == self.query_ans[i])
        return self.log

class KNN(K_eval):
    
    def __init__(self, corpus, limit=None, k=1):
        super().__init__(corpus)
        self.corpus_limit = limit if limit is not None else len(self.corpus.docs)
        self.parameters['k'] = k

    def build_valid(self):
        #requries: corpus.build_vec, corpus.build_np_vec
        q_li = []
        q_l2 = []
        for query in self.valid[self.q_start:self.q_end]:
            q_doc = self.corpus.doc_from_dict(query, is_query=True)
            q_vec = self.corpus.get_vector(q_doc)
            q_l2.append(l2_norm(q_vec))
            q_li.append(q_vec)
        self.q_matrix = sparse_to_numpy(q_li, self.corpus.word_to_num.keys())
        self.q_l2 = np.array(q_l2)

    def eval_queries(self):
        k = self.parameters['k']
        self.fill_product_matrix()
        best_k_indexes = self.product.argsort(axis=1)[:,:k]
        for i in range(self.active_query_count):
            self.query_ans[i] = most_repeated(map(lambda index: self.corpus.docs[index].category, best_k_indexes[i,:]))

class KNN_cosine(KNN):
    
    def __init__(self, corpus, **kwargs):
        super().__init__(corpus, **kwargs)

    def fill_product_matrix(self):
        limit = self.corpus_limit
        self.product = -np.dot(self.q_matrix, self.corpus.np_vecs[:limit,:].T) / self.corpus.l2[:limit]

class KNN_euclid(KNN):
    
    def __init__(self, corpus, **kwargs):
        super().__init__(corpus, **kwargs)

    def fill_product_matrix(self):
        limit = self.corpus_limit
        xy = np.dot(self.q_matrix, self.corpus.np_vecs[:limit,:].T) / self.corpus.l2[:limit]
        self.product = -2 * xy + self.corpus.l2[:limit]


class Naive_classifier(K_eval):

    def __init__(self, corpus, alpha=0.01):
        super().__init__(corpus, **kwargs)
        self.parameters['alpha'] = alpha

    def build_valid(self):
        #assumes that corpus.build_vec has been called
        self.q_docs = []
        for query in self.valid[self.q_start:self.q_end]:
            q_doc = self.corpus.doc_from_dict(query, is_query=True)
            q_docs.append(q_doc)
        self.q_docs

    def eval_queries(self, query_nums, alpha=0.01):
        for i in query_nums:
            alpha = self.parameters['alpha']
            score = np.log(self.corpus.class_doc_count / self.corpus.class_doc_count.sum())
            for word in q_doc.word_iterator:
                word_score = np.log(
                        (self.corpus.number_of_occurences[word,:] + alpha) /
                        (self.corpus.class_total_occurences + alpha * len(self.corpus.word_to_num))
                        )
                score += word_score
            best = np.argmax(score)
            self.query_ans[i] = Doc.int_to_category(best)
