from scipy.stats import truncnorm
from operator import itemgetter
import itertools
import pickle
import math
import ingr2vec
import nn_suggestor
import numpy as np
import csv


from flask import Flask, jsonify
from webargs import fields
from webargs.flaskparser import use_kwargs


app = Flask(__name__)


# Import data
freq_matrix = pickle.load(open('Backend/data/freq_matrix.pickle', 'rb'))
ingredients = pickle.load(open('Backend/data/ingredients.pickle', 'rb'))
master = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
blacklist = open('Backend/data/blacklist').read().lower().split("\n")

# Initialize neural net
neural_net = nn_suggestor.NNSuggestor(d=200)
neural_net.restore_model()
print(1)

# Initialize ingr2vec
i2v = ingr2vec.Ingr2Vec()
i2v.load('Backend/data/ingr2vec_model_200')


# def new_choice(data):
#     print('\nNew choice')
#     # Append new choice
#     to_be_added = [data]
#     # Add substitutes if similarity > 0.x
#     try:
#         for s in i2v.similar_vectors(data, n=5):
#             if s[1] > 0.6:
#                 to_be_added.append(s[0])
#     except KeyError:
#         pass
#     db.child('chosen').child(data).set(to_be_added)
#     print('Chosen ingredients so far: {}'.format([c.val() for c in db.child("chosen").get().each()]))
#
#     # Update suggestions
#     suggestions = generate_suggestions()
#     db.child('suggestions').set(suggestions)
#     # Update positions
#     positions = generate_positions()
#     db.child('positions').set(positions)
#
#     # Add to training data
#     with open('Backend/data/nn_training_data.csv', 'a+', newline='') as nn_training_data:
#         writer = csv.writer(nn_training_data, delimiter=';', quotechar='|')
#         writer.writerow([c.key() for c in db.child("chosen").get().each()])
#
#
# def search_for_ingredient(data):
#     print('Search for "{}"'.format(data))
#     alternatives = []
#     try:
#         for s in i2v.similar_strings(data, n=7):
#             # Add most similar word
#             if not alternatives:
#                 alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
#                                      "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
#             # Add if similarity > 0.5
#             elif s[1] > 0.5:
#                 alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
#                                      "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
#     except KeyError:
#         pass
#
#     # Generate positions for search results
#     positions = generate_search_positions(alternatives)
#     for i, p in enumerate(positions):
#         if i < len(alternatives):
#             alternatives[i]["x"] = p[0]
#             alternatives[i]["y"] = p[1]
#             alternatives[i]["r"] = p[2]
#
#     # Update database
#     db.child("searchResults").set(alternatives)
#
#
# # TODO: Merge with generate_positions()
# def generate_search_positions(alternatives):
#
#     # Calculate radius from device size and frequency
#     canvas_size = db.child("canvasSize").get().val()
#     device_size_x, device_size_y = [s.val() for s in db.child("deviceSize").get().each()]
#     min_radius, max_radius = device_size_x/6, device_size_y/8
#     while True:
#         try:
#             search_results = alternatives
#             radii = [s["freq"] for s in search_results]
#             radii = [r / max(1, max(radii)) * (max_radius - min_radius) + min_radius for r in radii]
#             break
#         except TypeError:
#             pass
#
#     # Generate positions
#     positions = []
#     for i, r in enumerate(radii):
#         mean = canvas_size/2
#         std = canvas_size/100
#         no_overlaps = False
#         # Iteratively generate random positions until no overlaps and add to list
#         while not no_overlaps:
#             x = truncnorm.rvs((0 - mean) / std, (canvas_size - mean) / std, loc=mean, scale=std)
#             y = truncnorm.rvs((0 - mean) / std, (canvas_size - mean) / std, loc=mean, scale=std)
#             if i == 0:
#                 no_overlaps = True
#             for j, p in enumerate(positions):
#                 d = math.sqrt(math.pow(x - p[0], 2) + math.pow(y - p[1], 2))
#                 if d > r + p[2]:
#                     no_overlaps = True
#                 else:
#                     no_overlaps = False
#                     std *= 1.01
#                     break
#             if no_overlaps:
#                 positions.append([x, y, r])
#                 # print('Appended position for bubble %d: ' % i, end='')
#                 # print(positions[-1])
#     return positions
#
#
# def get_alternatives(data):
#
#     # Suggest similar ingredients on long-press
#     alternatives = []
#     try:
#         for s in i2v.similar_vectors(data, n=7):
#             # Add most similar vector
#             if not alternatives:
#                 alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
#                                      "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
#             # Add if similarity > 0.x
#             elif s[1] > 0.5:
#                 alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
#                                      "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
#         # Update database
#         db.child("altIngredients").child("alternatives").set(alternatives)
#     except KeyError:
#         pass
#
#
# def within_recipe_space(combo, ingredient, best_over_combos):
#
#     # Ensure that there exist recipes with given ingredient combination
#     for count, recipe in enumerate(master):
#         bad_recipe = False
#         for ingr in list(combo) + [ingredient["name"]]:
#             if ingr not in recipe["aug_ingredients"]:
#                 bad_recipe = True
#                 # print("Skipped recipe {} due to {}".format(count, ingr))
#                 break
#         # If recipe exists, calculate and return recipe score
#         if not bad_recipe:
#             score = max(best_over_combos,
#                         min(freq_matrix[ingredients[combo[i]]["id"]][ingredient["id"]] /
#                             math.sqrt(ingredient["freq"])
#                             for i in range(len(combo))))
#             # print("{} made it with score {}".format(ingredient["name"], score))
#             return score
#     return -1


@app.route('/generate_suggestions', methods=['POST'])
@use_kwargs({
    'chosen': fields.Dict(
        fields.List(
            fields.Str(),
            required=True,
            locations=('json',)
        )
    ),
    'n': fields.Int(
        required=False,
        locations=('json',),
        validate=lambda x: x > 0,
        missing=10
    ),
    'canvas_size': fields.Int(
        required=True,
        locations=('json',),
        validate=lambda x: x > 0,
    ),
    'dev_x': fields.Int(
        required=True,
        locations=('json',),
        validate=lambda x: x > 0,
    ),
    'dev_y': fields.Int(
        required=True,
        locations=('json',),
        validate=lambda x: x > 0,
    )
})
def generate_suggestions(chosen, n, canvas_size, dev_x, dev_y):
    return jsonify(_generate_suggestions(chosen, n, canvas_size, dev_x, dev_y))


def _generate_suggestions(chosen, n, canvas_size, dev_x, dev_y):
    # Create empty suggestion list
    top_suggestions = [{"id": -1, "name": "", "freq": -1, "main_freq": -1,
                        "score": -1}] * n

    # Loop over all combinations of alternative ingredients
    for combo in list(itertools.product(*chosen.values())):

        try:
            # Get suggestions from neural net
            suggestions = neural_net.suggest(combo, 100)
        except ValueError:
            suggestions = sorted(ingredients.values(), key=itemgetter("main_freq"), reverse=True)[:n]
            suggestions = [(s['name'], s['main_freq']) for s in suggestions]

        # Add to top suggestions if better than lowest score and sort list
        for s in suggestions:
            ingredient = ingredients[s[0]]
            score = s[1]
            if score > top_suggestions[-1]["score"] and \
                    ingredient["name"] not in list(itertools.chain.from_iterable(chosen)) and \
                    ingredient["name"] not in blacklist and not \
                    i2v.too_similar(ingredient, top_suggestions):
                ingredient["score"] = score
                top_suggestions[-1] = ingredient
                top_suggestions = sorted(top_suggestions, key=itemgetter("score"), reverse=True)

    # Print suggestions for traceability
    print("\nSuggestions:")
    print([ingr["name"] for ingr in top_suggestions])

    # Add positions
    positions = generate_positions(top_suggestions, canvas_size, dev_x, dev_y)
    for i, s in enumerate(top_suggestions):
        s['x'], s['y'], s['r'] = positions[i]

    # Return top suggestions
    return top_suggestions


def generate_positions(suggestions, canvas_size, device_size_x, device_size_y):
    # Calculate radius from device size and frequency
    min_radius, max_radius = device_size_x/6, device_size_y/8
    while True:
        try:
            radii = [s["freq"] for s in suggestions]
            radii = [r / max(1, max(radii)) * (max_radius - min_radius) + min_radius for r in radii]
            break
        except TypeError:
            pass

    # Generate positions
    positions = []
    for i, r in enumerate(radii):
        mean = canvas_size/2
        std = canvas_size/10
        no_overlaps = False
        # Iteratively generate random positions until no overlaps and add to list
        while not no_overlaps:
            x = truncnorm.rvs((0 - mean) / std, (canvas_size - mean) / std, loc=mean, scale=std)
            y = truncnorm.rvs((0 - mean) / std, (canvas_size - mean) / std, loc=mean, scale=std)
            if i == 0:
                no_overlaps = True
            for j, p in enumerate(positions):
                d = math.sqrt(math.pow(x - p[0], 2) + math.pow(y - p[1], 2))
                if d > r + p[2]:
                    no_overlaps = True
                else:
                    no_overlaps = False
                    std *= 1.01
                    break
            if no_overlaps:
                positions.append([x, y, r])
    return positions


@app.route('/generate_recipes', methods=['POST'])
@use_kwargs({
    'chosen': fields.Dict(
        fields.List(
            fields.Str(),
            required=True,
            locations=('json',)
        )
    ),
})
def generate_recipes(chosen):
    return jsonify(_generate_recipes(chosen))


def _generate_recipes(chosen):
    # chosen = {"räkor":["räkor"],"löjrom":["löjrom"],"svarta bönor":["svarta bönor"]}
    top_recipes = 5 * [
        {"id": -1, "title": "", "image": "", "instructions": "", "ingredients": [],
        "cooking_time": "", "categories": [], "nutr": "", "tags": [], "score": -1,
        "substitutions": []}
    ]
    # Prioritize actual choices over alternatives
    original_choices = list(chosen.keys())
    print("Actual choices: {}\n".format(original_choices))
    # Loop over all recipes
    for recipe in master:
        best_over_combos = -1
        substitutions = []
        # Loop over all combinations of alternative ingredients
        for combo in list(itertools.product(*chosen.values())):
            temp_score = 0
            temp_substitutions = []
            for c in combo:
                if c in recipe["aug_ingredients"]:
                    try:
                        # Base score on alternatives' similarity to original choices
                        temp_index = np.argmax([i2v.ingr2vec.similarity(c, s) for s in original_choices])
                        temp_score += i2v.ingr2vec.similarity(c, original_choices[temp_index])
                        if original_choices[temp_index] != c:
                            temp_substitutions.append([c, original_choices[temp_index]])
                    except KeyError:
                        temp_score += 1
            if temp_score > best_over_combos:
                best_over_combos = temp_score
                substitutions = temp_substitutions
        # TODO: weight in if there's an author
        # Add to top recipes if better than lowest score and sort list
        if best_over_combos > top_recipes[0]["score"]:
            recipe["score"] = best_over_combos
            recipe["substitutions"] = substitutions
            top_recipes[0] = recipe
            top_recipes = sorted(top_recipes, key=itemgetter("score"))
    top_recipes.reverse()
    for t in top_recipes:
        t["score"] = round(t["score"], 2)
    return top_recipes


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8005)
