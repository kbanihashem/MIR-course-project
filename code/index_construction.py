import xml.etree.ElementTree as ET
import re
class Doc:
    persian_regex = '[^آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی ]+'

    def __init__(self, doc_id=None, title=None, text=None):
        self.doc_id = doc_id
        self.title = title
        self.text = text

    @property
    def info_iterator(self):

        for i, word in enumerate(self.title):
            yield (word, i + 1, 'title')

        for i, word in enumerate(self.text):
            yield (word, i + 1, 'text')

    @classmethod
    def create_list_from_xml(cls, xml, max_num=None, method='file'):

        if method == 'root':
            root = xml
        else:
            if method == 'file':
                tree = ET.parse(xml)
            elif method == 'string':
                pass
            elif method == 'root':
                tree = xml
            root = tree.getroot()

        li = []
        for i, doc_root in enumerate(root):
            print(i, ':', end=' ')
            if max_num is not None and i >= max_num:
                break
            li.append(cls.create_from_xml(doc_root, method='root'))
        return li

    @classmethod
    def create_from_xml(cls, xml, method='file'):

        if method == 'root':
            root = xml
        else:
            if method == 'file':
                tree = ET.parse(xml)
            elif method == 'string':
                pass
            elif method == 'root':
                tree = xml
            root = tree.getroot()

        doc_id = root[2].text
        title = Doc.clean_text(Doc.get_title(root))
        text = Doc.clean_text(Doc.get_text(root))
        return cls(doc_id, title, text)

    def __str__(self):
        ans = ""
        ans += "ID: %s\n" % self.doc_id
        ans += "Title: %s\n\n" % self.title
        ans += self.text
        return ans
    
    @staticmethod
    def get_field_number(root, name):
        for i, field in enumerate(root):
            if name in field.tag:
                return i
        return -1

    @staticmethod
    def get_title(root):
        i = Doc.get_field_number(root, 'title')
        if i == -1:
            print(1)
            return ''
        return root[i].text

    @staticmethod
    def get_text(root):
        i = Doc.get_field_number(root, 'revision')
        if i == -1:
            print(2)
            return ''
        root = root[i]

        i = Doc.get_field_number(root, 'text')
        if i == -1:
            print(3)
            return ''
        return root[i].text
    
    @staticmethod
    def clean_text(text):
        text = re.sub(Doc.persian_regex, ' ', text)
        text = re.sub('[ ]+', ' ', text)
        return text

    def __str__(self):
        ans = "Doc:\n"
        ans += "\ttitle: %s\n" % self.title
        ans += "\ttext: %s..." % self.text[:20].replace("\n", "\\n")
        return ans

    def __repr__(self):
        return str(self).replace("\n", "\\n").replace("\t", "\\t")
    
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
