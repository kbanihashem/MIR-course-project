import xml.etree.ElementTree as ET
import re
class RetrievalIndex:

    def __init__(self):
        self.docs = dict()
        self.index = dict()

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


    def get_posting_list(self, word):
        return self.index.setdefault(word, {})

    @classmethod
    def construct_from_wiki(cls, xml):
        tree = ET.parse(xml)


    def __str__(self):
        ans = ""
        ans += "Doc_ids: %s\n" % str(list(self.docs))
        ans += '+++++++++++++++++++++\n'
        ans += "Index: %s\n" % '\n------------\n'.join("%s: %s" % (word, self.index[word]) for word in self.index)
        return ans

def main():
    test4()

def test4():
    doc = Doc.create_from_xml_file('test_doc.xml')
    print(doc)

def test3():
    docs = test_docs()
    index = RetrievalIndex()
    print('empty index')
    print(index)
    print('adding')
    for doc in docs:
        index.add_doc(doc)
        print(index)
    print('removing')
    for doc in docs:
        index.remove_doc(doc)
        print(index)

def test_docs():
    doc1 = Doc(doc_id=9, title=['kiarash', 'banihashem'], text=['allo', 'hello', 'bye'])
    doc2 = Doc(doc_id=10, title=['joan'], text=['kiarash', 'Mate'])
    return [doc1, doc2]

def test2():
    doc1, doc2 = test_docs()
    for x in doc1.info_iterator:
        print(x)

def test1():
    #testing get_posting_list
    index = RetrievalIndex()
    doc = Doc(doc_id=9, title=['kiarash', 'banihashem'], text=['allo', 'hello', 'bye'])
    index.add_doc(doc)
    doc = Doc(doc_id=10, title=['joan'], text=['kiarash', 'Mate'])
    index.add_doc(doc)
    print(index.get_posting_list('kiarash')) 
    print(index.get_posting_list('joan')) 
    print(index.get_posting_list('allo')) 
    print(index.get_posting_list('hasan'))

if __name__ == '__main__':
    main()
