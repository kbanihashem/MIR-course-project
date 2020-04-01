import xml.etree.ElementTree as ET
import re
from collections import Counter
import numpy as np

class Doc:
    persian_regex = '[^آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی ]+'

    def __init__(self, doc_id=None, title=None, text=None):
        self.doc_id = doc_id
        self.title = title
        self.text = text
        self._bag_of_words = None

    @property
    def bag_of_words(self):
        if self._bag_of_words is not None:
            self._bag_of_words = Counter(self.info_iterator)
        return self._bag_of_words

    @property
    def distinct_terms(self):
        return self.bag_of_words.keys()
        
    @property
    def info_iterator(self):
        """returns word_pos_part"""
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
            #print(i, ':', end=' ')
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
    
    def tf_idf(self, method):
        v = dict()
        for word, count in self.bag_of_words:
            v[word] = Doc.transform_tf(count, method[0]) 

        if method[3] == 'n':
            const = 1
        elif method[3] == 'c':
            const = np.sqrt(sum(map(lambda x: x**2, v.values())))
        return v, const

    @staticmethod
    def transform_tf(tf, method='l'):
        methods_supported = "l"
        if method not in methods_supported:
            raise ValueError("method should be in '%s'" % methods_supported)

        if method == 'l':
            return 1 + np.log(tf) if tf > 0 else 0
