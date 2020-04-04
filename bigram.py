class Bigram:

    def __init__(self):
        #bigram -> {word1, word2, ... wordn}
        self.bigram_index = {}

    def add_word(self, word):
        bigrams = Bigram.shatter(word)
        for bigram in bigrams:
            self.bigram_index.setdefault(bigram, []).add(word)

    def remove_word(self, word):
        bigrams = Bigram.shatter(word)
        for bigram in bigrams:
            bigram_set = self.bigram_index[bigram]
            if word in bigram_set:
                bigram_set.remove(word)

    @staticmethod
    def shatter(word):
        n = len(word)
        return [word[i:i + 2] for i in range(n - 1)]

