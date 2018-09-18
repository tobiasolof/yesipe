import os
import math
import pandas as pd
from scipy.stats import truncnorm
from gensim.models import Word2Vec
import keras

from flask import Flask, jsonify
from webargs import fields
from webargs.flaskparser import use_kwargs

import nn_utils


app = Flask(__name__)


# Define constants
CURRENT_DIR = os.path.dirname(__file__)
CHOICES_PATH = os.path.join(CURRENT_DIR, 'data/choices.csv')


# Load models
ingr2vec = Word2Vec.load(os.path.join(CURRENT_DIR, 'models/ingr2vec.pkl'))
suggestor = keras.models.load_model(
    os.path.join(CURRENT_DIR, 'models/w2v_spec.pkl'),
    custom_objects={'k': keras.backend}
)
suggestor._make_predict_function()


# Load data
master_df = pd.read_pickle(os.path.join(CURRENT_DIR, 'data/master_df.pkl'))
blacklist = open(os.path.join(CURRENT_DIR, 'data/blacklist')).read().lower().split('\n')


@app.route('/generate_suggestions', methods=['POST'])
@use_kwargs({
    'chosen': fields.List(
        fields.Str(),
        required=True,
        locations=('json',)
    ),
    'choice': fields.Str(
        required=False,
        locations=('json',)
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
def generate_suggestions(chosen, choice, n, canvas_size, dev_x, dev_y):
    return jsonify(_generate_suggestions(chosen, choice, n, canvas_size, dev_x, dev_y))


def _generate_suggestions(chosen, choice, n, canvas_size, dev_x, dev_y):
    if choice:
        add_to_training_data(chosen, choice)
    suggestions = nn_utils.predict_next([], suggestor, ingr2vec, n=n)
    suggestions = [s for s in suggestions if s[0] not in chosen]
    suggestions = [s for s in suggestions if s[0] not in blacklist]
    suggestions = [{'name': s[0], 'score': int(1000*s[1])} for s in suggestions]

    # Print suggestions for traceability
    print('\nSuggestions:')
    print([s['name'] for s in suggestions])

    # Add positions
    positions = generate_positions(suggestions, canvas_size, dev_x, dev_y)
    for i, s in enumerate(suggestions):
        s['x'], s['y'], s['r'] = positions[i]

    # Return top suggestions
    return suggestions


def add_to_training_data(chosen, choice):
    with open(CHOICES_PATH, 'a+') as f:
        f.write(','.join([c for c in chosen if c != choice]) + ';' + choice + '\n')


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


def generate_positions(suggestions, canvas_size, device_size_x, device_size_y):
    # Calculate radius from device size and frequency
    min_radius, max_radius = device_size_x/6, device_size_y/8
    while True:
        try:
            radii = [s["score"] for s in suggestions]
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


def _generate_recipes(chosen, n=10):
    top_recipes = master_df.copy()
    top_recipes['score'] = master_df.ingredients.apply(
        lambda recipe: len(list(set(chosen) & set(recipe))))  # TODO: aug_ingredients
    top_recipes = top_recipes.sort_values('score', ascending=False)[:n]
    top_recipes = [r.to_dict() for _, r in top_recipes.iterrows()]
    return top_recipes


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8005)
