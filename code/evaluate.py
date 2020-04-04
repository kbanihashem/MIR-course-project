import glob
from helper import Eval_calc
from index_construction import RetrievalIndex
class IREvaluator:

    funcs = {'F': Eval_calc.F,
            'MAP': Eval_calc.MAP,
            'R': Eval_calc.R_precision,
            'NDCG': Eval_calc.NDCG,
            }
    def __init__(self, retrieval_index=None,
            queries_path='../data/',
            query_nums=20):
        self.retrieval_index = retrieval_index
        self.queries_path = queries_path
        self.query_nums = query_nums

    def query_path(self, num='all'):
        return [self.queries_path + ("queries/%s.txt" % i) for i in (range(1, self.query_nums) if num == 'all' else [num])]

    def result_path(self, num='all'):
        return [self.queries_path + ("relevance/%s.txt" % i) for i in (range(1, self.query_nums) if num == 'all' else [num])]

    def q_and_res_path(self, num='all'):
        return zip(self.queries_path(num), self.result_path(num))

    def evaluate(self, query_id='all', metric='F', method='ltn-lnn'):
        scores = []
        for q, res in self.q_and_res_path(query_id):
            with open(q, 'r') as f:
                lines = f.read().split('\n')
                if len(lines) < 1:
                    raise ValueError('file has no lines')
                query_title = lines[0]
                if len(lines) > 1:
                    query_text = lines[1]
                else:
                    query_text = query_title
                top_k = self.retrieval_index.query(query_title, query_text, method)
            with open(res, 'r') as f:
                real_best = f.read().line().split()
            scores.append(IREvaluator.funcs[metric](real_best, top_k))
        
        assert len(scores) > 0
        return sum(scores)/ len(scores)
