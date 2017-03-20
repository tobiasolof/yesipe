import pickle
import gensim
from sklearn import cluster
from operator import itemgetter

# recipes = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
# print("Loaded {} recipes".format(len(recipes)))
#
# sentences = []
# for r in recipes:
#     sentences.append(r['ingredients'])
#
# ingr2vec = gensim.models.Word2Vec(sentences, size=50, window=100, min_count=5, workers=30, iter=1000)
# ingr2vec.save("Backend/data/ingr2vec_model")
# print("Saved ingr2vec model to Backend/data/ingr2vec_model")

# ==================================

ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))
ingr2vec = gensim.models.Word2Vec.load("Backend/data/ingr2vec_model")

raw_vectors = []
names = []
for ingredient in ingredients:
    try:
        raw_vectors.append(ingr2vec[ingredient])
        names.append(ingredient)
    except KeyError:
        pass

print("\nWe have {} vectors in the ingr2vec model.".format(len(raw_vectors)))

n_clusters = int(input("Enter number of clusters: "))
print("")
k_means = cluster.KMeans(n_clusters=n_clusters)
k_means.fit(raw_vectors)
labels = k_means.predict(raw_vectors)
x = zip(names, labels)
x = sorted(x, key=itemgetter(1))

all_classes = [[] for n in range(n_clusters)]
for element in x:
    all_classes[element[1]].append((element[0], ingredients[element[0]]["freq"]))
for c in all_classes:
    c.sort(key=itemgetter(1), reverse=True)
    c = [k[0] for k in c]
    print(c[:20])
    print("")
