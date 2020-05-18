import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from helper import dist_euclid

class Kmeans:

    def set_vectors(self, vecs):
        self.vecs = vecs

    def set_random_centers(self, k=4, seed=78):
        np.random.seed(seed)
        center_indexes = np.random.choice(len(self.vecs), k, replace=False)
        self.centers = self.vecs[center_indexes]
        self.assign_labels()

    def fill_dist(self):
        x = self.vecs
        y = self.centers
        self.dists = dist_euclid(x, y)

    def assign_labels(self):
        self.fill_dist()
        self.labels = self.dists.argmin(axis=1)
        self.cost_function = self.dists[np.arange(len(self.dists)), self.labels].sum()

    def assign_centers(self):
        k = len(self.centers)
        for i in range(k):
            is_i = self.labels == i
            self.centers[i] = np.mean(self.vecs[is_i], axis=0)

    def one_iter(self):
        self.assign_centers()
        self.assign_labels()

class Shower:

    def set_vectors(self, vecs):
        self.vecs = vecs
        self.tsne = TSNE(n_components=2)

    def set_indexes(self, indexes):
        self.indexes = indexes

    @staticmethod
    def get_color(i):
        li = ['orange', 'blue', 'green', 'black']
        return li[i]

    @property
    def to_show(self):
        return self.vecs[self.indexes]

    @property
    def for_show_colors(self):
        return map(Shower.get_color, self.labels[self.indexes])

    def fit(self):
        self.embedded = self.tsne.fit_transform(self.to_show)

    def set_labels(self, labels):
        self.labels = labels


    def plot(self):
        for point, color in zip(self.embedded, self.for_show_colors):
            plt.scatter(point[0], point[1], color=color)

