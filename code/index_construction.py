import xml.etree.ElementTree as ET
import re
import numpy as np

from document import Doc
from helper import Tf_calc

class RetrievalIndex:

    def __init__(self):
        self.docs = dict()
        self.index = dict()
        self.vecs = None
        self.consts = None

    @classmethod
    def from_xml(cls, xml, max_num=None, method='file'):
        index = cls()
        for doc in Doc.create_list_from_xml(xml, max_num=max_num, method=method):
            index.add_doc(doc)
        return index

    def add_doc(self, doc, raise_on_exists=True):
        doc_id = doc.doc_id

        if doc_id in self.docs:
            if raise_on_exists:
                raise ValueError("Doc already in list, change id")
            else:
                return

        self.docs[doc_id] = doc
        for word, position, doc_part in doc.info_iterator:
            self.word_index_add_doc(word, position, doc_id, doc_part)

    def remove_doc(self, doc_id, raise_on_not_exists=True):

        if doc_id not in self.docs:
            if raise_on_not_exists:
                raise ValueError("doc_id not found")
            else:
                return

        doc = self.docs[doc_id]
        for word, position, doc_part in doc.info_iterator:
            self.word_index_remove_doc(word, doc_id)
        del self.docs[doc_id]

    def word_index_add_doc(self, word, position, doc_id, doc_part):
        self.index.setdefault(word, {}).setdefault(doc_id, {}).setdefault(doc_part, []).append(position)

    #assumes no Attack
    def word_index_remove_doc(self, word, doc_id, raise_on_not_exists=False):

        posting_list = self.get_posting_list(word, raise_on_not_exists=raise_on_not_exists)
        if doc_id not in posting_list:
            if raise_on_not_exists:
                raise ValueError("Doc %s not in posting list for word %s" % (doc_id, word))
            return

        del posting_list[doc_id]
        if not posting_list:
            del self.index[word]

    def get_posting_list(self, word, raise_on_not_exists=True):

        if raise_on_not_exists and word not in self.index:
            raise ValueError('term not in index')

        return self.index.get(word, {})

    def tf(self, term, doc_id, part, method='l'):

        posting_list = self.get_posting_list(term)
        tf = len(posting_list.get(doc_id, {}).get(part, {}))
        
        return Tf_calc.transform_tf(tf, method)

    def idf(self, term, part, method='n'):

        methods_supported = 'ntp'
        if method not in methods_supported:
            raise ValueError('method shoud be in "%s"', methods_supported)

        if method == 'n':
            return 1

        df = len(self.get_posting_list(term))
        return Tf_calc.idf_transform(df, method=method, N=self.N)

    def tf_idf(self, term, doc_id, part, method='ln'):
        return self.tf(term, doc_id, part, method=method[0]) * self.idf(term, part, method=method[1])

    def query(self, query_title, query_text, method='ltn-lnn', k=15, flatten=True):

        query = Doc.from_query(query_title, query_text)

        self.make_vectors(method[:3])
        v, const = query.tf_idf(method[4:])
        scores = []
        for doc_id, vec in self.vecs.items():
            score = 0
            for term, w_q in v.items():
                score += vec.get(term, 0) * w_q
            scores.append((doc_id, score / const / self.consts[doc_id]))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_k = [scores[i][0] for i in range(min(k, len(scores)))]
        if k == 1 and flatten:
            return top_k[0]
        else:
            return top_k

    def make_vectors(self, method='lnn'):
        self.vecs = {}
        self.consts = {}
        for doc_id, doc in self.docs.items():
            v = dict()
            for term in doc.distinct_terms:
                v[term] = self.tf_idf(term, doc_id, method=method[:2]) 

            self.vecs[doc_id] = v
            self.consts[doc_id] = Tf_calc.const(v, method[2])

    @property
    def N(self):
        return len(self.docs)

    def __str__(self):
        ans = ""
        ans += "Doc_ids: %s\n" % str(list(self.docs))
        ans += '+++++++++++++++++++++\n'
        ans += "Index: %s\n" % '\n------------\n'.join("%s: %s" % (word, self.index[word]) for word in self.index)
        return ans

