import xml.etree.ElementTree as ET
import re
import numpy as np
import pickle

from document import Doc
from helper import Tf_calc, EPSILON, Text_cleaner

class RetrievalIndex:

    def __init__(self):
        self.docs = dict()
        self.index = dict()
        self.vecs = None
        self.consts = None
        self.modified = {'ltn':True, 'ltc': True}
        self.cached_vectors = {'ltn': None, 'ltc': None}
        self.cached_consts = {'ltn': None, 'ltc': None}

    def save(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, file_path):
        with open(file_path, 'rb') as f:
            index = pickle.load(f)
        return index

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d

    @classmethod
    def from_xml(cls, xml, max_num=None, method='file'):
        index = cls()
        for doc in Doc.create_list_from_xml(xml, max_num=max_num, method=method):
            index.add_doc(doc)
        return index

    def add_doc(self, doc, raise_on_exists=True):

        self.set_modified()
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

        self.set_modified()
        self.modified = True
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

    def get_exact_docs(self, li_title, li_text, method="standard"):

        if method == "standard":
            li = li_text
            def is_fine(doc_id):
                return all(self.docs[doc_id].has_exact(phrase) for phrase in li)
        else:
            raise ValueError("method must be standard")

        ans = list(filter(is_fine, self.docs.keys()))
        return ans

    def query(self, query_title, query_text, method='ltn-lnn', k=15, title_ratio=2, flatten=True, exact_method="standard"):

        query_title, li_title = Text_cleaner.query_cleaner(query_title)
        query_text, li_text = Text_cleaner.query_cleaner(query_text)

        query = Doc.from_query(query_title, query_text)

        good_doc_ids = self.get_exact_docs(li_title, li_text, exact_method)

        self.make_vectors(method[:3])
        v, const = query.tf_idf(method[4:])
        scores = []
        for doc_id, doc_v in self.vecs.items():
            if doc_id not in good_doc_ids:
                continue
            part_score = dict()
            for part, part_vec in doc_v.items():
                part_score[part] = 0
                for term, w_q in v[part].items():
                    part_score[part] += part_vec.get(term, 0) * w_q
                normalization_factor = self.consts[doc_id][part] * const[part] + EPSILON
#                if normalization_factor < 1e-6:
#                    part_score[part] = 0
#                else:
#                    part_score[part] /= normalization_factor
                part_score[part] /= normalization_factor
            final_score = part_score['title'] * title_ratio + part_score['text']
            scores.append((doc_id, final_score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_k = [scores[i][0] for i in range(min(k, len(scores)))]
        if k == 1 and flatten:
            return top_k[0]
        else:
            return top_k

    def make_vectors(self, method='ltn'):

        if not self.modified[method]:
            self.vecs = self.cached_vectors[method]
            self.consts = self.cached_consts[method]
            return

        self.vecs = {}
        self.consts = {}
        for doc_id, doc in self.docs.items():
            self.vecs[doc_id] = {}
            self.consts[doc_id] = {}
            for part in Doc.PARTS:
                v = dict()
                for term in doc.distinct_terms(part):
                    v[term] = self.tf_idf(term, doc_id, part, method=method[:2]) 
    
                self.vecs[doc_id][part] = v
                self.consts[doc_id][part] = Tf_calc.const(v, method[2])

        self.cached_vectors[method] = self.vecs
        self.cached_consts[method] = self.consts
        self.modified[method] = False

    def set_modified(self):
        for method in self.modified:
            self.modified[method] = True

    @property
    def N(self):
        return len(self.docs)

    def __str__(self):
        ans = ""
        ans += "Doc_ids: %s\n" % str(list(self.docs))
        ans += '+++++++++++++++++++++\n'
        ans += "Index: %s\n" % '\n------------\n'.join("%s: %s" % (word, self.index[word]) for word in self.index)
        return ans

