import json 
import numpy as np

import helper
from document import Doc

class Corpus:
    
    def __init__(self):
        self.word_to_num = dict()
        self.num_to_word = []
        self.docs = []

    @classmethod
    def from_file(cls, path):
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data):
        corpus = cls()
        for doc in data:
            document = Doc(
                    corpus.process(doc['title']),
                    corpus.process(doc['body']),
                    doc['category'],
                    )
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

    def process_query(self, text):
        tokenized = helper.tokenize(text)
        vec = []
        for word in tokenized:
            if word in self.word_to_num:
                vec.append(self.word_to_num[word])
        return vec

    def process(self, text, nummify=True, add_words_to_list=True):
        tokenized = helper.tokenize(text)
        for word in tokenized:
            self.add_word(word)
       
        if not nummify:
            return 

        return self.nummify(tokenized)
        
    def nummify(self, words):
        return list(map(lambda word: self.word_to_num[word], words))

    def build_vectors(self):
        self.vecs = [dict() for _ in range(len(self.docs))]
        self.df = [0] * len(self.word_to_num)
        for i, doc in enumerate(self.docs):
            for word_num in doc.word_iterator:
                self.vecs[i].setdefault(word_num, 0)
                self.vecs[i][word_num] += 1
            distinct_words = self.vecs[i].keys()
            for word_num in distinct_words:
                self.df[word_num] += 1

        N = len(self.docs)
        self.idf = list(map(lambda df: np.log(N / df), self.df))
        for i, doc in enumerate(self.docs):
            for word_num in self.vecs[i]:
                self.vecs[i][word_num] *= self.idf[word_num]
