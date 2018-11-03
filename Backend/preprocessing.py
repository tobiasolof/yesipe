import numpy as np
import pickle
import regex as re
from Backend import ingr2vec
import json
import pprint


class Preprocessing(object):

    def __init__(self):
        self.recipes = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
        self.blacklist = open('Backend/data/blacklist.txt.txt').read().lower().split("\n")
        self.ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))

    def create_aliases(self):

        # Load ingr2vec model
        i2v = ingr2vec.Ingr2Vec()
        i2v.load('Backend/data/ingr2vec_model_200')

        # Load old session if there is one, otherwise start new
        try:
            # aliases structured as "original_name -> new_alias"
            aliases = open("Backend/data/aliases", "r").read().splitlines()
            # handled is a list of original names that has been taken care of
            handled = []
            for line in aliases:
                handled.append(re.search('.+->', line).group()[:-3])
        except FileNotFoundError:
            aliases = []
            handled = []

        # Ask for start index (useful if continuing on earlier session)
        start = int(input("Enter start index: "))
        print("")
        # Loop over all ingredients and list most similar vectors and most similar words for each
        for i, ingredient in enumerate(list(sorted(self.ingredients))[start:]):
            if ingredient not in handled:
                similar = []
                count = 0
                # List similar strings
                print("Similar strings:")
                for s in i2v.similar_strings(ingredient, n=15):
                    similar.append(s[0])
                    print("    {0: <3}: {1} - {2:.2f}".format(count, s[0], s[1]))
                    count += 1
                # List similar ingredients based on their vectors
                try:
                    print("Similar vectors:")
                    for s in i2v.similar_vectors(ingredient, n=15):
                        similar.append(s[0])
                        print("    {0: <3}: {1} - {2:.2f}".format(count, s[0], s[1]))
                        count += 1
                # Exception if the current ingredient does not have a vector
                except KeyError:
                    pass

                # Choose from the list all synonyms to the current ingredient
                chosen_indices = input("Enter indices for duplicates to '{}': ".format(ingredient)).split()
                # -q to stop
                if chosen_indices[0] == "-q":
                    print("\nTo continue, start at index {} next time.".format(start + i))
                    break
                # -r to remove a bad string
                if chosen_indices[0] in ["-b", "-r"]:
                    with open("Backend/data/blacklist.txt.txt", "a") as blacklist:
                        blacklist.write("\n{}".format(ingredient))
                    print("Blacklisted '{}'\n\n".format(ingredient))
                    continue

                # Enter the name that all these synonyms (including current ingredient) should be called
                chosen_indices = [int(c) for c in chosen_indices]
                desired_name = input("Enter desired name of these ingredients [{}]: ".format(ingredient))
                # Empty string interpreted as current string should be used
                if desired_name == "":
                    desired_name = ingredient

                # Add rows to alias list
                for c in chosen_indices:
                    aliases.append("{} -> {}".format(similar[c], desired_name))
                    handled.append(similar[c])

                # Write to file
                with open("Backend/data/aliases", "w") as file:
                    for line in sorted(list(set(aliases))):
                        file.writelines("{}\n".format(line))
                print("\n\n")

        # Write to file
        with open("Backend/data/aliases", "w") as file:
            for line in sorted(list(set(aliases))):
                file.writelines("{}\n".format(line))

        # Search for duplicates
        for i, row in enumerate(aliases):
            current = re.search(".+->", row).group()[:-3]
            if re.search(".+->", aliases[i + 1]).group()[:-3] == current:
                print(current)

    def update_to_aliases(self):
        temp_aliases = open('Backend/data/aliases').read().splitlines()
        aliases = {}
        for line in temp_aliases:
            old_name = re.search('.+->', line).group()[:-3]
            new_name = re.search('->.+', line).group()[3:]
            if new_name != old_name:
                aliases[old_name] = {"old_name": old_name, "new_name": new_name}
        for r in self.recipes:
            r["ingredients_true"] = r["ingredients"].copy()
            for i, ingredient in enumerate(r["ingredients"]):
                if ingredient in aliases:
                    r["ingredients"][i] = aliases[ingredient]["new_name"]
            for i, ingredient in enumerate(r["aug_ingredients"]):
                if ingredient in aliases:
                    ingredient = aliases[ingredient]["new_name"]
            for i, ingredient in enumerate(r["categories"]):
                if ingredient in aliases:
                    r["categories"][i] = aliases[ingredient]["new_name"]
            for i, ingredient in enumerate(r["tags"]["main_ingr"]):
                if ingredient in aliases:
                    r["tags"]["main_ingr"][i] = aliases[ingredient]["new_name"]
        with open('Backend/data/tasteline.json', 'w') as f:
            json.dump(self.recipes, f)
            print("Wrote {} recipes to {}".format(len(self.recipes), "tasteline.json"))
        with open('Backend/data/tasteline.pickle', 'wb') as f:
            pickle.dump(self.recipes, f)
            print("Wrote {} recipes to {}".format(len(self.recipes), "tasteline.pickle"))

    def fix_broken_categories(self):
        # Fix broken categories
        for r in self.recipes:
            for i, category in enumerate(r["categories"]):
                if "href" in category:
                    categories = re.sub("<\/span>.*\/\">", ",", category).split(",")
                    r["categories"][i] = categories[0]
                    r["categories"].append(categories[1])
                    print(r["categories"])
        pickle.dump(self.recipes, open('Backend/data/tasteline.pickle', 'wb'))
        json.dump(self.recipes, open('Backend/data/tasteline.json', 'w'))

    def fix_amp(self):
        # Fix "&amp;"
        for r in self.recipes:
            for i, ingredient in enumerate(r["ingredients"]):
                if "&amp;" in ingredient:
                    ingredient = re.sub("&amp;", "&", ingredient)
                    r["ingredients"][i] = ingredient
                    print(r["ingredients"])
        pickle.dump(self.recipes, open('Backend/data/tasteline.pickle', 'wb'))
        json.dump(self.recipes, open('Backend/data/tasteline.json', 'w'))

    def add_categories_to_aug_ingredients(self):
        for r in self.recipes:
            r["aug_ingredients"] = r["ingredients"]
            for category in r["categories"]:
                if category not in r["aug_ingredients"]:
                    r["aug_ingredients"].append(category)
            pprint.pprint(r["aug_ingredients"])
        pickle.dump(self.recipes, open('Backend/data/tasteline.pickle', 'wb'))
        json.dump(self.recipes, open('Backend/data/tasteline.json', 'w'))

    def write_ingredients_to_file(self):
        # Ingredient IDs, frequency and "main frequency"
        ingredients = []
        for r in self.recipes:
            ingredients.extend(r['aug_ingredients'])
        unique_ingredients = list(set(ingredients))
        unique_ingredients.sort()
        ingredients = {}
        percent = 0
        for i, ingredient in enumerate(unique_ingredients):
            freq = 0
            main_freq = 0
            for r in self.recipes:
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

    def write_freq_matrix_to_file(self):
        # Co-occurrence matrix
        unique_ingredients = list(set(self.ingredients))
        unique_ingredients.sort()
        freq_matrix = np.zeros((len(unique_ingredients), len(unique_ingredients)))
        percent = 0
        for count, r in enumerate(self.recipes):
            temp_ingredients = r['aug_ingredients']
            for i, first_ingredient in enumerate(temp_ingredients):
                for second_ingredient in temp_ingredients[i+1:]:
                    a = self.ingredients[first_ingredient]["id"]
                    b = self.ingredients[second_ingredient]["id"]
                    freq_matrix[a][b] += 1
                    freq_matrix[b][a] += 1
            if round(100 * count/len(self.recipes)) > percent:
                percent = round(100 * count/len(self.recipes))
                print("1: {0:d}%".format(percent))
            print('{}%'.format(int(100*count/len(self.recipes))), end=" ")
        with open('Backend/data/freq_matrix.pickle', 'wb') as f:
            pickle.dump(freq_matrix, f)

    def categories_to_keep(self):
        blacklist = open('Backend/data/blacklist.txt.txt').read().lower().split("\n")
        categories = {}
        no_list = []
        for r in self.recipes:
            for i, category in enumerate(r["categories"]):
                if category not in r["tags"]["main_ingr"] and category not in blacklist:
                    if category in categories:
                        categories[category]["freq"] += 1
                    else:
                        if category not in no_list:
                            include = input("Include '{}'? (y/n): ".format(category))
                            if include == "y":
                                categories[category] = {"name": category, "freq": 1}
                            if include == "n":
                                no_list.append(category)
        with open("Backend/data/categories", "w") as file:
            file.write(str(categories))

if __name__ == "__main__":
    p = Preprocessing()
