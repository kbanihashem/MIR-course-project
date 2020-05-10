import json 
import numpy as np

import helper
from document import Doc

class Corpus:
    
    def __init__(self):
        self.word_to_num = dict()
        self.num_to_word = []
        self.docs = []
        self.num_categories = 4

    @classmethod
    def from_file(cls, path):
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def doc_from_dict(self, doc, is_query=False):
        document = Doc(
                self.process_text(doc['title'], is_query=is_query),
                self.process_text(doc['body'], is_query=is_query),
                doc['category'],
                )
        return document

    @classmethod
    def from_dict(cls, data):
        corpus = cls()
        for doc in data:
            document = corpus.doc_from_dict(doc)
            corpus.add_doc(document)
        return corpus

    def next_doc_id(self):
        return len(self.docs)

    def next_word_number(self):
        return len(self.word_to_num)

    def add_doc(self, document, set_id=True):
        if set_id:
            if document.doc_id is not None:
                raise Exception("doc_id already set")

            document.doc_id = self.next_doc_id()
        self.docs.append(document)

    def add_word(self, word):
        if word in self.word_to_num:
            return
        num = self.next_word_number()
        self.num_to_word.append(word)
        self.word_to_num[word] = num

    def process_text(self, text, nummify=True, add_words_to_list=True, is_query=False):
        tokenized = helper.tokenize(text)

        if is_query:
            vec = []
            for word in tokenized:
                if word in self.word_to_num:
                    vec.append(self.word_to_num[word])
            return vec
        else:
            for word in tokenized:
                self.add_word(word)
           
            if not nummify:
                return 

            return self.nummify(tokenized)
        
    def nummify(self, words):
        return list(map(lambda word: self.word_to_num[word], words))

    def build_idf(self):
        self.df = [0] * len(self.word_to_num)
        for i, doc in enumerate(self.docs):
            distinct_words = set(doc.word_iterator)
            for word_num in distinct_words:
                self.df[word_num] += 1

        N = len(self.docs)
        self.idf = list(map(lambda df: np.log(N / df), self.df))

    def get_vector(self, doc):
        vec = dict()
        for word_num in doc.word_iterator:
            vec.setdefault(word_num, 0)
            vec[word_num] += 1
        for word_num in vec:
            vec[word_num] *= self.idf[word_num]
        return vec
    
    def clear_vectors(self):
        del self.df
        del self.idf
        del self.vecs
        del self.l2

    def build_vectors(self):
        self.build_idf()
        self.vecs = [dict() for _ in range(len(self.docs))]
        self.l2 = [None for _ in range(len(self.docs))]
        for i, doc in enumerate(self.docs):
            self.vecs[i] = self.get_vector(doc)
            self.l2[i] = helper.l2_norm(self.vecs[i])

    def build_naive(self):
        self.number_of_occurences = np.zeros((len(self.word_to_num), self.num_categories), dtype=np.int64)
        self.class_doc_count = np.zeros(self.num_categories, dtype=np.int64)
        for doc in self.docs:
            for word in doc.word_iterator:
                self.number_of_occurences[word, doc.int_category] += 1
            self.class_doc_count[doc.int_category] += 1
        self.class_total_occurences = self.number_of_occurences.sum(axis=0)

    def clear_naive(self):
        del self.number_of_occurences
        del self.class_total_occurences
        #TODO: check again

