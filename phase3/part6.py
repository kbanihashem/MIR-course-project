import numpy as np
from sklearn.svm import LinearSVC
from time import time
from sklearn.metrics import ndcg_score

train_path = 'data/train.txt'
valid_path = 'data/vali.txt'
test_path = 'data/test.txt'

def query_and_rank(line):
    li = line.split()
    rank = int(li[0])
    vector = np.array(list(map(lambda x: float(x.split(':')[1]), li[2:48])))
    query_id = li[1].split(':')[1]
    return query_id, vector, rank

def get_dict(train):
    train_dict = dict()
    for q_id, v, r in train:
        if q_id not in train_dict:
            train_dict[q_id] = []
        train_dict[q_id].append((v, r))
    return train_dict

with open(train_path, 'r') as f:
    train = [query_and_rank(line.rstrip()) for line in f]
    train_dict = get_dict(train)

with open(valid_path, 'r') as f:
    valid = [query_and_rank(line.rstrip()) for line in f]
    valid_dict = get_dict(valid)

svm_X = []
svm_y = []
count = 0
limit = 10000
for li in train_dict.values():
    for di, qi in li:
        for dj, qj in li:
            count += 1
            if limit is not None and count > limit:
                break
            if qi == qj:
                continue
            v = di - dj
            y = 1 if qi > qj else 0
            svm_X.append(v)
            svm_y.append(y)

def get_dcg(ordering, values, ndcg_limit=5):
    total = 0
    for i, ith_guess in enumerate(ordering[:ndcg_limit]):
        dicsount_factor = 1 if i == 0 else np.log2(i + 1)
        total += values[ith_guess] / dicsount_factor
#    for i, ith_guess in enumerate(ordering[:ndcg_limit]):
#        dicsount_factor = 1 if i == 0 else np.log2(i + 1)
#        dicsount_factor = np.log2(i + 2)
#        total += (2**values[ith_guess] - 1) / dicsount_factor
    return total

t0 = time()
possible_Cs = 10**np.linspace(-3, 0, 4)

def eval_C(C=1):
    clf = LinearSVC(random_state=0, C=C, tol=1e-5)
    clf.fit(svm_X, svm_y)
    t1 = time()
#    print(limit, t1 - t0)
    w = clf.coef_.reshape((-1,))
    mean_vals = np.array([np.mean([w @ v for q_id, v, r in train if r == i]) for i in range(3)])
    ndcg = []
    for q_id, li in valid_dict.items():
        truth = []
        dot_prods = []
        for doc, rank in li:
            dot_prods.append(w @ doc)
            truth.append(rank)

        dot_prods = np.array(dot_prods)
        #dot_prods = np.random.rand(len(dot_prods))
        truth = np.array(truth)

        our_ordering = np.argsort(-dot_prods)
        best_ordering = np.argsort(-truth)
        our_score = get_dcg(our_ordering, truth)
        best_score = get_dcg(best_ordering, truth) 
        if best_score > 1e-2:
            frac = our_score / best_score
            ndcg.append(frac) 

    ndcg = np.array(ndcg)
    return np.mean(ndcg)

results = []
for C in possible_Cs:
    results.append(eval_C(C))
    print(f'C={C}, average ndcg: {results[-1]}')
best_C = possible_Cs[np.argmin(results)]

with open(test_path, 'r') as f:
    valid = [query_and_rank(line.rstrip()) for line in f]
    valid_dict = get_dict(valid)
print(f'results on test: {eval_C(best_C)}')
