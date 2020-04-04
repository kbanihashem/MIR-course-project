from hazm import Normalizer, word_tokenize, Stemmer
import re
import numpy as np

EPSILON = 1e-7
class Tf_calc:
    def transform_tf(tf, method='l'):
    
        methods_supported = "l"
        if method not in methods_supported:
            raise ValueError("method should be in '%s'" % methods_supported)
    
        if method == 'l':
            return 1 + np.log(tf) if tf > 0 else 0

    def const(v, method='n'):
        methods_supported = "nc"
        if method not in methods_supported:
            raise ValueError("method should be in '%s'" % methods_supported)

        if method == 'n':
            return 1

        if method == 'c':
            return np.sqrt(sum(map(lambda x: x**2, v.values())))

    def idf_transform(df, method='n', N=1):
        methods_supported = "ntp"
        if method not in methods_supported:
            raise ValueError("method should be in '%s'" % methods_supported)

        if method == 'n':
            return 1

        if method == 't':
            return np.log(N/df)

        if method == 'p':
            return max(0, np.log((N - df)/df))
        

class Text_cleaner:

    persian_regex = "[^آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی abcdefghijklmnopqrstuvwxyz]+" 

    @staticmethod
    def clean_and_prepare_text(text):
        cleaned = Text_cleaner.clean_text(text)
        prepared = Text_cleaner.prepare_text(cleaned)
        return prepared

    @staticmethod
    def clean_text(text):
        text = text.lower()
        text = re.sub(Text_cleaner.persian_regex, ' ', text)
        text = re.sub('[ ]+', ' ', text)
        normalizer = Normalizer()
        text = normalizer.normalize(text)
        tokenized = word_tokenize(text)
        return tokenized
    
    @staticmethod
    def prepare_text(tokenized):    
        #نگارشی
        punc_list = '.،؟!؛'
        def fix_word(w):
            for c in punc_list:
                w = w.replace(c, '')
            return "$" if w == "" else w
        
        punc_free = filter(lambda x: x != '$', map(fix_word, tokenized))
        stemmer = Stemmer()
        stemmed_list = list(filter(lambda x: x != '', map(stemmer.stem, punc_free)))
        
        return stemmed_list

    @staticmethod
    def query_cleaner(query):
        query = query.replace("'", '"')
        li = query.split('"')
        real_query = ''.join(li[i] for i in range(len(li)) if i % 2 == 0)
        real_query = re.sub('[ ]+', ' ', real_query)
        exact = [li[i] for i in range(len(li)) if i % 2 == 1]
        return real_query, exact

class Eval_calc:

    @staticmethod 
    def MAP(truth, out):
        truth = set(truth)
        total_precisions = 0
        releavent = 0
        for i, doc in enumerate(out):
            if doc in truth:
                releavent += 1
                total_precisions += releavent / (i + 1) 
        return total_precisions / len(truth)

    @staticmethod 
    def F(truth, out):
        truth = set(truth)
        out = set(out)
        
        tp = len(set.intersection(truth, out))
        precision = tp / len(out)
        recall = tp / len(truth)
        if precision + recall == 0:
            return 0

        return 2 * precision * recall / (precision + recall)

    @staticmethod 
    def R_precision(truth, out):
        rel = len(truth)
        out = out[:rel]
        tp = len(set(out).intersection(truth))
        return tp / rel

    @staticmethod
    def NDCG(truth, out):

        truth = set(truth)
        k = len(out)
        dcg = 0
        max_dcg = 0
        for i in range(k):
            factor = 1 if i == 0 else np.log2(i + 1)
            if out[i] in truth:
                dcg += 1 / factor
            if i < len(truth):
                max_dcg += 1 / factor
        return dcg / max_dcg

def mean(li):
    if len(li) == 0:
        raise ValueError("li shouldn't be empty")
    return sum(li)/len(li)
