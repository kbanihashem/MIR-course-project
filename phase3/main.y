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
    es.update_by_query(INDEX_NAME, {"script":{"source":"ctx._source.paper.page_rank = params.pagerank[ctx._id]", "params": {"pagerank": pagerank_by_id}}})

#https://www.elastic.co/guide/en/elasticsearch/guide/current/query-time-boosting.html
def query(es, q_title, q_abstract, q_year, use_page_rank=False, w_title=1, w_abstract=1, w_year=1, index_name=INDEX_NAME):
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
    number_of_docs = 2000
    if use_page_rank:
        query['query']['bool']['should'].append(
                {
                    'rank_feature': {
                        'field': 'page_rank',
                        'log': {
                            'scaling_factor': 0
                            },
                        'boost': 10,
                        }
                    }
                )
    return es.search(query, INDEX_NAME, size=10)['hits']['hits']

#es.update_by_query(INDEX_NAME, {"script":{"source":"ctx._source.paper.hasan = params.count[ctx._id]", "params": {"count": kiarash}}})

