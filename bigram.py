import numpy as np
class Bigram:

    def __init__(self):
        #bigram -> {word1, word2, ... wordn}
        self.bigram_index = {}
        self.word_set = set()

    def add_word(self, word):
        self.word_set.add(word)
        bigrams = Bigram.shatter(word)
        for bigram in bigrams:
            self.bigram_index.setdefault(bigram, []).add(word)

    def remove_word(self, word):

        if word in self.word_set:
            self.word_set.remove(word)

        bigrams = Bigram.shatter(word)
        for bigram in bigrams:
            bigram_set = self.bigram_index[bigram]
            if word in bigram_set:
                bigram_set.remove(word)

    @staticmethod
    def shatter(word):
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



    def extract_top_bigram(self, word):
        pass

    def fix_word(self, word):
        if w in self.word_set:
            return w

        candidates = self.extract_top_bigram(word)
        return max(candidates, key = lambda w: edit_distance(word, w), reverse=True)
