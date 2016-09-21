from operator import itemgetter
import numpy as np
import pickle

# Read in data
recipes = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
print("Number of recipes: {}".format(len(recipes)))
blacklist = open('Backend/data/blacklist').read().lower().split("\n")


# # Change bad ingredients to the ones specified in aliases
# import re
# import json
# import pprint
# temp_aliases = open('Backend/data/aliases').read().splitlines()
# aliases = {}
# for line in temp_aliases:
#     old_name = re.search('.+->', line).group()[:-3]
#     new_name = re.search('->.+', line).group()[3:]
#     if new_name != old_name:
#         aliases[old_name] = {"old_name": old_name, "new_name": new_name}
# for r in recipes:
#     r["ingredients_true"] = r["ingredients"].copy()
#     for i, ingredient in enumerate(r["ingredients"]):
#         if ingredient in aliases:
#             r["ingredients"][i] = aliases[ingredient]["new_name"]
#     for i, ingredient in enumerate(r["aug_ingredients"]):
#         if ingredient in aliases:
#             ingredient = aliases[ingredient]["new_name"]
#     for i, ingredient in enumerate(r["categories"]):
#         if ingredient in aliases:
#             r["categories"][i] = aliases[ingredient]["new_name"]
#     for i, ingredient in enumerate(r["tags"]["main_ingr"]):
#         if ingredient in aliases:
#             r["tags"]["main_ingr"][i] = aliases[ingredient]["new_name"]
# with open('Backend/data/tasteline.json', 'w') as f:
#     json.dump(recipes, f)
#     print("Wrote {} recipes to {}".format(len(recipes), "tasteline.json"))
# with open('Backend/data/tasteline.pickle', 'wb') as f:
#     pickle.dump(recipes, f)
#     print("Wrote {} recipes to {}".format(len(recipes), "tasteline.pickle"))


# # Fix broken categories
# import regex as re
# import json
# for r in recipes:
#     for i, category in enumerate(r["categories"]):
#         if "href" in category:
#             categories = re.sub("<\/span>.*\/\">", ",", category).split(",")
#             r["categories"][i] = categories[0]
#             r["categories"].append(categories[1])
#             print(r["categories"])
# pickle.dump(recipes, open('Backend/data/tasteline.pickle', 'wb'))
# json.dump(recipes, open('Backend/data/tasteline.json', 'w'))


# # Fix "&amp;"
# import regex as re
# import json
# for r in recipes:
#     for i, ingredient in enumerate(r["ingredients"]):
#         if "&amp;" in ingredient:
#             ingredient = re.sub("&amp;", "&", ingredient)
#             r["ingredients"][i] = ingredient
#             print(r["ingredients"])
# pickle.dump(recipes, open('Backend/data/tasteline.pickle', 'wb'))
# json.dump(recipes, open('Backend/data/tasteline.json', 'w'))


# import pprint
# import json
# for r in recipes:
#     r["aug_ingredients"] = r["ingredients"]
#     for category in r["categories"]:
#         if category not in r["aug_ingredients"]:
#             r["aug_ingredients"].append(category)
#     pprint.pprint(r["aug_ingredients"])
# pickle.dump(recipes, open('Backend/data/tasteline.pickle', 'wb'))
# json.dump(recipes, open('Backend/data/tasteline.json', 'w'))


# Ingredient IDs, frequency and "main frequency"
ingredients = []
for r in recipes:
    ingredients.extend(r['aug_ingredients'])
unique_ingredients = list(set(ingredients))
unique_ingredients.sort()
ingredients = {}
percent = 0
for i, ingredient in enumerate(unique_ingredients):
    freq = 0
    main_freq = 0
    for r in recipes:
        if ingredient in r["aug_ingredients"]:
            freq += 1
        if ingredient in r["tags"]["main_ingr"]:
            main_freq += 1
    entry = ({"id": i, "name": ingredient, "freq": freq, "main_freq": main_freq})
    ingredients[ingredient] = entry
    if int(100 * i/len(unique_ingredients)) > percent:
        percent = int(100 * i/len(unique_ingredients))
        print("{}%".format(percent), end=" ")
with open('Backend/data/ingredients.pickle', 'wb') as f:
    pickle.dump(ingredients, f)
    print("\nNumber of ingredients: {}".format(len(ingredients)))


# Co-occurrence matrix
ingredients = pickle.load(open('Backend/data/ingredients.pickle', 'rb'))
unique_ingredients = list(set(ingredients))
unique_ingredients.sort()
freq_matrix = np.zeros((len(unique_ingredients), len(unique_ingredients)))
percent = 0
for count, r in enumerate(recipes):
    temp_ingredients = r['aug_ingredients']
    for i, first_ingredient in enumerate(temp_ingredients):
        for second_ingredient in temp_ingredients[i+1:]:
            a = ingredients[first_ingredient]["id"]
            b = ingredients[second_ingredient]["id"]
            freq_matrix[a][b] += 1
            freq_matrix[b][a] += 1
    if round(100 * count/len(recipes)) > percent:
        percent = round(100 * count/len(recipes))
        print("1: {0:d}%".format(percent))
    print('{}%'.format(int(100*count/len(recipes))), end=" ")
with open('Backend/data/freq_matrix.pickle', 'wb') as f:
    pickle.dump(freq_matrix, f)
