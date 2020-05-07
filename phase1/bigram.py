import numpy as np
from helper import Text_cleaner
from functools import reduce 

class Bigram:

    def __init__(self):
        #bigram -> {word1, word2, ... wordn}
        self.bigram_index = dict()
        self.word_count = dict()

    def add_word(self, word):

        if word in self.word_count:
            self.word_count[word] += 1
            return

        self.word_count[word] = 1
        bigrams = Bigram.shatter(word)
        for bigram in bigrams:
            self.bigram_index.setdefault(bigram, set()).add(word)

    def remove_word(self, word):

        if word not in self.word_count:
            raise ValueError("Word not in index")

        self.word_count[word] -= 1
        if self.word_count[word] == 0:
            del self.word_count[word]
            for bigram in Bigram.shatter(word):
                #special case for گوناگون. 
                bigram_set = self.bigram_index.get(bigram)
                if not bigram_set:
                    continue

                if word in bigram_set:
                    bigram_set.remove(word)
                if not bigram_set:
                    del self.bigram_index[bigram]

    @staticmethod
    def shatter(word):
        word = "$" + word + "*"
        n = len(word)
        return [word[i:i + 2] for i in range(n - 1)]

    @staticmethod
    def edit_distance(word1, word2):
        l1 = len(word1)
        l2 = len(word2)
        m = np.zeros((l1, l2), dtype=np.long)
        for i in range(l1):
            m[i][0] = i + 1
        for j in range(l2):
            m[0][j] = j + 1

        for i in range(l1):
            for j in range(l2):
                m[i][j] = min(
                        m[i - 1, j] + 1,
                        m[i, j - 1] + 1,
                        m[i - 1, j - 1] + (0 if word1[i] == word2[j] else 1),
                        )
        return m[l1 - 1, l2 - 1]


    def jaccard(self, word1, word2):
        s1 = set(Bigram.shatter(word1))
        s2 = set(Bigram.shatter(word2))
        return len(set.intersection(s1, s2)) / len(set.union(s1, s2))

    def bigram_union(self, word):
        return reduce(set.union, map(lambda b: self.bigram_index[b], Bigram.shatter(word)))

    def top_jacard(self, word, k=100):
        li = [(w, self.jaccard(word, w)) for w in self.bigram_union(word)]
        li.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in li[:k]]

    def correct_query(self, text):
        words = Text_cleaner.bigram_cleaner(text)
        return ' '.join(map(self.fix_word, words))

    def fix_word(self, word):
        if word in self.word_count:
            return word

        candidates = self.top_jacard(word)
        return min(candidates, key = lambda w: Bigram.edit_distance(word, w))

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d
