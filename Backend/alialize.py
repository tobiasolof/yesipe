import pickle
import regex as re
from Backend import search

# Load ingredient dictionary
ingredients = pickle.load(open("Backend/data/ingredients.pickle", "rb"))
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
for i, ingredient in enumerate(list(sorted(ingredients))[start:]):
    if ingredient not in handled:
        similar = []
        count = 0
        # List similar strings
        print("Similar strings:")
        for s in search.similar_strings(ingredient, n=15):
            similar.append(s[0])
            print("    {0: <3}: {1} - {2:.2f}".format(count, s[0], s[1]))
            count += 1
        # List similar ingredients based on their vectors
        try:
            print("Similar vectors:")
            for s in search.similar_vectors(ingredient, n=15):
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
            with open("Backend/data/blacklist", "a") as blacklist:
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
    if re.search(".+->", aliases[i+1]).group()[:-3] == current:
        print(current)
