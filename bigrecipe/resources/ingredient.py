import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from bigrecipe.models import Ingredient
from bigrecipe import db
from bigrecipe.utils import BigrecipeBuilder, create_error_response
from bigrecipe.constants import *


class IngredientCollection(Resource):

    def get(self):
        body = BigrecipeBuilder()

        body.add_namespace("bigrec", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.ingredientcollection"))
        body.add_control_add_ingredient()
        body["items"] = []
        for db_ingredient in Ingredient.query.all():
            if db_ingredient.calories:
                item = BigrecipeBuilder(
                    name=db_ingredient.name,
                    unit=db_ingredient.unit,
                    calories=db_ingredient.calories,
                    description=db_ingredient.description
                )
            else:
                    item = BigrecipeBuilder(
                    name=db_ingredient.name,
                    unit=db_ingredient.unit,
                    description=db_ingredient.description
                )
            item.add_control("self", url_for("api.ingredientitem", ingredient=db_ingredient.name))
            item.add_control("profile", INGREDIENT_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Ingredient.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        ingredient = Ingredient(
            name=request.json["name"],
            unit=request.json["unit"],
            )
        try:
            calories = request.json["calories"]
            ingredient.calories=calories
        except KeyError:
            pass
        try:
            description = request.json["description"]
            ingredient.description=description
        except KeyError:
            pass
        try:
            db.session.add(ingredient)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Ingredient with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.ingredientitem", ingredient=request.json["name"])
        })


class IngredientItem(Resource):

    def get(self, ingredient):
        db_ingredient = Ingredient.query.filter_by(name=ingredient).first()
        if db_ingredient is None:
            return create_error_response(
                404, "Not found",
                "No ingredient was found with the name {}".format(ingredient)
            )

        body = BigrecipeBuilder(
            name=db_ingredient.name,
            unit=db_ingredient.unit,
            calories=db_ingredient.calories,
            description=db_ingredient.description
        )
        body.add_namespace("bigrec", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.ingredientitem", ingredient=ingredient))
        body.add_control("profile", INGREDIENT_PROFILE)
        body.add_control("collection", url_for("api.ingredientcollection"))
        body.add_control_delete_ingredient(ingredient)
        body.add_control_modify_ingredient(ingredient)
        body.add_control_get_recipes(ingredient)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, ingredient):
        db_ingredient = Ingredient.query.filter_by(name=ingredient).first()
        if db_ingredient is None:
            return create_error_response(
                404, "Not found",
                "No ingredient was found with the name {}".format(ingredient)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Ingredient.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_ingredient.name = request.json["name"]
        db_ingredient.unit = request.json["unit"]
        try:
            calories = request.json["calories"]
            db_ingredient.calories=calories
        except KeyError:
            pass
        try:
            description = request.json["description"]
            db_ingredient.description=description
        except KeyError:
            pass

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Ingredient with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=204)

    def delete(self, ingredient):
        db_ingredient = Ingredient.query.filter_by(name=ingredient).first()
        if db_ingredient is None:
            return create_error_response(
                404, "Not found",
                "No ingredient was found with the name {}".format(ingredient)
            )
        if db_ingredient.recipes:
            return create_error_response(
                403, "Forbidden",
                "Can't delete ingredient with paired recipes."
            )
        else:
            db.session.delete(db_ingredient)
            db.session.commit()

            return Response(status=204)