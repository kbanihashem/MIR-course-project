import numpy as np
from typing import List, Dict

from corpus import Corpus
from k_eval import Naive_classifier
from helper import k_stemm, k_lemm, remove_stopwords

corpus=None
def train(training_docs: List[Dict]):
    global corpus
    corpus = Corpus.from_dict(training_docs, pipeline=[remove_stopwords, k_lemm])
    corpus.build_vectors()
    corpus.build_naive()

def classify(doc: Dict) -> int:
    bayes = Naive_classifier(corpus, alpha=0.3)
    doc['category'] = 1
    bayes.set_singular_valid(doc)
    bayes.query_ans = [None]
    bayes.eval_queries()
    return bayes.query_ans[0]

