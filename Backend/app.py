import os
import random
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
MODEL_PATH = os.path.join(CURRENT_DIR, 'models/w2v_spec.pkl')
MIN_SIM = 0.6


# Load models
ingr2vec = Word2Vec.load(os.path.join(CURRENT_DIR, 'models/ingr2vec.pkl'))
suggestor = keras.models.load_model(MODEL_PATH, custom_objects={'k': keras.backend})
suggestor._make_predict_function()
suggestor._make_train_function()


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


def _generate_suggestions(chosen, choice, n, canvas_size, dev_x, dev_y, rand_prop=0.25,
                          verbose=False):
    if choice:
        add_to_training_data(chosen, choice)
        nn_utils.train(suggestor, ingr2vec, chosen, choice)
        suggestor.save(MODEL_PATH)
    suggestions = nn_utils.predict_next([], suggestor, ingr2vec, round((1 - rand_prop) * n))
    # Random sample without overlap with suggestions
    random_suggestions = random.sample(
        [ingr for ingr in list(ingr2vec.wv.vocab) if ingr not in suggestions],
        round(rand_prop * n)
    )
    random_suggestions = [(r, suggestions[-1][1]) for r in random_suggestions]
    suggestions += random_suggestions
    suggestions = [s for s in suggestions if s[0] not in chosen]
    suggestions = [s for s in suggestions if s[0] not in blacklist]
    suggestions = [{'name': s[0], 'score': int(1000*s[1])} for s in suggestions]

    # Print suggestions for traceability
    if verbose:
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


def _generate_recipes_simple(chosen, n=10):
    top_recipes = master_df.copy()
    top_recipes['score'] = master_df.ingredients.apply(
        lambda recipe: len(list(set(chosen) & set(recipe))))
    top_recipes = top_recipes.sort_values('score', ascending=False)[:n]
    top_recipes = [r.to_dict() for _, r in top_recipes.iterrows()]
    return top_recipes


def _generate_recipes(chosen, n=10):
    chosen_and_sim = [[(c, 1.0)] + ingr2vec.wv.most_similar(c, topn=10) for c in chosen]
    chosen_and_sim = [[(sim_ingr, score) for sim_ingr, score in ingr_group if score >= MIN_SIM]
                      for ingr_group in chosen_and_sim]
    top_recipes = master_df.copy()
    top_recipes['score'] = top_recipes.ingredients.apply(score_recipe, chosen_and_sim=chosen_and_sim)
    top_recipes = top_recipes.sort_values('score', ascending=False)[:n]
    top_recipes = top_recipes.apply(rewrite_recipe, axis=1, chosen_and_sim=chosen_and_sim)
    top_recipes = [r.to_dict() for _, r in top_recipes.iterrows()]
    return top_recipes


def score_recipe(recipe, chosen_and_sim, n_dec=2):
    score = 0
    for ingr_group in chosen_and_sim:
        for ingr, sim in ingr_group:
            if ingr in recipe:
                score += sim
                break
    return round(score, n_dec)


def rewrite_recipe(recipe, chosen_and_sim):
    for ingr_group in chosen_and_sim:
        for ingr, sim in ingr_group:
            if ingr in recipe.ingredients:
                if ingr != ingr_group[0][0]:
                    recipe.loc['instructions'] = recipe.instructions.replace(
                        ingr,
                        '\u0336'.join(ingr) + '\u0336' + ' ' + ingr_group[0][0]
                    )
                break
    return recipe


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8005)
