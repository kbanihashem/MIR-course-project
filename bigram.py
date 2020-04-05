import numpy as np
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



    def extract_top_bigram(self, word):
        pass

    def fix_word(self, word):
        if w in self.word_set:
            return w

        candidates = self.extract_top_bigram(word)
        return max(candidates, key = lambda w: edit_distance(word, w), reverse=True)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d
