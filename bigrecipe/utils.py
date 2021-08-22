import json
from flask import Response, request, url_for
from bigrecipe.constants import *
from bigrecipe.models import *

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

"""
Control definitions using the methods above
"""

class BigrecipeBuilder(MasonBuilder):

    def add_control_get_recipes_by_ingredient(self, ingredient):
        base_uri = url_for("api.recipecollection", ingredient=ingredient)
        uri = base_uri + "?start={index}"
        self.add_control(
            "bigrec:recipesbying",
            uri,
            isHrefTemplate=True,
            schema=self._paginator_schema()
        )

    def add_control_add_recipe(self):
        self.add_control(
            "bigrec:add-recipe",
            url_for("api.recipecollection"),
            method="POST",
            encoding="json",
            title="Add a new Recipe",
            schema=Recipe.get_schema()
        )

    def add_control_add_pairing(self, recipe):
        self.add_control(
            "bigrec:add-pairing",
            url_for("api.recipeingredientpairing", recipe=recipe),
            method="POST",
            encoding="json",
            title="Add a new Ingredient to Recipe",
            schema=Recingpairings.get_schema()
        )

    def add_control_add_ingredient(self):
        self.add_control(
            "bigrec:add-ingredient",
            url_for("api.ingredientcollection"),
            method="POST",
            encoding="json",
            title="Add a new Ingredient",
            schema=Ingredient.get_schema()
        )

    def add_control_add_drink(self):
        self.add_control(
            "bigrec:add-drink",
            url_for("api.drinkcollection"),
            method="POST",
            encoding="json",
            title="Add a new Drink",
            schema=Drink.get_schema()
        )

    def add_control_get_recipe(self, recipe):
        self.add_control(
            "bigrec:recipe",
            url_for("api.recipeitem", recipe=recipe)
        )

    def add_control_get_drink(self, drink):
        self.add_control(
            "bigrec:drink",
            url_for("api.drinkitem", drink=drink)
        )

    def add_control_delete_recipe(self, recipe):
        self.add_control(
            "bigrec:delete",
            url_for("api.recipeitem", recipe=recipe),
            method="DELETE",
            title="Delete this recipe"
        )

    def add_control_delete_pairing(self, recipe):
        self.add_control(
            "bigrec:delete-pairing",
            url_for("api.recipeingredientpairing", recipe=recipe),
            method="DELETE",
            title="Give an ingredient to remove from this recipe"
        )

    def add_control_delete_drink(self, drink):
        self.add_control(
            "bigrec:delete",
            url_for("api.drinkitem", drink=drink),
            method="DELETE",
            title="Delete this drink"
        )

    def add_control_delete_ingredient(self, ingredient):
        self.add_control(
            "bigrec:delete",
            url_for("api.ingredientitem", ingredient=ingredient),
            method="DELETE",
            title="Delete this ingredient"
        )

    def add_control_modify_recipe(self, recipe):
        self.add_control(
            "edit",
            url_for("api.recipeitem", recipe=recipe),
            method="PUT",
            encoding="json",
            title="Edit this recipe",
            schema=Recipe.get_schema()
        )

    def add_control_modify_ingredient(self, ingredient):
        self.add_control(
            "edit",
            url_for("api.ingredientitem", ingredient=ingredient),
            method="PUT",
            encoding="json",
            title="Edit this ingredient",
            schema=Ingredient.get_schema()
        )

    def add_control_modify_drink(self, drink):
        self.add_control(
            "edit",
            url_for("api.drinkitem", drink=drink),
            method="PUT",
            encoding="json",
            title="Edit this drink",
            schema=Drink.get_schema()
        )

    def add_control_get_recingpairings(self, recipe):
        uri = url_for("api.recipeingredientpairing", recipe=recipe)
        self.add_control(
            "bigrec:ingredients",
            uri,
            isHrefTemplate=True,
        )

    def add_control_get_recipes(self, ingredient):
        base_uri = url_for("api.recipecollection", ingredient=ingredient)
        uri = base_uri + "?start={index}"
        self.add_control(
            "bigrec:recipes",
            uri,
            isHrefTemplate=True,
            schema=self._paginator_schema()
        )

    @staticmethod
    def _paginator_schema():
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        props = schema["properties"]
        props["index"] = {
            "description": "Starting index for pagination",
            "type": "integer",
            "default": "0"
        }
        return schema

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
