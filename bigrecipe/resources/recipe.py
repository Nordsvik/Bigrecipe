import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from bigrecipe.models import Ingredient, Recipe, Recingpairings
from bigrecipe import db
from bigrecipe.utils import BigrecipeBuilder, create_error_response
from bigrecipe.constants import *


class RecipeCollection(Resource):

    def get(self):
        
        try:
            start = int(request.args.get("start", 0))
            ingredient = str(request.args.get("ingredient"))
        except ValueError:
            return create_error_response(400, "Invalid query string value")

        db_ingredient = Ingredient.query.filter_by(name=ingredient).first()

        if db_ingredient is None:
            remaining = Recipe.query.order_by("name").offset(start)
        else:
            remaining = Recipe.query.join(Recingpairings).join(Ingredient).filter((Recingpairings.recipe_id == Recipe.id)
            & (Recingpairings.ingredient_id == db_ingredient.id)).order_by("name").offset(start)

        body = BigrecipeBuilder(
            items=[]
        )
        body.add_namespace("bigrec", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.recipecollection"))
        body.add_control_add_recipe()

        if db_ingredient:
            base_uri = url_for("api.recipecollection", ingredient=ingredient)
            body.add_control("bigrec:ingredient", url_for("api.ingredientitem", ingredient=ingredient))
        else:
            base_uri = url_for("api.recipecollection")
        if start >= 2 and db_ingredient:
            body.add_control("self", base_uri + "&start={}".format(start))
            body.add_control("prev", base_uri + "&start={}".format(start - RECIPE_PAGE_SIZE))
        elif start >= 2:
            body.add_control("self", base_uri + "?start={}".format(start))
            body.add_control("prev", base_uri + "?start={}".format(start - RECIPE_PAGE_SIZE))
        else:
            body.add_control("self", base_uri)
        if remaining.count() > 2 and db_ingredient:
            body.add_control("next", base_uri + "&start={}".format(start + RECIPE_PAGE_SIZE))
        elif remaining.count() > 2:
            body.add_control("next", base_uri + "?start={}".format(start + RECIPE_PAGE_SIZE))

        for rec in remaining.limit(RECIPE_PAGE_SIZE):
            if rec.description:
                item = BigrecipeBuilder(
                    name=rec.name,
                    description=rec.description,
                    text=rec.text
                )
            else:
                item = BigrecipeBuilder(
                    name=rec.name,
                    text=rec.text
                    )
            item.add_control("self", url_for("api.recipeitem", recipe=rec.name))
            item.add_control("profile", RECIPE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Recipe.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        try:
            recipe = Recipe(
                name=request.json["name"],
                description=request.json["description"],
                text=request.json["text"]
                )
        except KeyError:
                recipe = Recipe(
                name=request.json["name"],
                text=request.json["text"]
                )
        try:
            db.session.add(recipe)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Recipe with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.recipeitem", recipe=request.json["name"])
        })

class RecipeItem(Resource):

    def get(self, recipe):
        db_recipe = Recipe.query.filter_by(name=recipe).first()
        if db_recipe is None:
            return create_error_response(
                404, "Not found",
                "No recipe was found with the name {}".format(recipe)
            )
        body = BigrecipeBuilder(
            name=db_recipe.name,
            description=db_recipe.description,
            text=db_recipe.text
        )
        body.add_namespace("bigrec", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.recipeitem", recipe=recipe))
        body.add_control("profile", RECIPE_PROFILE)
        body.add_control("collection", url_for("api.recipecollection"))
        body.add_control_delete_recipe(recipe)
        body.add_control_modify_recipe(recipe)
        body.add_control_get_recingpairings(recipe)
        if db_recipe.drink:
            body.add_control_get_drink(db_recipe.drink.name)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, recipe):
        db_recipe = Recipe.query.filter_by(name=recipe).first()
        if db_recipe is None:
            return create_error_response(
                404, "Not found",
                "No recipe was found with the name {}".format(recipe)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Recipe.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_recipe.name = request.json["name"]
        db_recipe.text = request.json["text"]
        try:
            db_recipe.description = request.json["description"]
        except KeyError:
            pass

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Recipe with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=204)

    def delete(self, recipe):
        db_recipe = Recipe.query.filter_by(name=recipe).first()
        if db_recipe is None:
            return create_error_response(
                404, "Not found",
                "No recipe was found with the name {}".format(recipe)
            )

        if db_recipe.ingredients:
            return create_error_response(
                403, "Forbidden",
                "Can't delete recipe with paired ingredients."
            )
        else:
            db.session.delete(db_recipe)
            db.session.commit()

            return Response(status=204)

class RecipeIngredientPairing(Resource):

    def get(self, recipe):
        db_recipe = Recipe.query.filter_by(name=recipe).first()
        if db_recipe is None:
            return create_error_response(
                404, "Not found",
                "No recipe was found with the name {}".format(recipe)
            )
        ingamt={}
        for i in Recingpairings.query.join(Recipe).join(Ingredient).filter((Recingpairings.recipe_id == db_recipe.id)).order_by("name").all():
            q = Ingredient.query.filter_by(id = i.ingredient_id).first()
            ingamt[q.name] = i.amount, q.unit
        body = BigrecipeBuilder(
            ingredients = ingamt,
            recipe = db_recipe.name
        )
        body.add_namespace("bigrec", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.recipeingredientpairing", recipe=recipe))
        body.add_control_add_pairing(recipe)
        body.add_control_get_recipe(recipe)
        body.add_control_delete_pairing(recipe)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, recipe):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        try:
            validate(request.json, Recingpairings.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        recingpairing = Recingpairings(
            amount=request.json["amount"],
            recipe=Recipe.query.filter_by(name=request.json["recipe"]).first(),
            ingredient=Ingredient.query.filter_by(name=request.json["ingredient"]).first()
            )
        try:
            db.session.add(recingpairing)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Pairing for ingredient'{}' already exists.".format(request.json["ingredient"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.recipeingredientpairing", recipe=request.json["recipe"])
        })

    def delete(self, recipe):
        try:
            db_ingredient_name = request.json["ingredient"]
            db_recipe_name = request.json["recipe"]
        except TypeError:
            return create_error_response(
                404, "No such pairing found"
            )
        try:
            recid = Recipe.query.filter_by(name=db_recipe_name).first().id
            ingid = Ingredient.query.filter_by(name=db_ingredient_name).first().id
        except AttributeError:
            return create_error_response(
                404, "No such pairing found"
            )
        db_pairing = Recingpairings.query.filter((Recingpairings.recipe_id == recid) & (Recingpairings.ingredient_id == ingid)).first()
        if db_pairing is None:
            return create_error_response(
                404, "Not found",
                "No pairing was found with the input {}".format(db_recipe_name)+"{}".format(db_ingredient_name)
            )

        db.session.delete(db_pairing)
        db.session.commit()

        return Response(status=204)