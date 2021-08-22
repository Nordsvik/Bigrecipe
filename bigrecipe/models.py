import click
from flask.cli import with_appcontext
from bigrecipe import db

"""
Started out with the sensorhub project template,
mostly as a starting point for utils and admin.js, all
other code is original
"""


#Association table so amount can be added
class Recingpairings(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id", ondelete='CASCADE'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id", ondelete='CASCADE'), primary_key=True)
    amount = db.Column(db.Integer)

    recipe = db.relationship("Recipe", back_populates="ingredients")
    ingredient = db.relationship("Ingredient", back_populates="recipes")

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["amount", "recipe", "ingredient"]
        }
        props = schema["properties"] = {}
        props["recipe"] = {
            "description": "Recipe's unique name",
            "type": "string"
        }
        props["ingredient"] = {
            "description": "Ingredient's unique name",
            "type": "string"
        }
        props["amount"] = {
            "description": "Amount of ingredient",
            "type": "number"
        }
        return schema

#Basic model definitions below

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drink_id = db.Column(db.Integer, db.ForeignKey("drink.id", ondelete="SET NULL"))
    name = db.Column(db.String, unique=True, nullable=False)
    description=db.Column(db.String(256), nullable=True)
    text=db.Column(db.String, nullable=False)

    ingredients = db.relationship("Recingpairings", back_populates="recipe")

    drink = db.relationship("Drink", back_populates="recipes")

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "text"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Recipe's unique name",
            "type": "string"
        }
        props["text"] = {
            "description": "The text body of the recipe.",
            "type": "string"
        }
        props["description"] = {
            "description": "Short introductory description of the recipe.",
            "type": "string"
        }
        return schema

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    unit = db.Column(db.String, nullable=False)
    calories = db.Column(db.Integer, nullable=True)
    description=db.Column(db.String(256), nullable=True)

    recipes = db.relationship("Recingpairings", back_populates="ingredient")

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "unit"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Ingredient's unique name",
            "type": "string"
        }
        props["unit"] = {
            "description": "Ingredient's single unit measurement (e.g. whole, grams, cup)",
            "type": "string"
        }
        props["calories"] = {
            "description": "Caloric value of the ingredient per unit",
            "type": "number"
        }
        props["description"] = {
            "description": "Description of the ingredient",
            "type": "string"
        }
        return schema


class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    alcohol = db.Column(db.Boolean, nullable=False, default=False)
    description=db.Column(db.String(512), nullable=True)

    recipes = db.relationship("Recipe", back_populates="drink")

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "alcohol"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Drink's unique name",
            "type": "string"
        }
        props["alcohol"] = {
            "description": "Is the drink alcoholic, True/False",
            "type": "boolean"
        }
        props["description"] = {
            "description": "Description of the drink",
            "type": "string"
        }
        props["recipe"] = {
            "description": "Name of the associated recipe",
            "type": "string"
        }
        return schema

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

@click.command("testgen")
@with_appcontext
def generate_test_data():

    r = Recipe(
        name="Nice Stew",
        description="A stew for folks",
        text="Make a big stew then eat it."
    )


    r2 = Recipe(
        name="Cool Chili",
        description="A chili for folks",
        text="Make chili then eat it."
    )

    r3 = Recipe(
        name="Hamburger Sandwich",
        description="Scrom nom nom",
        text="Om nom nom"
        )

    iii = Ingredient(
        name="Burger Meat",
        unit="g",
        calories=2,
        description="Flame it up"
        )


    i = Ingredient(
        name="Garlic",
        unit="whole",
        calories=12,
        description="Nice garlic"
        )

    d = Drink(
        name="Bad Beer",
        alcohol=True,
        description="You don't have to drink it but it helps."
        )


    ii = Ingredient(
        name="Whole Grain Rice",
        unit="g",
        calories=1,
        description="Nice rice"
        )

    

    r.drink = d

    db.session.add(r)
    db.session.add(r2)
    db.session.add(r3)
    db.session.add(i)
    db.session.add(ii)
    db.session.add(iii)
    db.session.commit()


@click.command("assocgen")
@with_appcontext
def generate_associations():

    a = Recingpairings(amount=4, recipe=Recipe.query.filter_by(name="Cool Chili").first(), ingredient=Ingredient.query.filter_by(name="Garlic").first())

    a2 = Recingpairings(amount=200, recipe=Recipe.query.filter_by(name="Cool Chili").first(), ingredient=Ingredient.query.filter_by(name="Whole Grain Rice").first())

    a3 = Recingpairings(amount=4, recipe=Recipe.query.filter_by(name="Nice Stew").first(), ingredient=Ingredient.query.filter_by(name="Garlic").first())


    db.session.add(a)
    db.session.add(a2)
    db.session.add(a3)
    db.session.commit()


@click.command("extestgen")
@with_appcontext
def generate_test_data_existing():
   pass

@click.command("arbtest")
@with_appcontext
def arbitrary_test():
    print(Recipe.query.all())
    print(Recipe.query.filter_by(name="Cool Chili").first().drink.name)
    print(Recingpairings.query.filter_by(recipe=Recipe.query.filter_by(name="Cool Chili").first(), ingredient = Ingredient.query.filter_by(name="Garlic").first()))
    db_ingredient = Ingredient.query.first()
    db_ingredient = Ingredient.query.filter_by(id=2).first()
    print(db_ingredient.id)
    print(Recipe.query.first().ingredients)
    print(Recipe.query.join(Recingpairings).join(Ingredient).filter((Recingpairings.c.recipe_id == Recipe.id) & (Recingpairings.c.ingredient_id == db_ingredient.id)).all())