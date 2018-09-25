import os
import random
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
import keras

from flask import Flask, jsonify
from flask_cors import CORS
from webargs import fields
from webargs.flaskparser import use_kwargs

import nn_utils


app = Flask(__name__)
CORS(app)


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
    'chosen': fields.Dict(
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
def generate_suggestions(chosen, choice, n, dev_x, dev_y):
    return jsonify(_generate_suggestions(chosen, choice, n, dev_x, dev_y))


def _generate_suggestions(chosen, choice, n, dev_x, dev_y, rand_prop=0.25,
                          verbose=False):
    if choice:
        add_to_training_data(chosen.keys(), choice)
        nn_utils.train(suggestor, ingr2vec, chosen.keys(), choice)
        suggestor.save(MODEL_PATH)
    suggestions = nn_utils.predict_next([], suggestor, ingr2vec, round((1 - rand_prop) * n))
    # Random sample without overlap with suggestions
    random_suggestions = random.sample(
        [ingr for ingr in list(ingr2vec.wv.vocab) if ingr not in suggestions],
        round(rand_prop * n)
    )
    random_suggestions = [(r, suggestions[-1][1]) for r in random_suggestions]
    suggestions += random_suggestions
    suggestions = [s for s in suggestions if s[0] not in chosen.keys()]
    suggestions = [s for s in suggestions if s[0] not in blacklist]
    suggestions = [{'name': s[0], 'score': int(1000*s[1])} for s in suggestions]

    # Print suggestions for traceability
    if verbose:
        print('\nSuggestions:')
        print([s['name'] for s in suggestions])

    # Add positions
    positions = generate_positions(chosen, suggestions, dev_x, dev_y)
    for i, s in enumerate(suggestions):
        s['x'], s['y'], s['r'] = positions[i]

    # Return top suggestions
    return suggestions


def add_to_training_data(chosen, choice):
    with open(CHOICES_PATH, 'a+') as f:
        f.write(','.join([c for c in chosen if c != choice]) + ';' + choice + '\n')


def generate_positions(chosen, suggestions, device_size_x, device_size_y):
    min_radius, max_radius = device_size_x / 10, device_size_x / 6
    max_score = max(s['score'] for s in suggestions)
    min_score = max(s['score'] for s in suggestions)
    positions = [(c[1], c[2], c[3]) for c in chosen.values()]
    for s in suggestions:
        try:
            r = (s['score'] - min_score) / (max_score - min_score) * \
                (max_radius - min_radius) + min_radius
        except ZeroDivisionError:
            r = (max_radius + min_radius) / 2
        while True:
            x = r + random.random() * (device_size_x - 2 * r)
            y = r + random.random() * (device_size_y - 2 * r)
            if len(positions) == 0 or all(np.linalg.norm((x - xx, y - yy)) > (r + rr) for xx, yy, rr in positions):
                break
        positions.append((x, y, r))
    return positions[len(chosen):]


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
