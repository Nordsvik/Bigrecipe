"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function recipeRow(item) {
    let link = "<a href='" +
        item["@controls"].self.href +
        "' onClick='followLink(event, this, renderRecipe)'>show</a>";

    return "<tr><td>" + item.name +
        "</td><td>" + item.description +
        "</td><td>" + link + "</td></tr>";
}

function ingredientRow(item) {
    let link = "<a href='" +
        item["@controls"].self.href +
        "' onClick='followLink(event, this, renderIngredient)'>show</a>";

    return "<tr><td>" + item.name +
        "</td><td>" + item.unit +
        "</td><td>" + item.calories +
        "</td><td>" + link + "</td></tr>";
}

function drinkRow(item) {
    let link = "<a href='" +
        item["@controls"].self.href +
        "' onClick='followLink(event, this, renderDrink)'>show</a>";

    return "<tr><td>" + item.name +
        "</td><td>" + item.alcohol  + 
        "</td><td>" + link + "</td></tr>";
}

function pairingRow(ingredient, unit, amount) {

    return "<tr><td>" + ingredient +
        "</td><td>" + unit +
        "</td><td>" + amount +
        "</td></tr>";
}


function appendRecipeRow(body) {
    $(".resulttable tbody").append(recipeRow(body));
}


function appendIngredientRow(body) {
    $(".resulttable tbody").append(ingredientRow(body));
}

function appendDrinkRow(body) {
    $(".resulttable tbody").append(drinkRow(body));
}

function deletePairing(body) {
    deletePairingForm(body["@controls"]["bigrec:delete-pairing"]);
    $("input[name='recipe']").val(body["recipe"]);
    $("input[name='amount']").val(1);
}

function deletePairingForm(ctrl) {
    let form = $("<form>");
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitPairing);
    form.append("<h1>Delete which pairing?</h1>");
    form.append("<label>" + "Ingredient" + "</label>");
    form.append("<input type='text' name='ingredient'>");
    form.append("<label>" + "Recipe" + "</label>");
    form.append("<input type='text' name='recipe' disabled>");
    form.append("<input type='number' name='amount' value='1' hidden>");
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}


function submitRecipe(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form"); //DIV1 IN CSS, DON'T KNOW IF WRAPPING WORKS
    data.name = $("input[name='name']").val();
    data.description = $("input[name='description']").val();
    data.text = $("textarea[name='text']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedRecipe);
}

function submitPairing(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form"); //DIV1 IN CSS, DON'T KNOW IF WRAPPING WORKS
    data.recipe = $("input[name='recipe']").val();
    data.amount = parseInt($("input[name='amount']").val());
    data.ingredient = $("input[name='ingredient']").val();
    sendData(form.attr("action"), form.attr("method"), data, renderMsg("Successful Pairing Submission"));
}

function submitIngredient(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form"); //DIV1 IN CSS, DON'T KNOW IF WRAPPING WORKS
    data.name = $("input[name='name']").val();
    data.unit = $("input[name='unit']").val();
    data.calories = parseInt($("input[name='calories']").val());
    data.description = $("input[name='description']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedIngredient);
}

function submitDrink(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form"); //DIV1 IN CSS, DON'T KNOW IF WRAPPING WORKS
    data.name = $("input[name='name']").val();
    data.alcohol = document.getElementById("alcohol").checked;
    data.description = $("input[name='description']").val();
    data.recipe = $("input[name='recipe']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedDrink);
}

function getSubmittedRecipe(data, status, jqxhr) {
    renderMsg("Successful Recipe Submission");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendRecipeRow);
    }
}


function getSubmittedIngredient(data, status, jqxhr) {
    renderMsg("Successful Ingredient Submission");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendIngredientRow);
    }
}

function getSubmittedDrink(data, status, jqxhr) {
    renderMsg("Successful Drink Submission");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendDrinkRow);
    }
}

function renderRecipeForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.name;
    let description = ctrl.description;
    let text = ctrl.text;
    let drink = ctrl["@controls"]["bigrec:drink"];
    form.append("<h1>" + name + "</h1>");
    form.append("<label>" + description + "</label>" + "<br>");
    form.append(text);
    if (drink) {
        form.append("<br><br><a href='" +
            drink.href +
            "' onClick='followLink(event, this, renderDrink)'>Drink Recommendation</a>");
    }
    $("div.form").html(form);
}

function renderIngredientForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.name;
    let unit = ctrl.unit;
    let calories = ctrl.calories;
    let description = ctrl.description;
    form.append("<h1>" + name + "</h1>");
    form.append("<label>Unit: " + unit + "</label>" + "<br>");
    form.append("<label>Calories: " + calories + "</label>" + "<br>");
    form.append("Description: " + description);
    $("div.form").html(form);
}

function renderDrinkForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.name;
    let alcohol = ctrl.alcohol;
    let description = ctrl.description;
    form.append("<h1>" + name + "</h1>");
    form.append("Alcohol: " + alcohol + "<br>");
    form.append("Description: " + description);
    $("div.form").html(form);
}

function postRecipeForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let description = ctrl.schema.properties.description;
    let text = ctrl.schema.properties.text;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitRecipe);
    form.append("<h1>Post New Recipe</h1>");
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + description.description + "</label>");
    form.append("<input type='text' name='description'>");
    form.append("<label>" + text.description + "</label>");
    form.append("<textarea id='text' name='text' rows='4' cols='50'>" + ctrl.text + "</textarea>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function deleteRecipe(ctrl) {
    let form = $("<form>");
    form.attr("action", ctrl["@controls"]["bigrec:delete"].href);
    form.attr("method", ctrl["@controls"]["bigrec:delete"].method);
    form.submit(submitRecipe);
    form.append("<h1>Delete Recipe?</h1>");
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function postIngredientForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let description = ctrl.schema.properties.description;
    let unit = ctrl.schema.properties.unit;
    let calories = ctrl.schema.properties.calories;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitIngredient);
    form.append("<h1>Post New Recipe</h1>");
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + description.description + "</label>");
    form.append("<input type='text' name='description'>");
    form.append("<label>" + unit.description + "</label>");
    form.append("<input type='text' name='unit'>");
    form.append("<label>" + calories.description + "</label>");
    form.append("<input type='number' name='calories'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function postPairingForm(ctrl) {
    let form = $("<form>");
    let ingredient = ctrl.schema.properties.ingredient;
    let recipe = ctrl.schema.properties.recipe;
    let amount = ctrl.schema.properties.amount;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitPairing);
    form.append("<h1>Post New Pairing</h1>");
    form.append("<label>" + ingredient.description + "</label>");
    form.append("<input type='text' name='ingredient'>");
    form.append("<label>" + recipe.description + "</label>");
    form.append("<input type='text' name='recipe' disabled>");
    form.append("<label>" + amount.description + "</label>");
    form.append("<input type='number' name='amount'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function editRecipeForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let description = ctrl.schema.properties.description;
    let text = ctrl.schema.properties.text;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitRecipe);
    form.append("<h1>Edit Recipe</h1>");
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + description.description + "</label>");
    form.append("<input type='text' name='description'>");
    form.append("<label>" + text.description + "</label>");
    form.append("<textarea id='text' name='text' rows='4' cols='50'>" + ctrl.text + "</textarea>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function editIngredientForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let unit = ctrl.schema.properties.unit;
    let description = ctrl.schema.properties.description;
    let calories = ctrl.schema.properties.calories;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitIngredient);
    form.append("<h1>Edit Ingredient</h1>");
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + unit.description + "</label>");
    form.append("<input type='text' name='unit'>");
    form.append("<label>" + calories.description + "</label>");
    form.append("<input type='number' name='calories'>");
    form.append("<label>" + description.description + "</label>");
    form.append("<input type='text' name='description'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function editDrinkForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let alcohol = ctrl.schema.properties.alcohol;
    let description = ctrl.schema.properties.description;
    let recipe = ctrl.schema.properties.recipe;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitDrink);
    form.append("<h1>Edit Drink</h1>");
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + alcohol.description + "</label>");
    form.append("<input type='checkbox' id='alcohol' name='alcohol'>");
    form.append("<label>" + description.description + "</label>");
    form.append("<input type='text' name='description'>");
    form.append("<label>" + recipe.description + "</label>");
    form.append("<input type='text' name='recipe'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function postDrinkForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let alcohol = ctrl.schema.properties.alcohol;
    let description = ctrl.schema.properties.description;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitDrink);
    form.append("<h1>Post Drink</h1>");
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + alcohol.description + "</label>");
    form.append("<input type='checkbox' id='alcohol' name='alcohol'>");
    form.append("<label>" + description.description + "</label>");
    form.append("<input type='text' name='description'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function renderRecipe(body) {
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderRecipe)'>recipe</a> | " +
        "<a href='" +
        body["@controls"]["edit"].href +
        "' onClick='followLink(event, this, editRecipe)'>edit recipe body</a> | " +
        "<a href='" +
        body["@controls"]["bigrec:ingredients"].href +
        "' onClick='followLink(event, this, deletePairing)'>remove ingredient</a> | " +
        "<a href='" +
        body["@controls"]["bigrec:ingredients"].href +
        "' onClick='followLink(event, this, postPairing)'>add ingredient</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    renderRecipeForm(body);
    getResource(body["@controls"]["bigrec:ingredients"].href, renderRecIngPairings);
    $("input[name='name']").val(body.name);
    $("input[name='text']").val(body.text);
}

function renderIngredient(body) {
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderIngredients)'>back</a> | " +
        "<a href='" +
        body["@controls"]["edit"].href +
        "' onClick='followLink(event, this, editIngredient)'>edit this ingredient</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderIngredientForm(body);
    $("input[name='name']").val(body.name);
    $("input[name='unit']").val(body.unit);
    $("input[name='calories']").val(body.calories);
    $("input[name='description']").val(body.description);
}

function renderDrink(body) {
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderDrinks)'>back</a> | " +
        "<a href='" +
        body["@controls"]["edit"].href +
        "' onClick='followLink(event, this, editDrink)'>edit this drink</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderDrinkForm(body);
    document.getElementById('alcohol').checked = body.alcohol === true
    $("input[name='name']").val(body.name);
    $("input[name='alcohol']").val(document.getElementById('alcohol').checked);
    $("input[name='description']").val(body.description);
}

function postPairing(body) {
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    postPairingForm(body["@controls"]["bigrec:add-pairing"]);
    $("input[name='recipe']").val(body.recipe);
}

function postRecipe(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderRecipes)'>back</a> | " +
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderRecipe)'>show this recipe</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    postRecipeForm(body["@controls"]["bigrec:add-recipe"]);
    $("input[name='name']").val(body.name);
    $("input[name='description']").val(body.description);
    $("textarea[name='text']").val(body.text);
}

function postIngredient(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderIngredients)'>back</a> | " +
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderIngredient)'>show this ingredient</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    postIngredientForm(body["@controls"]["bigrec:add-ingredient"]);
    $("input[name='name']").val(body.name);
    $("input[name='description']").val(body.description);
    $("textarea[name='text']").val(body.text);
}

function editRecipe(body) {
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    editRecipeForm(body["@controls"].edit);
    $("input[name='name']").val(body.name);
    $("input[name='description']").val(body.description);
    $("textarea[name='text']").val(body.text);
}

function editIngredient(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderIngredients)'>back</a> | " +
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderIngredient)'>show this ingredient</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    editIngredientForm(body["@controls"].edit);
    $("input[name='name']").val(body.name);
    $("input[name='unit']").val(body.unit);
    $("input[name='calories']").val(body.calories);
    $("input[name='description']").val(body.description);
}

function editDrink(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderDrinks)'>back</a> | " +
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderDrink)'>show this drink</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    editDrinkForm(body["@controls"].edit);
    document.getElementById('alcohol').checked = (body.alcohol === true)
    $("input[name='name']").val(body.name);
    $("input[name='alcohol']").val(body.alcohol);
    $("input[name='description']").val(body.description);
}

function postDrink(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, renderDrinks)'>back</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    postDrinkForm(body["@controls"]["bigrec:add-drink"]);
    document.getElementById('alcohol').checked = (body.alcohol === true)
    $("input[name='name']").val(body.name);
    $("input[name='alcohol']").val(body.alcohol);
    $("input[name='description']").val(body.description);
}

function searchRecipe(event) {
    event.preventDefault();

    let form = $("div.form form"); //DIV1 IN CSS, DON'T KNOW IF WRAPPING WORKS
    //renderMsg($("input[name='ingredient']").val());
    getResource(form.attr("url") + $("input[name='recipe']").val(), renderRecipe);
}
function searchIngredient(event) {
    event.preventDefault();

    let form = $("div.form form"); //DIV1 IN CSS, DON'T KNOW IF WRAPPING WORKS
    //renderMsg($("input[name='ingredient']").val());
    getResource(form.attr("url") + $("input[name='ingredient']").val(), renderIngredient);
}

function searchDrink(event) {
    event.preventDefault();

    let form = $("div.form form"); //DIV1 IN CSS, DON'T KNOW IF WRAPPING WORKS
    //renderMsg($("input[name='ingredient']").val());
    getResource(form.attr("url") + $("input[name='drink']").val(), renderDrink);
}

function renderRecSearchForm(ctrl) {
    let form = $("<form>");
    form.attr("url", ctrl.href);
    form.submit(searchRecipe);
    form.append("<h1>Search</h1>");
    form.append("<label>Search by name</label>");
    form.append("<input type='text' name='recipe'>");
    form.append("<input type='submit' name='submit' value='Search'>");
    $("div.form").html(form);
}

function renderIngSearchForm(ctrl) {
    let form = $("<form>");
    form.attr("url", ctrl.href);
    form.submit(searchIngredient);
    form.append("<h1>Search</h1>");
    form.append("<label>Search by name</label>");
    form.append("<input type='text' name='ingredient'>");
    form.append("<input type='submit' name='submit' value='Search'>");
    $("div.form").html(form);
}

function renderDrSearchForm(ctrl) {
    let form = $("<form>");
    form.attr("url", ctrl.href);
    form.submit(searchDrink);
    form.append("<h1>Search</h1>");
    form.append("<label>Search by name</label>");
    form.append("<input type='text' name='drink'>");
    form.append("<input type='submit' name='submit' value='Search'>");
    $("div.form").html(form);
}

function renderRecipes(body) {
    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    let prev = body["@controls"].prev;
    let next = body["@controls"].next;
    if (prev) {
        tablectrl.append(
            "<a href='" + prev.href +
            "' onClick='followLink(event, this, renderRecipes)'>prev</a>"
        );
    }
    if (prev && next) {
        tablectrl.append(" | ");
    }
    if (next) {
        tablectrl.append(
            "<a href='" + next.href +
            "' onClick='followLink(event, this, renderRecipes)'>next</a>"
        );
    }
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, postRecipe)'>Post New Recipe</a>"
    );
    $(".resulttable thead").html(
        "<h1>Recipes</h1><tr><th>Name</th><th>Description</th><th>Link</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(recipeRow(item));
    });
    renderRecSearchForm(body["@controls"]["self"]);
}

function renderIngredients(body) {
    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, postIngredient)'>Post New Ingredient</a>"
    );
    $(".resulttable thead").html(
        "<h1>Ingredients</h1><tr><th>Name</th><th>Unit</th><th>Calories</th><th>Link</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(ingredientRow(item));
    });
    renderIngSearchForm(body["@controls"]["self"]);
}

function renderDrinks(body) {
    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].self.href +
        "' onClick='followLink(event, this, postDrink)'>Post New Drink</a>"
    );
    $(".resulttable thead").html(
        "<h1>Drinks</h1><tr><th>Name</th><th>Alcohol</th><th>Link</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(drinkRow(item));
    });
    renderDrSearchForm(body["@controls"]["self"]);
}

function renderRecIngPairings(body) {
    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    $(".resulttable thead").html(
        "<h1>Ingredients</h1><tr><th>Name</th><th>Amount</th><th>Units</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    for(var i in body["ingredients"]) {
        tbody.append(pairingRow(i, body["ingredients"][i][0], body["ingredients"][i][1]));
    }
}

$(document).ready(function () {
    $("div.choice").html(
        "<a href='" +
        "/api/recipes/" +
        "' onClick='followLink(event, this, renderRecipes)'>Recipes</a> | " +
        "<a href='" +
        "/api/ingredients/" +
        "' onClick='followLink(event, this, renderIngredients)'>Ingredients</a>| " +
        "<a href='" +
        "/api/drinks/" +
        "' onClick='followLink(event, this, renderDrinks)'>Drinks</a>"
    );
    getResource("http://localhost:5000/api/recipes/", renderRecipes);
});