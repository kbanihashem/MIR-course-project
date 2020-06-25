import json
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch import helpers
INDEX_NAME = 'paper_index'

def del_index(es, index_name):
    es.indices.delete(index_name)

def create_empty_index(es, index_name):
    es.indices.create(index_name)

def add_fields(data, index_name=INDEX_NAME):
    return [
            {
                '_index': index_name,
                '_id': d['id'],
                '_source': {'paper': d},
                } for i, d in enumerate(data)
            ]
        
def add_data(es, path='data/quotes.json', index_name=INDEX_NAME):
    with open(path, 'r') as f:
        data = json.load(f)

    data = add_fields(data, index_name)
    helpers.bulk(es, data)

def get_all_ids(es, index_name=INDEX_NAME):
    scroll = helpers.scan(es, query={"_source":False, "query":{"match_all": {}}}, index=index_name, scroll='10s')
    return list(map(lambda e: e['_id'], scroll))

def get_neighbors(es, doc_id, index_name=INDEX_NAME):
    return list(map(lambda link: link.split('/')[-1], es.get(index=index_name, id=doc_id)['_source']['paper']['references'])) 

def build_graph(es, doc_ids, index_name=INDEX_NAME, alpha=0.9):
    id_to_i = {doc_id: i for i, doc_id in enumerate(doc_ids)}
    n = len(doc_ids)
    P = np.zeros((n, n))
    v = np.ones(n)/n
    for i, doc_id in enumerate(doc_ids):
        neighbor_is = [id_to_i[neighbor] for neighbor in get_neighbors(es, doc_id, index_name) if neighbor in id_to_i]
        if neighbor_is == []:
            P[i,:] = v
        else:
            for j in neighbor_is:
                P[i, j] += 1/len(neighbor_is)
            P[i,:] *= (1 - alpha)
            P[i,:] += alpha * v
    return P

def get_pagerank(P):
    eigenvalues, eigenvectors = np.linalg.eig(P.T)
    v = np.real(eigenvectors.T[np.argmax(eigenvalues)])
    return v/v.sum()

def add_doc_field(es, doc_id, field_name, field_value, index_name=INDEX_NAME):
    es.update(INDEX_NAME, doc_id, {"script":{"source":f"ctx._source.paper.{field_name} = params.value", "params": {"value": field_value}}})

def add_pagerank(es, index_name=INDEX_NAME, alpha=0.1):
    doc_ids = get_all_ids(es, index_name)
    P = build_graph(es, doc_ids, index_name, alpha)
    v = get_pagerank(P)
    pagerank_by_id = {doc_id:v[i] for i, doc_id in enumerate(doc_ids)}
    min_page_rank = min(pagerank_by_id.values())
    max_page_rank = max(pagerank_by_id.values())
    pagerank_by_id = {doc_id: (v - min_page_rank) / (max_page_rank - min_page_rank) for doc_id, v in pagerank_by_id.items()}
    es.update_by_query(INDEX_NAME, {"script":{"source":"ctx._source.paper.page_rank = params.pagerank[ctx._id]", "params": {"pagerank": pagerank_by_id}}})

#https://www.elastic.co/guide/en/elasticsearch/guide/current/query-time-boosting.html
def query(es, q_title, q_abstract, q_year, use_page_rank=False, w_title=1, w_abstract=1, w_year=1, w_page_rank=1, index_name=INDEX_NAME):
    query = {
            'query': {
                'bool': {
                    'should': [
                        {
                            'match': {
                                'paper.title': {
                                    'query': q_title,
                                    'boost': w_title,
                                    }
                                }
                            },
                        {
                            'match': {
                                'paper.abstract': {
                                    'query': q_abstract,
                                    'boost': w_abstract,
                                    }
                                }
                            },
                        {
                            'range': {
                                'paper.date': {
                                    'gte': q_year,
                                    'boost': w_year,
                                    }
                                }
                            },
                        ]
                    }
                }
            }
    #es.search({'query': {'script_score': {'query': {'match_all': {}}, 'script': {'source': 'saturation(doc["paper.page_rank"].value, 1)'}}}}, INDEX _NAME)
    number_of_docs = 2000
    if use_page_rank:
        query['query']['bool']['should'].append(
                {
                    'script_score': {
                        'query': {'match_all': {}},
                        'script': {
                            'source': 'saturation(doc["paper.page_rank"].value, 1)',
                            },
                        'boost': w_page_rank,
                        },
                    }
                )
    return es.search(query, index_name, size=10)['hits']['hits']

def get_author_graph(es, index_name=INDEX_NAME):
    doc_ids = get_all_ids(es)
    docs = dict()
    neighbors = dict()
    for i, doc_id in enumerate(doc_ids):
        docs[doc_id] = es.get(index_name, doc_id)['_source']['paper']
        neighbors[doc_id] = set(list(map(lambda link: link.split('/')[-1], docs[doc_id]['references'])))
    adj = dict()
    for doc_id, doc in docs.items():
        for author in doc['authors']:
            a = author.lower()
            adj[a] = []
            for neighbor in map(lambda x: docs.get(x), neighbors[doc_id]):
                #not in database case
                if neighbor is None:
                    continue
                for other in neighbor['authors']:
                    b = other.lower()
                    adj[a].append(b)
    return adj

def calc_hits(es, top_k=10, index_name=INDEX_NAME, repeat_count=5):
    doc_ids = get_all_ids(es)
    author_graph = get_author_graph(es, index_name)
    i_to_author = list(author_graph)
    author_to_i = {author: i for i, author in enumerate(author_graph)}
    n = len(i_to_author)
    adj = [[] for _ in range(n)]
    for i, author in enumerate(i_to_author):
        for j in map(lambda x: author_to_i[x], author_graph[author]):
            adj[i].append(j)
    a = np.ones(n)
    h = np.ones(n)
    li = []
    all_edges = [(i, j) for i in range(n) for j in adj[i]]
    for repeat in range(repeat_count):
        new_a = np.zeros(n)
        new_h = np.zeros(n)
        for i ,j in all_edges:
            new_h[i] += a[j]
            new_a[j] += h[i]
        
        a = new_a
        h = new_h
        a *= n / a.sum()
        h *= n / h.sum()
        li.append((a, h))
    top_author_index = np.argsort(-a)[:top_k]
    return list(map(lambda i: i_to_author[i], top_author_index))

#es.update_by_query(INDEX_NAME, {"script":{"source":"ctx._source.paper.hasan = params.count[ctx._id]", "params": {"count": kiarash}}})

