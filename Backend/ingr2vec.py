import pickle
import gensim
from sklearn import cluster
from operator import itemgetter
import multiprocessing


class Ingr2Vec(object):

    def __init__(self):
        self.ingr2vec = None

    def cluster(self, k):
        ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))
        raw_vectors = []
        names = []
        for ingr in ingredients:
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
            all_classes[element[1]].append((element[0], ingredients[element[0]]["freq"]))
        for c in all_classes:
            c.sort(key=itemgetter(1), reverse=True)
            c = [k[0] for k in c]
            print(c[:20])
            print("")

    def load(self, path='Backend/data/ingr2vec_model'):
        self.ingr2vec = gensim.models.Word2Vec.load(path)

    def model_score(self):
        recipes = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
        score = sum(self.ingr2vec.score([r['ingredients'] for r in recipes], total_sentences=len(recipes)))/len(recipes)
        return score

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

    # for d in [5, 10, 20, 30, 40, 50]:
    #     i2v = Ingr2Vec()
    #     i2v.train(d=d, iterations=10000)
    #     print(i2v.model_score())

    i2v = Ingr2Vec()
    i2v.load('Backend/data/ingr2vec_model_20')
    i2v.cluster(15)
