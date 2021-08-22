import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from bigrecipe.models import Drink, Recipe
from bigrecipe import db
from bigrecipe.utils import BigrecipeBuilder, create_error_response
from bigrecipe.constants import *


class DrinkCollection(Resource):

    def get(self):
        body = BigrecipeBuilder()

        body.add_namespace("bigrec", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.drinkcollection"))
        body.add_control_add_drink()
        body["items"] = []
        for db_drink in Drink.query.all():
            if db_drink.description:
                item = BigrecipeBuilder(
                    name=db_drink.name,
                    alcohol=db_drink.alcohol,
                    description=db_drink.description
                )
            else:
                item = BigrecipeBuilder(
                    name=db_drink.name,
                    alcohol=db_drink.alcohol,
                )
            item.add_control("self", url_for("api.drinkitem", drink=db_drink.name))
            item.add_control("profile", DRINK_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Drink.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        try:
            drink = Drink(
                name=request.json["name"],
                alcohol=request.json["alcohol"],
                description=request.json["description"]
                )
        except KeyError:
            drink = Drink(
                name=request.json["name"],
                alcohol=request.json["alcohol"]
                )
        try:
            db.session.add(drink)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Drink with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.drinkitem", drink=request.json["name"])
        })


class DrinkItem(Resource):

    def get(self, drink):
        db_drink = Drink.query.filter_by(name=drink).first()
        if db_drink is None:
            return create_error_response(
                404, "Not found",
                "No drink was found with the name {}".format(drink)
            )

        body = BigrecipeBuilder(
            name=db_drink.name,
            alcohol=db_drink.alcohol,
            description=db_drink.description
        )
        body.add_namespace("bigrec", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.drinkitem", drink=drink))
        body.add_control("profile", DRINK_PROFILE)
        body.add_control("collection", url_for("api.drinkcollection"))
        body.add_control_delete_drink(drink)
        body.add_control_modify_drink(drink)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, drink):
        db_drink = Drink.query.filter_by(name=drink).first()
        if db_drink is None:
            return create_error_response(
                404, "Not found",
                "No drink was found with the name {}".format(drink)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Drink.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_drink.name = request.json["name"]
        db_drink.alcohol = request.json["alcohol"]
        try:
            db_drink.description = request.json["description"]
        except KeyError:
            pass

        try:
            if Recipe.query.filter_by(name=request.json["recipe"]).first():
                db_drink.recipes.append(Recipe.query.filter_by(name=request.json["recipe"]).first())
        except KeyError:
            pass

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Drink with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=204)

    def delete(self, drink):
        db_drink = Drink.query.filter_by(name=drink).first()
        if db_drink is None:
            return create_error_response(
                404, "Not found",
                "No drink was found with the name {}".format(drink)
            )

        db.session.delete(db_drink)
        db.session.commit()

        return Response(status=204)
