import numpy as np
from sklearn.svm import LinearSVC

from k_eval import K_eval
from helper import sparse_to_numpy

class SVM(K_eval):

    def __init__(self, corpus, C=1, **kwargs):
        super().__init__(corpus, **kwargs)
        self.parameters['C'] = C
        self.corpus_limit = len(self.corpus.docs)

    def pre_build(self):
        self.corpus.build_vectors()
        self.corpus.build_np_vecs()
        self.fit_corpus()

    def fit_corpus(self):
        X = self.corpus.np_vecs[:self.corpus_limit]
        y = self.corpus.y_vec[:self.corpus_limit]
        self.model = LinearSVC(random_state=0, tol=1e-5, C=self.parameters['C'])
        self.model.fit(X, y)
    
    def build_valid(self):
        li = []
        y_s = []
        for query in self.active_queries:
            q_doc = self.corpus.doc_from_dict(query, is_query=True)
            q_vec = self.corpus.get_vector(q_doc)
            pred = q_doc.int_category

            li.append(q_vec)
            y_s.append(pred)

        self.q_matrix = sparse_to_numpy(li, self.corpus.word_to_num.keys())
        self.q_ys = np.array(y_s, dtype=np.int64)

    def eval_queries(self):
        self.query_ans = self.model.predict(self.q_matrix) + 1
