from operator import itemgetter
import random
import pickle


def generate_suggestions(chosen_ingredients, n):
    if not chosen_ingredients:
        return top_frequent[:n]

    top_suggestions = [[-1, 'null', -1]] * n
    for col in range(len(ingredient_ids)):

        temp_sum = min(freq_matrix[chosen_ingredients[i][0]][col] for i in range(len(chosen_ingredients)))

        if temp_sum > top_suggestions[0][2] and col not in chosen_ingredients \
                and ingredient_ids[col][1] not in blacklist:
            top_suggestions[0] = [col, ingredient_ids[col][1], temp_sum]
            top_suggestions = sorted(top_suggestions, key=itemgetter(2))
    top_suggestions.reverse()
    return top_suggestions

# ==================================================

if __name__ == "__main__":
    # Import data
    freq_matrix = pickle.load(open('Backend/data/freq_matrix.pickle', 'rb'))
    top_frequent = pickle.load(open('Backend/data/top_frequent.pickle', 'rb'))
    ingredient_ids = pickle.load(open('Backend/data/ingredient_ids.pickle', 'rb'))
    blacklist = open('Backend/data/blacklist').read().lower().split("\n")
    print('\nModel loaded successfully.\n')

    try:
        feedback = pickle.load(open("Backend/data/feedback.pickle", "rb"))
    except FileNotFoundError:
        feedback = []

    no_suggestions = 20
    while True:
        # Generate random start of recipe
        no_chosen = random.randint(1, 4)
        chosen = []
        for i in range(no_chosen):
            suggestions = generate_suggestions(chosen, no_suggestions)
            chosen.append(suggestions[random.randint(0, len(suggestions) - 1)])

        # Present the start and the top suggestions
        print("You have ", end="")
        for c in chosen[:-1]:
            print("{}, ".format(ingredient_ids[c[0]][1]), end="")
        print("{}.\nNow asses the following suggestions:".format(ingredient_ids[chosen[-1][0]][1]), end="")
        print("")
        suggestions = generate_suggestions(chosen, no_suggestions)
        for s in suggestions:
            response = input("  {}: ".format(s[1]))
            # Skip this start of recipe
            if response == "-s":
                break
            # Quit
            if response == "-q":
                pickle.dump(feedback, open("Backend/data/feedback.pickle", "wb"))
                print("Saved feedback to Backend/data/feedback.pickle")
                raise SystemExit
            # If assessed
            while int(response) not in [-1, 0, 1]:
                print("  Answer with an integer between -1 and 1.")
                response = input("  {}: ".format(s[1]))
            feedback.append({"old": [c[0] for c in chosen], "new": s[0], "y": int(response)})
            pickle.dump(feedback, open("Backend/data/feedback.pickle", "wb"))
        print("")
