import bs4
import requests
import regex as re
import json
import pickle
from multiprocessing import Pool


def get_links(prefix="http://www.tasteline.com/recept/", page_number=1):
    url = prefix + "?sida={}".format(page_number)
    html_doc = requests.get(url).text
    parse_tree = bs4.BeautifulSoup(html_doc, "html.parser")
    recipe_descriptions = parse_tree.find_all("div", "recipe-description")
    link_list = []
    for element in recipe_descriptions:
        link = str(element.a)
        link_list.append(re.search("http:" + ".+/\"", link).group()[:-1])
    return link_list


def get_ingredients(parse_tree):
    ingredient_group = parse_tree.find_all("div", "ingredient-group")
    ingredient_list = []
    for i in ingredient_group:
        temp_ingredient_list = [re.findall("ingredients\">.+<", str(i))][0]
        temp_ingredient_list = [re.search(">.+?<", i).group().lower()[1:-1] for i in temp_ingredient_list]
        temp_ingredient_list = [i.strip() for i in temp_ingredient_list]
        ingredient_list.extend(temp_ingredient_list)
    return ingredient_list


def get_instructions(parse_tree):
    step_group = parse_tree.find_all("div", "step-group")
    step_list = []
    for s in step_group:
        temp_step_list = []
        for element in s:
            p = re.compile('<li>[0-9]+\..+<|<h3>.+<')
            temp_step_list.extend(re.findall(p, str(element)))
        temp_step_list = [s[4:-1] for s in temp_step_list]
        step_list.extend(temp_step_list)
    step_list = "\n\n".join(step_list)
    return step_list


def get_image(parse_tree):
    header = parse_tree.find_all("div", "recipe-header-image")
    image = re.search("http:" + ".+\"?", str(header)).group()[:-2]
    return image


def get_title(parse_tree):
    recipe_description = parse_tree.find_all("div", "recipe-description")
    title = re.search("<h1 itemprop=\"name\">.+</h1>", str(recipe_description)).group()[20:-5]
    return title


def get_nutrition_fact(parse_tree):
    nutritional_facts = parse_tree.find_all("div", "nutritional-facts")
    elements = re.findall("<li>.+?<\/li>", str(nutritional_facts))
    nutritional_facts = []
    for e in elements:
        key = re.search("<li>.+<span", e).group()[4:-6]
        value = re.search(">[\p{N}\p{P}]+?<\/span>", e).group()[1:-7]
        temp = " ".join([key, value])
        try:
            unit = re.search("<\/span>.+?<\/li>", e).group()[7:-5].strip()
            temp = " ".join([temp, unit])
        except AttributeError:
            pass
        nutritional_facts.append(temp)
    return nutritional_facts


def get_categories(parse_tree):
    category_list = parse_tree.find_all("div", "category-list")[0]
    categories = re.findall("href.*>.+?</a>", str(category_list))
    categories = re.findall(">.+?</a>", str(categories))
    category_list = [c[1:-4].lower().strip() for c in categories]
    return category_list


def get_cooking_time(parse_tree):
    try:
        recipe_description = parse_tree.find_all("div", "recipe-description")
        time = re.search("clock-o\"><\/i>.+?<time", str(recipe_description)).group()
        time = re.search("i>.+<", time).group()
        time = time[2:-1].strip()
        return time
    except AttributeError:
        return ""


def extract_tag(tags, t, one=False):
    for element in tags:
        try:
            match = re.search(t + "\"\].+\];", element).group()
            match = re.search("\[\".+\"", match).group()
            match = re.sub("[\[\"]", "", match)
            match = re.sub("\\\\u00e5", "å", match)
            match = re.sub("\\\\u00e4", "ä", match)
            match = re.sub("\\\\u00f6", "ö", match)
            match = re.sub("\\\\u00e9", "é", match)
            matches = match.split(",")
            matches = [m for m in matches if re.search("\p{L}", m) is not None]
            if one:
                matches = [matches[0]]
            break
        except AttributeError:
            matches = []
    return matches


def get_tags(parse_tree):
    str_tree = str(parse_tree)
    tags = re.findall("window\.Fusion\.parameters.*;", str_tree)
    tags = [re.sub("\\t", " ", t) for t in tags]
    tags = [re.sub(" +", " ", t) for t in tags]
    return tags


def get_recipes(p):
    batch = []
    for i in range(1, 51):
        links = get_links(prefix=p, page_number=i)
        for l in links:
            try:
                html_doc = requests.get(l).text
                parse_tree = bs4.BeautifulSoup(html_doc, "html.parser")

                title = get_title(parse_tree)
                image = get_image(parse_tree)
                instructions = get_instructions(parse_tree)
                ingredients = get_ingredients(parse_tree)
                cooking_time = get_cooking_time(parse_tree)
                categories = get_categories(parse_tree)
                nutr = get_nutrition_fact(parse_tree)

                tags = get_tags(parse_tree)
                author = extract_tag(tags, "receptskapare", one=True)
                occasion = extract_tag(tags, "tillfalle")
                kitchen = extract_tag(tags, "kok")
                main_type = extract_tag(tags, "huvudtyp")
                recipe_type = extract_tag(tags, "typ_av_recept")
                dish_type = extract_tag(tags, "typ_av_ratt")
                main_ingr = extract_tag(tags, "huvudingrediens")
                tags = {"author": author, "occasion": occasion, "kitchen": kitchen, "main_type": main_type,
                        "recipe_type": recipe_type, "dish_type": dish_type, "main_ingr": main_ingr}

                entry = {"id": l, "title": title, "image": image, "instructions": instructions, "ingredients": ingredients,
                         "cooking_time": cooking_time, "categories": categories, "nutr": nutr, "tags": tags}
                batch.append(entry)
            except:
                print("EXCEPTION. Skipped {}".format(l))
    print("Finished scraping {}".format(p))
    return batch

# ===============================

if __name__ == "__main__":
    p = Pool(50)
    prefix_list = open("Backend/data/tasteline_url").read().split("\n")
    category_map = p.map(get_recipes, prefix_list)
    print("\nFinished threaded scraping.\n")

    master_index = []
    for batch in category_map:
        for recipe in batch:
            if recipe not in master_index:
                master_index.append(recipe)

    with open('Backend/data/tasteline_2.json', 'w') as f:
        json.dump(master_index, f)
        print("Wrote {} recipes to {}".format(len(master_index), "tasteline.json"))

    with open('Backend/data/tasteline_2.pickle', 'wb') as f:
        pickle.dump(master_index, f)
        print("Wrote {} recipes to {}".format(len(master_index), "tasteline.pickle"))
