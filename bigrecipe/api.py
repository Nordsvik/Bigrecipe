from flask import Blueprint
from flask_restful import Api

from bigrecipe.resources.ingredient import IngredientCollection, IngredientItem
from bigrecipe.resources.recipe import RecipeItem, RecipeCollection, RecipeIngredientPairing
from bigrecipe.resources.drink import DrinkItem, DrinkCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(RecipeCollection, "/recipes/")
api.add_resource(RecipeItem, "/recipes/<recipe>/")
api.add_resource(IngredientCollection, "/ingredients/")
api.add_resource(IngredientItem, "/ingredients/<ingredient>/")
api.add_resource(DrinkCollection, "/drinks/")
api.add_resource(DrinkItem, "/drinks/<drink>/")
api.add_resource(RecipeIngredientPairing, "/recipes/<recipe>/ingredients/")