from hazm import Normalizer, word_tokenize, Stemmer
import re
import numpy as np

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
        return cleaned

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
