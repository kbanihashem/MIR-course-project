from itertools import chain
class Doc:

    def __init__(self, title, body, category=0, doc_id=None):
        self.title = title
        self.body = body
        self.category = category
        self.doc_id = doc_id

    @classmethod
    def from_dict(cls, doc):
        return self(doc['title'], doc['body'], doc['category'])
    
    @property
    def word_iterator(self):
        return chain(self.title, self.body)

    @property
    def int_category(self):
        return int(self.category) - 1

    @staticmethod
    def int_to_category(c):
        return c + 1
