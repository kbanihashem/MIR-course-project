import json
import numpy as np

from corpus import Corpus
from helper import most_repeated, sparse_to_numpy, l2_norm, dist_euclid, dist_cosine
from document import Doc

class K_eval:

    def __init__(self, corpus, limit=None):
        self.corpus = corpus 
        self.parameters = dict()
        self.limit = limit

    def set_corpus(self, corpus):
        self.corpus = corpus

    def set_singular_valid(self, doc):
        self.valid = [doc]
        self.q_start = 0
        self.q_end = 1
        self.build_valid()
    
    def set_valid(self, path):
        with open(path, 'r') as f:
            self.valid = json.load(f)
        self.q_start = 0
        self.q_end = len(self.valid)
        self.build_valid()

    @property
    def limit(self):
        return len(self.corpus.docs) if self._limit is None else self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    @property
    def active_queries(self):
        return self.valid[self.q_start:self.q_end]

    def build_valid(self):
        pass

    def eval_queries(self):
        pass

    def pre_build(self):
        pass

    def fill_amalkard(self):
        #confusion matrix
        self.confusion_matrix = np.zeros((4, 4), dtype=np.int64)
        for i in range(self.active_query_count):
            real = self.active_queries[i]['category'] - 1
            pred = self.query_ans[i] - 1
            self.confusion_matrix[pred, real] += 1
        self.accuracy = self.confusion_matrix.trace() / self.confusion_matrix.sum()
        self.precision = self.confusion_matrix.diagonal() / self.confusion_matrix.sum(axis=1)
        self.recall = self.confusion_matrix.diagonal() / self.confusion_matrix.sum(axis=0)
        self.f1 = 2 * self.precision * self.recall / (self.precision + self.recall)
        self.macro_averaged_f1 = self.f1.mean()

    @property
    def active_query_count(self):
        return self.q_end - self.q_start

    def evaluate(self):
        self.query_ans = [None] * self.active_query_count
        self.eval_queries()
        self.log = []
        for i, query in enumerate(self.active_queries):
            self.log.append(query['category'] == self.query_ans[i])
        self.fill_amalkard()
        return self.log

class KNN(K_eval):
    
    def __init__(self, corpus, k=1, **kwargs):
        super().__init__(corpus, **kwargs)
        self.parameters['k'] = k

    def pre_build(self):
        self.corpus.build_vectors()
        self.corpus.build_np_vecs()

    def build_valid(self):
        #requries: corpus.build_vectors, corpus.build_np_vec
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
        limit = self.limit
        self.product = dist_cosine(self.q_matrix[self.q_start:self.q_end,:], self.corpus.np_vecs[:limit])

class KNN_euclid(KNN):
    
    def __init__(self, corpus, **kwargs):
        super().__init__(corpus, **kwargs)

    def fill_product_matrix(self):
        limit = self.limit
        self.product = dist_euclid(self.q_matrix[self.q_start:self.q_end,:], self.corpus.np_vecs[:limit])

class Naive_classifier(K_eval):

    def __init__(self, corpus, alpha=0.01, **kwargs):
        super().__init__(corpus, **kwargs)
        self.parameters['alpha'] = alpha

    def pre_build(self):
        self.corpus.build_vectors()
        self.corpus.build_naive()

    def build_valid(self):
        #assumes that corpus.build_vectors, build_naive has been called
        self.q_docs = []
        for query in self.active_queries:
            q_doc = self.corpus.doc_from_dict(query, is_query=True)
            self.q_docs.append(q_doc)

    def eval_queries(self):
        alpha = self.parameters['alpha']
        for i, q_doc in enumerate(self.q_docs):
            score = np.log(self.corpus.class_doc_count / self.corpus.class_doc_count.sum())
            for word in q_doc.word_iterator:
                word_score = np.log(
                        (self.corpus.number_of_occurences[word,:] + alpha) /
                        (self.corpus.class_total_occurences + alpha * len(self.corpus.word_to_num))
                        )
                score += word_score
            best = np.argmax(score)
            self.query_ans[i] = Doc.int_to_category(best)
