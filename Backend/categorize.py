import pickle

# Read in data
recipes = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
print("Number of recipes: {}".format(len(recipes)))
blacklist = open('Backend/data/blacklist').read().lower().split("\n")

ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))
categories = {}
no_list = []
for r in recipes:
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
