import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

def remove_stopwords(tokens):
    english_stopwords = set(stopwords.words('english'))
    return [word for word in tokens if word not in english_stopwords]

def dist_euclid(x, y):
    xy = np.dot(x, y.T)
    x2 = np.sum(x**2, axis=1)
    y2 = np.sum(y**2, axis=1)
    return -2 * xy + x2[:,None] + y2

def dist_cosine(x, y, l2=1):
    return -x.dot(y.T) / l2

def k_stemm(tokens):
    stemmer = PorterStemmer()
    return list(map(stemmer.stem, tokens))

def k_lemm(tokens):
    lemmatizer = WordNetLemmatizer() 
    return list(map(lemmatizer.lemmatize, tokens))

def tokenize(text, pipeline):
    punctuation_list = ":,.?!*/'\\\""
    for c in punctuation_list:
        text = text.replace(c, ' ')
    tokenized = text.split()

    for func in pipeline:
        tokenized = func(tokenized)

    return tokenized

def vec_dot(v1, v2):
    prod = sum(v2.get(word, 0) * v1.get(word, 0) for word in v1)
    return prod

def l2_norm(v):
    return np.sqrt(vec_dot(v, v))

def cosine(v1, v2):
    return -vec_dot(v1, v2) #/ l2_norm(v1) / l2_norm(v2)

def euclidean(v1, v2):
    diff = dict()
    
    for word in v1:
        diff.setdefault(word, 0)
        diff[word] += v1[word]

    for word in v2:
        diff.setdefault(word, 0)
        diff[word] -= v2[word]

    return l2_norm(diff)

def most_repeated(li):
    count_dict = dict()
    for x in li:
        count_dict.setdefault(x, 0)
        count_dict[x] += 1

    return max(count_dict.keys(), key=lambda x: count_dict[x])

def sparse_to_numpy(li, keys):
    m = len(li)
    n = len(keys)
    ans = np.zeros((m, n))
    for i in range(m):
        ans[i] = np.zeros(n)
        for word in li[i]:
            ans[i][word] = li[i][word]
#        ans[i] = np.array(list(map(lambda j: li[i].get(j, 0), range(n))), dtype=np.float16)
    return ans

