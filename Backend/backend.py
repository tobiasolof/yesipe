from scipy.stats import truncnorm
from operator import itemgetter
import itertools
import pyrebase
import pickle
import math
from Backend import search
from Backend import nn_suggestor
import numpy as np
import csv


def stream_handler(root):

    # Retrieve path and data
    path = root['path']
    data = root['data']

    if path == '/clear' and data is True:
        clear()

    elif path == '/done' and data is True:
        done()

    elif path == '/search':
        if db.child('search').get().val():
            search_for_ingredient(db.child('search').get().val())

    elif path == '/choice':
        if str(data[0]) == 's':
            new_choice(db.child('searchResults').child(str(data[1:])).child('name').get().val())
        else:
            new_choice(db.child('suggestions').child(str(data[1:])).child('name').get().val())


def clear():
    print('\nClear')
    # Empty chosen
    db.child('chosen').set([])
    # Empty recipes
    db.child('recipes').set([])
    # Empty search and search results
    db.child('search').set([])
    db.child('searchResults').set([])
    # Generate new suggestions
    suggestions = sorted(ingredients.values(), key=itemgetter("main_freq"), reverse=True)[:no_suggestions]
    for t in suggestions:
        t["score"] = t["main_freq"]
    db.child('suggestions').set(suggestions)
    # Generate new positions
    positions = generate_positions()
    db.child('positions').set(positions)
    # Set clear to false again
    db.child('clear').set(False)


def new_choice(data):
    print('\nNew choice')
    # Append new choice
    to_be_added = [data]
    # Add substitutes if similarity > 0.x
    try:
        for s in search.similar_vectors(data, n=5):
            if s[1] > 0.6:
                to_be_added.append(s[0])
    except KeyError:
        pass
    db.child('chosen').child(data).set(to_be_added)
    print('Chosen ingredients so far: {}'.format([c.val() for c in db.child("chosen").get().each()]))

    # Update suggestions
    suggestions = generate_suggestions()
    db.child('suggestions').set(suggestions)
    # Update positions
    positions = generate_positions()
    db.child('positions').set(positions)

    # Add to training data TODO: Can be stored more efficiently
    with open('Backend/data/nn_training_data.csv', 'a+', newline='') as nn_training_data:
        writer = csv.writer(nn_training_data, delimiter=';', quotechar='|')
        writer.writerow([c.key() for c in db.child("chosen").get().each()])


def search_for_ingredient(data):
    print('Search for "{}"'.format(data))
    alternatives = []
    try:
        for s in search.similar_strings(data, n=7):
            # Add most similar word
            if not alternatives:
                alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
                                     "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
            # Add if similarity > 0.5
            elif s[1] > 0.5:
                alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
                                     "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
    except KeyError:
        pass

    # Generate positions for search results
    positions = generate_search_positions(alternatives)
    for i, p in enumerate(positions):
        if i < len(alternatives):
            alternatives[i]["x"] = p[0]
            alternatives[i]["y"] = p[1]
            alternatives[i]["r"] = p[2]

    # Update database
    db.child("searchResults").set(alternatives)


# TODO: Merge with generate_positions()
def generate_search_positions(alternatives):

    # Calculate radius from device size and frequency
    canvas_size = db.child("canvasSize").get().val()
    device_size_x, device_size_y = [s.val() for s in db.child("deviceSize").get().each()]
    min_radius, max_radius = device_size_x/6, device_size_y/8
    while True:
        try:
            search_results = alternatives
            radii = [s["freq"] for s in search_results]
            radii = [r / max(1, max(radii)) * (max_radius - min_radius) + min_radius for r in radii]
            break
        except TypeError:
            pass

    # Generate positions
    positions = []
    for i, r in enumerate(radii):
        mean = canvas_size/2
        std = canvas_size/100
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
                # print('Appended position for bubble %d: ' % i, end='')
                # print(positions[-1])
    return positions


def get_alternatives(data):

    # Suggest similar ingredients on long-press
    alternatives = []
    try:
        for s in search.similar_vectors(data, n=7):
            # Add most similar vector
            if not alternatives:
                alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
                                     "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
            # Add if similarity > 0.x
            elif s[1] > 0.5:
                alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
                                     "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
        # Update database
        db.child("altIngredients").child("alternatives").set(alternatives)
    except KeyError:
        pass


def within_recipe_space(combo, ingredient, best_over_combos):

    # Ensure that there exist recipes with given ingredient combination
    for count, recipe in enumerate(master):
        bad_recipe = False
        for ingr in list(combo) + [ingredient["name"]]:
            if ingr not in recipe["aug_ingredients"]:
                bad_recipe = True
                # print("Skipped recipe {} due to {}".format(count, ingr))
                break
        # If recipe exists, calculate and return recipe score
        if not bad_recipe:
            score = max(best_over_combos,
                        min(freq_matrix[ingredients[combo[i]]["id"]][ingredient["id"]] /
                            math.sqrt(ingredient["freq"])
                            for i in range(len(combo))))
            # print("{} made it with score {}".format(ingredient["name"], score))
            return score
    return -1


def generate_suggestions():

    # Get chosen list from database
    chosen = [c.val() for c in db.child("chosen").get().each()]

    # Create empty suggestion list
    nr_of_neural_net_suggestions = 50
    top_suggestions = [{"id": -1, "name": "", "freq": -1, "main_freq": -1, "score": -1}] * nr_of_neural_net_suggestions

    # Loop over all combinations of alternative ingredients
    for combo in list(itertools.product(*chosen)):

        # Get suggestions from neural net
        suggestions = neural_net.suggest(combo, 100)

        # Add to top suggestions if better than lowest score and sort list
        for s in suggestions:
            ingredient = ingredients[s[0]]
            score = s[1]
            if score > top_suggestions[-1]["score"] and \
                            ingredient["name"] not in list(itertools.chain.from_iterable(chosen)) and \
                            ingredient["name"] not in blacklist and not \
                    search.too_similar(ingredient, top_suggestions):
                ingredient["score"] = score
                top_suggestions[-1] = ingredient
                top_suggestions = sorted(top_suggestions, key=itemgetter("score"), reverse=True)

    # Print suggestions for traceability
    print("\nSuggestions:")
    print([ingr["name"] for ingr in top_suggestions])

    # Return top suggestions
    return top_suggestions

    # # Weight suggestions according to category importance
    # suggestions_per_category = [30, 5, 5, 5, 5]
    # # Get chosen list from database
    # chosen = [c.val() for c in db.child("chosen").get().each()]
    # # Create empty suggestion list
    # top_suggestions = [[{"id": -1, "name": "", "freq": -1, "main_freq": -1, "score": -1}] * suggestions_per_category[i]
    #                    for i in range(len(suggestions_per_category))]
    #
    # # Loop over all ingredients
    # for ingredient in ingredients.values():
    #     for category in range(len(suggestions_per_category)):
    #         best_over_combos = -1
    #         # Loop over all combinations of alternative ingredients
    #         for combo in list(itertools.product(*chosen)):
    #
    #             # Maximize the MIN relative importance with chosen ingredients
    #             if category == 0:
    #                 score = max(best_over_combos,
    #                             min(freq_matrix[ingredients[combo[i]]["id"]][ingredient["id"]] /
    #                                 math.sqrt(ingredient["freq"])
    #                                 for i in range(len(combo))))
    #             # Maximize the MAX relative importance with chosen ingredients
    #             # TODO: don't suggest if frequency is 0 with one ingredient
    #             if category == 1:
    #                 score = max(best_over_combos,
    #                             max(freq_matrix[ingredients[combo[i]]["id"]][ingredient["id"]] /
    #                                 math.sqrt(ingredient["freq"])
    #                                 for i in range(len(combo))))
    #             # Maximize the SUM of relative importance with chosen ingredients
    #             if category == 2:
    #                 score = max(best_over_combos,
    #                             sum(freq_matrix[ingredients[combo[i]]["id"]][ingredient["id"]] /
    #                                 math.sqrt(ingredient["freq"]) /
    #                                 math.sqrt(ingredients[combo[i]]["freq"])
    #                                 for i in range(len(combo))))
    #             # Penalizing frequency more, maximize the SUM of relative importance with chosen ingredients
    #             if category == 3:
    #                 score = max(best_over_combos,
    #                             sum(freq_matrix[ingredients[combo[i]]["id"]][ingredient["id"]] /
    #                                 math.pow(ingredient["freq"], 0.6) /
    #                                 math.sqrt(ingredients[combo[i]]["freq"])
    #                                 for i in range(len(combo))))
    #             # Rewarding frequency as main ingredient, Maximize the MIN relative importance with chosen ingredients
    #             if category == 4:
    #                 score = max(best_over_combos,
    #                             min(freq_matrix[ingredients[combo[i]]["id"]][ingredient["id"]] /
    #                                 math.sqrt(ingredient["freq"]) *
    #                                 ingredient["main_freq"]
    #                                 for i in range(len(combo))))
    #             # # Within the recipe space, Maximize the MIN
    #             # if category == 5:
    #             #     score = within_recipe_space(combo, ingredient, best_over_combos)
    #
    #         # Add to top suggestions if better than lowest score and sort list
    #         if score > top_suggestions[category][-1]["score"] and ingredient["name"] not in list(
    #                 itertools.chain.from_iterable(chosen)) and ingredient[
    #             "name"] not in blacklist and not search.too_similar(ingredient, list(
    #                 itertools.chain.from_iterable(top_suggestions))):
    #             ingredient["score"] = score
    #             top_suggestions[category][-1] = ingredient
    #             top_suggestions[category] = sorted(top_suggestions[category], key=itemgetter("score"), reverse=True)
    #
    # # Print suggestions for traceability
    # print("\nSuggestions:")
    # for i, l in enumerate(top_suggestions):
    #     print("  Category {} [mean freq={}]:".format(i, sum([ingr["freq"] for ingr in l]) / len(l))) if i == 3\
    #         else print("  Category {}:".format(i))
    #     print("   {}".format([ingr["name"] for ingr in l]))
    # print("")
    #
    # # Return top suggestions
    # top_suggestions = list(itertools.chain.from_iterable(top_suggestions))
    # return top_suggestions


def generate_positions():
    # Calculate radius from device size and frequency
    canvas_size = db.child("canvasSize").get().val()
    device_size_x, device_size_y = [s.val() for s in db.child("deviceSize").get().each()]
    min_radius, max_radius = device_size_x/6, device_size_y/8
    while True:
        try:
            suggestions = [s.val() for s in db.child('suggestions').get().each()]
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
                # print('Appended position for bubble %d: ' % i, end='')
                # print(positions[-1])
    return positions


def done():

    # Show best recipes when user is happy with ingredients
    print('\nDone.', end=" ")
    top_recipes = 5 * [{"id": -1, "title": "", "image": "", "instructions": "", "ingredients": [],
                        "cooking_time": "", "categories": [], "nutr": "", "tags": [], "score": -1,
                        "substitutions": []}]
    chosen = [k.val() for k in db.child("chosen").get().each()]
    # Prioritize actual choices over alternatives
    original_choices = list(db.child("chosen").shallow().get().val())
    print("Actual choices: {}\n".format(original_choices))
    # Loop over all recipes
    for recipe in master:
        best_over_combos = -1
        substitutions = []
        # Loop over all combinations of alternative ingredients
        for combo in list(itertools.product(*chosen)):
            temp_score = 0
            temp_substitutions = []
            for c in combo:
                if c in recipe["aug_ingredients"]:
                    try:
                        # Base score on alternatives' similarity to original choices
                        temp_index = np.argmax([search.ingr2vec.similarity(c, s) for s in original_choices])
                        temp_score += search.ingr2vec.similarity(c, original_choices[temp_index])
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

    # Write to database
    db.child('recipes').set(top_recipes)
    for t in top_recipes:
        print("{0} [{1:.2f}]".format(t["title"], t["score"]))
        print(t["aug_ingredients"], end="\n\n")
    return top_recipes

# ==================================================

if __name__ == "__main__":

    # Import data
    freq_matrix = pickle.load(open('Backend/data/freq_matrix.pickle', 'rb'))
    ingredients = pickle.load(open('Backend/data/ingredients.pickle', 'rb'))
    master = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
    blacklist = open('Backend/data/blacklist').read().lower().split("\n")

    # Initialize neural net
    neural_net = nn_suggestor.NNSuggestor(d=200)
    neural_net.restore_model()

    # Initialize firebase connection
    config = {
        "apiKey": "apiKey",
        "authDomain": "yesipe-test1.firebaseapp.com",
        "databaseURL": "https://yesipe-test1.firebaseio.com",
        "storageBucket": "gs://yesipe-test1.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Start the streaming
    stream = db.stream(stream_handler)
    no_suggestions = 50
    clear()
    print('\nModel loaded successfully.\n')
