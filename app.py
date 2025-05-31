from flask import Flask, request, render_template, redirect, url_for
import os
import json

app = Flask(__name__)
RECIPES_DIR = "recipes"
if not os.path.exists(RECIPES_DIR):
    os.makedirs(RECIPES_DIR)

# Home route to list recipes
@app.route('/')
def home():
    recipes = []
    for filename in os.listdir(RECIPES_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(RECIPES_DIR, filename), "r") as file:
                data = json.load(file)
                recipes.append({
                    "title": data["title"],
                    "url": url_for('view_recipe', recipe_id=filename[:-5]),  # Generates correct URL
                    "tags": data.get("tags", [])
                })
    return render_template("index.html", recipes=recipes)

# Route to add a new recipe
@app.route('/add', methods=['POST'])
def add_recipe():
    data = request.form.to_dict()
    data["ingredients"] = data.get("ingredients", "").split("\n")
    data["directions"] = data.get("directions", "").split("\n")
    data["tags"] = [tag.strip() for tag in data.get("tags", "").split(",") if tag.strip()]
    recipe_id = data['title'].replace(" ", "_").lower()
    filepath = os.path.join(RECIPES_DIR, f"{recipe_id}.json")
    
    with open(filepath, "w") as file:
        json.dump(data, file)
    
    return redirect(url_for('home'))  # Redirects to homepage after adding a recipe

# Route to view a recipe
@app.route('/recipe/<recipe_id>')
def view_recipe(recipe_id):
    filepath = os.path.join(RECIPES_DIR, f"{recipe_id}.json")
    if not os.path.exists(filepath):
        return "Recipe not found", 404
    with open(filepath, "r") as file:
        recipe = json.load(file)
    return render_template("recipe.html", recipe=recipe)

# Route to delete a recipe
@app.route('/delete/<recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    filepath = os.path.join(RECIPES_DIR, f"{recipe_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('home'))  # Redirects to homepage after deleting a recipe

# Search function
@app.route('/search')
def search():
    query = request.args.get("q", "").lower()
    results = []
    for filename in os.listdir(RECIPES_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(RECIPES_DIR, filename), "r") as file:
                data = json.load(file)
                if query in data["title"].lower() or any(query in ing.lower() for ing in data.get("ingredients", [])):
                    results.append({
                        "title": data["title"],
                        "url": url_for('view_recipe', recipe_id=filename[:-5]),
                        "tags": data.get("tags", [])
                    })
    return render_template("search.html", results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
