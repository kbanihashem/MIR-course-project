import numpy as np
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

from k_eval import K_eval
from helper import sparse_to_numpy

class SKLearn_Classifier(K_eval):
    def __init__(self, corpus, **kwargs):
        super().__init__(corpus, **kwargs)
        self.corpus_limit = len(self.corpus.docs)

    def pre_build(self):
        self.corpus.build_vectors()
        self.corpus.build_np_vecs()
        self.fit_corpus()

    def build_model(self):
        pass

    def fit_corpus(self):
        X = self.corpus.np_vecs[:self.corpus_limit]
        y = self.corpus.y_vec[:self.corpus_limit]
        self.build_model()
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

class SVM(SKLearn_Classifier):

    def __init__(self, corpus, C=1, **kwargs):
        super().__init__(corpus, **kwargs)
        self.parameters['C'] = C

    def build_model(self):
        self.model = LinearSVC(random_state=0, tol=1e-5, C=self.parameters['C'])

class Forest(SKLearn_Classifier):
    def __init__(self, corpus, tree_count=100, max_depth=None, **kwargs):
        super().__init__(corpus, **kwargs)
        self.parameters['tree_count'] = tree_count
        self.parameters['max_depth'] = max_depth

    def build_model(self):
        self.model = RandomForestClassifier(n_estimators=self.parameters['tree_count'], max_depth=self.parameters['max_depth'], random_state=0)
