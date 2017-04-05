import pickle
import gensim
from sklearn import cluster
from operator import itemgetter
from difflib import SequenceMatcher
import multiprocessing


class Ingr2Vec(object):

    def __init__(self):
        self.ingr2vec = None
        self.ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))

    def cluster(self, k):
        raw_vectors = []
        names = []
        for ingr in self.ingredients:
            try:
                raw_vectors.append(self.ingr2vec[ingr])
                names.append(ingr)
            except KeyError:
                pass
        print("\nThere are {} vectors in the ingr2vec model.".format(len(raw_vectors)))

        k_means = cluster.KMeans(n_clusters=k)
        k_means.fit(raw_vectors)
        labels = k_means.predict(raw_vectors)
        x = zip(names, labels)
        x = sorted(x, key=itemgetter(1))

        all_classes = [[] for n in range(k)]
        for element in x:
            all_classes[element[1]].append((element[0], self.ingredients[element[0]]["freq"]))
        for c in all_classes:
            c.sort(key=itemgetter(1), reverse=True)
            c = [k[0] for k in c]
            print(c[:20])
            print("")

    def explore(self):
        while True:
            w = input('\nEnter ingredient: ')
            if w != "-q":
                print("Most similar by string:")
                for s in self.similar_strings(w):
                    print("    {0:.2f} - {1}".format(s[1], s[0]))
                try:
                    print("Most similar by vector:")
                    for s in self.similar_vectors(w):
                        print("    {0:.2f} - {1}".format(s[1], s[0]))
                except KeyError:
                    print('    Unknown ingredient.\n')
            else:
                return

    def load(self, path='Backend/data/ingr2vec_model'):
        self.ingr2vec = gensim.models.Word2Vec.load(path)

    def model_score(self):
        recipes = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
        score = sum(self.ingr2vec.score([r['ingredients'] for r in recipes], total_sentences=len(recipes)))/len(recipes)
        return score

    def similar_strings(self, string, n=10):
        top_similar = n * [(" ", -1.0)]
        for ingredient in self.ingredients:
            score = SequenceMatcher(None, string, ingredient).ratio()
            if score > top_similar[0][1]:
                top_similar[0] = (ingredient, score)
                top_similar = sorted(top_similar, key=itemgetter(1))
        top_similar.reverse()
        return top_similar

    def similar_vectors(self, string, n=10):
        return self.ingr2vec.most_similar(string, topn=n)

    def too_similar(self, ingr1, ingr_set):
        for i in ingr_set:
            if ingr1["name"] == i["name"]:
                return True
            try:
                similarity = self.ingr2vec.similarity(ingr1["name"], i["name"])
                if similarity > 0.7:
                    # print("'{}' and '{}' too similar ({})".format(ingr1["name"], i["name"], similarity))
                    return True
            except KeyError:
                pass
        return False

    def train(self, d, min_count=5, iterations=1000):
        recipes = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))

        max_ingr = 0
        sentences = []
        for r in recipes:
            sentences.append(r['ingredients'])
            max_ingr = max(max_ingr, len(r['ingredients']))

        self.ingr2vec = gensim.models.Word2Vec(sentences, size=d, window=max_ingr, min_count=min_count,
                                               workers=multiprocessing.cpu_count(), iter=iterations, hs=1, negative=0)
        self.ingr2vec.save("Backend/data/ingr2vec_model_"+str(d))
        print("Saved ingr2vec model to Backend/data/ingr2vec_model_"+str(d))


if __name__ == "__main__":

    i2v = Ingr2Vec()
    i2v.train(d=200, iterations=10000)
    print(i2v.model_score())
    i2v.cluster(5)
