import xml.etree.ElementTree as ET
import re
import numpy as np

from document import Doc

class RetrievalIndex:

    def __init__(self):
        self.docs = dict()
        self.index = dict()
        self.vecs = None
        self.consts = None

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

    def remove_doc(self, doc=None, doc_id=None, raise_on_not_exists=True):
        doc_id = doc.doc_id if doc is not None else doc_id
        if doc_id is None:
            raise ValueError("enter doc or doc_id!")

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
    def word_index_remove_doc(self, word, doc_id):
        if word not in self.index:
            return

        posting_list = self.index[word]
        if doc_id not in posting_list:
            return

        del posting_list[doc_id]
        if not posting_list:
            del self.index[word]

    def tf(self, term, doc_id, method='l'):
        methods_supported = 'l'
        if method not in methods_supported:
            raise ValueError('method shoud be in "%s"', methods_supported)
        posting_list = self.get_posting_list(term)

        if doc_id not in posting_list:
            tf = 0
        else:
            li = posting_list[doc_id]
            tf = sum(len(li[part]) for part in li)
        
        if method == 'l':
            return 1 + np.log(tf) if tf > 0 else 0

    def idf(self, term, method='n'):

        methods_supported = 'ntp'
        if method not in methods_supported:
            raise ValueError('method shoud be in "%s"', methods_supported)

        if method == 'n':
            return 1

        df = len(self.get_posting_list(term))

        if method == 't':
            return np.log(self.N/df)

        if method == 'p':
            return max(0, np.log((self.N - df)/df))

    def tf_idf(self, term, doc_id, method='ln'):
        return self.tf(term, doc_id, method=method[0]) * self.idf(term, method=method[1])

    def get_posting_list(self, word, raise_on_not_exists=True):

        if raise_on_not_exists and word not in self.index:
            raise ValueError('term not in index')

        return self.index.getdefault(word, {})

    def make_vectors(self, method='lnn'):
        for doc_id, doc in self.docs.items():
            v = dict()
            for term in doc.distinct_terms:
                v[term] = self.tf_idf(term, doc_id, method=method[:2]) 
            if method[2] == 'n':
                normalization_factor = 1
            if method[2] == 'c':
                normalization_factor = np.sqrt(sum(map(lambda x: x**2, v.values())))

            self.vecs[doc_id] = v
            self.consts[doc_id] = normalization_factor
            

    @classmethod
    def construct_from_wiki(cls, xml):
        tree = ET.parse(xml)

    @property
    def N(self):
        return len(self.docs)

    def __str__(self):
        ans = ""
        ans += "Doc_ids: %s\n" % str(list(self.docs))
        ans += '+++++++++++++++++++++\n'
        ans += "Index: %s\n" % '\n------------\n'.join("%s: %s" % (word, self.index[word]) for word in self.index)
        return ans

