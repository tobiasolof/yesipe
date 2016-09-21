import pickle
from difflib import SequenceMatcher
from operator import itemgetter
import gensim

ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))
ingr2vec = gensim.models.Word2Vec.load("Backend/data/ingr2vec_model")


def similar_strings(string, n=10):
    top_similar = n * [(" ", -1.0)]
    for ingredient in ingredients:
        score = SequenceMatcher(None, string, ingredient).ratio()
        if score > top_similar[0][1]:
            top_similar[0] = (ingredient, score)
            top_similar = sorted(top_similar, key=itemgetter(1))
    top_similar.reverse()
    return top_similar


def similar_vectors(string, n=10):
    return ingr2vec.most_similar(string, topn=n)


if __name__ == "__main__":
    while True:
        w = input('\nEnter ingredient: ')
        if w != "-q":
            # print("Most similar by string:")
            # for s in similar_strings(w):
            #     print("    {0:.2f} - {1}".format(s[1], s[0]))
            try:
                print("Most similar by vector:")
                for s in similar_vectors(w):
                    print("    {0:.2f} - {1}".format(s[1], s[0]))
            except KeyError:
                print('    Unknown ingredient.\n')
        else:
            raise SystemExit
