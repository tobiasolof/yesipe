from scipy.stats import truncnorm
from operator import itemgetter
import pyrebase
import pickle
import math
from Backend import search


def stream_handler(root):

    # Retrieve path and data
    path = root['path']
    data = root['data']

    if path == '/clear' and data is True:
        clear()

    elif path == '/done' and data is True:
        done()

    elif path == '/request':
        get_alternatives(db.child('suggestions').child(str(data)).child('name').get().val())

    elif path == '/choice':
        new_choice(db.child('suggestions').child(str(data)).child('name').get().val())


def clear():
    print('\nClear')
    # Empty chosen
    db.child('chosen').set([])
    # Empty recipes
    db.child('recipes').set([])
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
    # Append new choice and possibly substitutes
    db.child('chosen').push(data)
    try:
        for s in search.similar_vectors(data, n=5):
            if s[1] > 0.75:
                db.child('chosen').push(s[0])
    except KeyError:
        pass
    print('Chosen ingredients so far: {}'.format([c.val() for c in db.child("chosen").get().each()]))

    # Update suggestions
    suggestions = generate_suggestions()
    db.child('suggestions').set(suggestions)
    # Update positions
    positions = generate_positions()
    db.child('positions').set(positions)


def get_alternatives(data):
    alternatives = []
    try:
        for s in search.similar_vectors(data, n=7):
            if s[1] > 0.5:
                alternatives.append({"name": s[0], "freq": ingredients[s[0]]["freq"], "id": ingredients[s[0]]["id"],
                                     "main_freq": ingredients[s[0]]["main_freq"], "similarity": s[1]})
        db.child("altIngredients").child("alternatives").set(alternatives)
    except KeyError:
        pass


def generate_suggestions():

    chosen = [c.val() for c in db.child("chosen").get().each()]
    top_suggestions = [{"id": -1, "name": "", "freq": -1, "main_freq": -1, "score": -1}] * no_suggestions
    for ingredient in ingredients.values():
        tot_sum = sum(freq_matrix[ingredients[chosen[i]]["id"]][ingredient["id"]]
                      for i in range(len(chosen)))
        worst = min(freq_matrix[ingredients[chosen[i]]["id"]][ingredient["id"]]
                    for i in range(len(chosen)))
        freq = ingredient["freq"]
        main_freq = ingredient["main_freq"]
        score = (main_freq + 1) * worst

        if score > top_suggestions[0]["score"] and ingredient["id"] not in chosen \
                and ingredient["name"] not in blacklist:
            ingredient["score"] = score
            top_suggestions[0] = ingredient
            top_suggestions = sorted(top_suggestions, key=itemgetter("score"))
    top_suggestions.reverse()

    # Category 3
    top_group_3 = [{"id": -1, "name": "", "freq": -1, "main_freq": -1, "score": -1}] * 10
    for ingredient in ingredients.values():
        if ingredient["freq"] < 100:
            tot_sum = sum(freq_matrix[ingredients[chosen[i]]["id"]][ingredient["id"]]
                          for i in range(len(chosen)))
            worst = min(freq_matrix[ingredients[chosen[i]]["id"]][ingredient["id"]]
                        for i in range(len(chosen)))
            freq = ingredient["freq"]
            main_freq = ingredient["main_freq"]
            score = (main_freq + 1) * worst

            if score > top_group_3[0]["score"] and ingredient["id"] not in chosen \
                    and ingredient["name"] not in blacklist and ingredient not in top_suggestions:
                ingredient["score"] = score
                top_group_3[0] = ingredient
                top_group_3 = sorted(top_group_3, key=itemgetter("score"))
    top_group_3.reverse()
    # top_suggestions.extend(top_group_3)

    # Category 4
    for ingredient in ingredients.values():
        if ingredient["freq"] < 100:
            tot_sum = sum(freq_matrix[ingredients[chosen[i]]["id"]][ingredient["id"]]
                          for i in range(len(chosen)))
            worst = min(freq_matrix[ingredients[chosen[i]]["id"]][ingredient["id"]]
                        for i in range(len(chosen)))
            freq = ingredient["freq"]
            main_freq = ingredient["main_freq"]
            score = (main_freq + 1) * worst

            if score > top_group_3[0]["score"] and ingredient["id"] not in chosen \
                    and ingredient["name"] not in blacklist and ingredient not in top_suggestions:
                ingredient["score"] = score
                top_group_3[0] = ingredient
                top_group_3 = sorted(top_group_3, key=itemgetter("score"))
    top_group_3.reverse()

    return top_suggestions


def generate_positions():
    # Get radii
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
    print('\nDone. Presented recipes:')
    top_recipes = 10 * [{"id": -1, "title": "", "image": "", "instructions": "", "ingredients": [],
                         "cooking_time": "", "categories": [], "nutr": "", "tags": [], "score": -1}]
    chosen = [k.val() for k in db.child("chosen").get().each()]
    for recipe in master:
        temp_score = 0
        for c in chosen:
            if c in recipe["aug_ingredients"]:
                temp_score += 1
        # TODO: weight in if there's an author
        if temp_score > top_recipes[0]["score"]:
            recipe["score"] = temp_score
            top_recipes[0] = recipe
            top_recipes = sorted(top_recipes, key=itemgetter("score"))
    top_recipes.reverse()
    db.child('recipes').set(top_recipes)
    for t in top_recipes:
        print("{} [{}] \n{}\n".format(t["title"], t["score"], t))
    return top_recipes

# ==================================================

if __name__ == "__main__":
    # Import data
    freq_matrix = pickle.load(open('Backend/data/freq_matrix.pickle', 'rb'))
    ingredients = pickle.load(open('Backend/data/ingredients.pickle', 'rb'))
    master = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
    blacklist = open('Backend/data/blacklist').read().lower().split("\n")

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

    # Enable command line interaction
    while True:
        c = input("Enter list index for the ingredient you want to choose: ")
        if c == "-d":
            done()
            input("\nPress a key to start over")
            clear()
        elif c == "-c":
            clear()
        else:
            new_choice(db.child('suggestions').child(str(c)).child('name').get().val())
