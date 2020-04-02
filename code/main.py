from document import Doc
from index_construction import RetrievalIndex

XML_PATH = '../data/Persian.xml'
INDEX_PATH = 'IR_INDEX.dat'

def main():
    test8()

def test8():
    index = RetrievalIndex.load(INDEX_PATH)
    index.make_vectors('lnn')
    return
    query_title = 'مسابقات فوتبال المپیک'
    query_text = query_title
    q = index.query(query_title, query_text, k=10)
    print(q)

def test7():
    index = RetrievalIndex.from_xml(XML_PATH, max_num=None)
    index.save(INDEX_PATH)

def test6():
    document = Doc.create_from_xml('test_doc.xml')
    print(document)

def test5():
    index = RetrievalIndex.from_xml(XML_PATH, max_num=None)
    query_title = 'مسابقات فوتبال المپیک'
    query_text = query_title
    q = index.query(query_title, query_text, k=10)
    print(q)
    
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
