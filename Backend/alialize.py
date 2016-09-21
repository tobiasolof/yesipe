import pickle
import regex as re
from Backend import search

ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))
try:
    aliases = open("Backend/data/aliases", "r").read().splitlines()
    handled = []
    for line in aliases:
        handled.append(re.search('.+->', line).group()[:-3])
except FileNotFoundError:
    aliases = []
    handled = []

start = int(input("Enter start index: "))
print("")
for i, ingredient in enumerate(list(sorted(ingredients))[start:]):
    if ingredient not in handled:
        similar = []
        count = 0
        print("Similar strings:")
        for s in search.similar_strings(ingredient, n=15):
            similar.append(s[0])
            print("    {0: <3}: {1} - {2:.2f}".format(count, s[0], s[1]))
            count += 1
        try:
            print("Similar vectors:")
            for s in search.similar_vectors(ingredient, n=15):
                similar.append(s[0])
                print("    {0: <3}: {1} - {2:.2f}".format(count, s[0], s[1]))
                count += 1
        except KeyError:
            pass

        chosen_indices = input("Enter indices for duplicates to '{}': ".format(ingredient)).split()
        # -q to stop
        if chosen_indices[0] == "-q":
            print("\nTo continue, start at index {} next time.".format(start + i))
            break
        # -r to remove a bad string
        if chosen_indices[0] in ["-b", "-r"]:
            with open("Backend/data/blacklist", "a") as blacklist:
                blacklist.write("\n{}".format(ingredient))
            print("Blacklisted '{}'\n\n".format(ingredient))
            continue

        chosen_indices = [int(c) for c in chosen_indices]
        desired_name = input("Enter desired name of these ingredients [{}]: ".format(ingredient))
        if desired_name == "":
            desired_name = ingredient

        for c in chosen_indices:
            aliases.append("{} -> {}".format(similar[c], desired_name))
            handled.append(similar[c])

        with open("Backend/data/aliases", "w") as file:
            for line in sorted(list(set(aliases))):
                file.writelines("{}\n".format(line))
        print("\n\n")

with open("Backend/data/aliases", "w") as file:
    for line in sorted(list(set(aliases))):
        file.writelines("{}\n".format(line))

for i, row in enumerate(aliases):
    current = re.search(".+->", row).group()[:-3]
    if re.search(".+->", aliases[i+1]).group()[:-3] == current:
        print(current)
