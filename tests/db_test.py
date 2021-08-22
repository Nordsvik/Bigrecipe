import os
import pytest
import tempfile
import time
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError, SQLAlchemyError

from bigrecipe import create_app, db
from bigrecipe.models import Recipe, Ingredient, Drink, Recingpairings

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        
    yield app
    
    os.close(db_fd)
    os.unlink(db_fname)

def _get_recipe():
    return Recipe(
        name="Nice Stew",
        description="A stew for folks",
        text="Make a big stew then eat it."
    )

def _get_ingredient():
    return Ingredient(
        name="Burger Meat",
        unit="g",
        calories=2,
        description="Flame it up"
        )

def _get_drink():
    return Drink(
        name="Bad Beer",
        alcohol=True,
        description="You don't have to drink it but it helps."
        )

def _get_recingpairing():
    recingpairing = Recingpairings(amount=4, recipe=Recipe(
        name="fa",
        description="da",
        text="noid"),
        ingredient=Ingredient(
        name="d Meat",
        unit="sss",
        calories=5,
        description="aaa"
        )
    )
    return recingpairing


def test_create_instances(app):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """
    
    with app.app_context():
        # Create everything
        recipe = _get_recipe()
        ingredient = _get_ingredient()
        drink = _get_drink()
        recingpairing = _get_recingpairing()
        recipe.drink = drink
        db.session.add(recipe)
        db.session.add(ingredient)
        db.session.add(drink) #added in recipe
        db.session.add(recingpairing)
        db.session.add(Recingpairings(amount=2, recipe=recipe, ingredient=ingredient))
        db.session.commit()
        
        # Check that everything exists
        assert Recipe.query.count() == 2
        assert Ingredient.query.count() == 2
        assert Recingpairings.query.count() == 2
        assert Drink.query.count() == 1
        db_recipe = Recipe.query.first()
        db_ingredient = Ingredient.query.first()
        db_recingpairing = Recingpairings.query.filter_by(recipe=db_recipe).first()
        db_drink = Drink.query.first()
        
        # Check all relationships (both sides)
        assert db_recipe.drink == db_drink
        assert db_recipe in db_drink.recipes
        assert db_recipe.id == db_recingpairing.recipe.id
        #assert db_sensor.location == db_location
        #assert db_sensor in db_deployment.sensors
        #assert db_deployment in db_sensor.deployments
        #assert db_measurement in db_sensor.measurements    
    
      

def test_recipe_ondelete_drink(app):
    """
    Tests that recipe's drink foreign key is set to null when the drink
    is deleted.
    """
    
    with app.app_context():
        recipe = _get_recipe()
        drink = _get_drink()
        recipe.drink = drink
        db.session.add(recipe)
        db.session.commit()
        db.session.delete(drink)
        db.session.commit()
        assert recipe.drink is None

def test_recipe_columns(app):
    """
    Tests the types and restrictions of recipe columns. Checks that name must
    be present and is unique, text must exist and that all of the columns are optional.
    """
    
    with app.app_context():
        
        recipe = _get_recipe()
        recipe.name = None
        db.session.add(recipe)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        recipe = _get_recipe()
        recipe.text = None
        db.session.add(recipe)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        recipe_1 = _get_recipe()
        recipe_2 = _get_recipe()
        db.session.add(recipe_1)
        db.session.add(recipe_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        recipe = Recipe(name="recipetest", text="sampletext")
        db.session.add(recipe)
        db.session.commit()

def test_ingredient_columns(app):
    """
    Tests the types and restrictions of ingredient columns. Checks that name must
    be present and is unique, calories takes only integers (DOES NOT RAISE ERROR and that all of the columns are optional.
    """
    
    with app.app_context():
        
        ingredient = _get_ingredient()
        ingredient.name = None
        db.session.add(ingredient)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        ingredient = _get_ingredient()
        ingredient.unit = None
        db.session.add(ingredient)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        ingredient_1 = _get_ingredient()
        ingredient_2 = _get_ingredient()
        db.session.add(ingredient_1)
        db.session.add(ingredient_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        ingredient = Ingredient(name="ingredienttest", unit="sampleunit")
        db.session.add(ingredient)
        db.session.commit()

def test_drink_columns(app):
    """
    Tests the types and restrictions of drink columns. Checks that name must
    be present and is unique, calories takes only integers (DOES NOT RAISE ERROR and that all of the columns are optional.
    """
    
    with app.app_context():
        
        drink = _get_drink()
        drink.name = None
        db.session.add(drink)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        drink = _get_drink()
        drink.alcohol = "not bool"
        db.session.add(drink)
        with pytest.raises(StatementError):
            db.session.commit()
        
        db.session.rollback()

        drink_1 = _get_drink()
        drink_2 = _get_drink()
        db.session.add(drink_1)
        db.session.add(drink_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        drink = Drink(name="drinktest", alcohol=True)
        db.session.add(drink)
        db.session.commit()

"""
def test_location_sensor_one_to_one(app):

    #Tests that the relationship between sensor and location is one-to-one.
    #i.e. that we cannot assign the same location for two sensors.

    
    with app.app_context():
        location = _get_location()
        sensor_1 = _get_sensor(1)
        sensor_2 = _get_sensor(2)
        sensor_1.location = location
        sensor_2.location = location
        db.session.add(location)
        db.session.add(sensor_1)
        db.session.add(sensor_2)    
        with pytest.raises(IntegrityError):
            db.session.commit()

def test_location_columns(app):

    #Tests the types and restrictions of location columns. Checks that numerical
    #values only accepts numbers, name must be present and is unique, and that
    #all of the columns are optional. 

    
    with app.app_context():
        location = _get_location()
        location.latitude = str(location.latitude) + "°"
        db.session.add(location)
        with pytest.raises(StatementError):
            db.session.commit()
            
        db.session.rollback()
            
        location = _get_location()
        location.longitude = str(location.longitude) + "°"
        db.session.add(location)
        with pytest.raises(StatementError):
            db.session.commit()
        
        db.session.rollback()

        location = _get_location()
        location.altitude = str(location.altitude) + "m"
        db.session.add(location)
        with pytest.raises(StatementError):
            db.session.commit()
        
        db.session.rollback()
        
        location = _get_location()
        location.name = None
        db.session.add(location)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        location_1 = _get_location()
        location_2 = _get_location()
        db.session.add(location_1)
        db.session.add(location_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        location = Location(name="site-test")
        db.session.add(location)
        db.session.commit()
    
def test_sensor_columns(app):

    #Tests sensor columns' restrictions. Name must be unique, and name and model
    #must be mandatory.

    with app.app_context():
        sensor_1 = _get_sensor()
        sensor_2 = _get_sensor()
        db.session.add(sensor_1)
        db.session.add(sensor_2)    
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
        
        sensor = _get_sensor()
        sensor.name = None
        db.session.add(sensor)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()
        
        sensor = _get_sensor()
        sensor.model = None
        db.session.add(sensor)
        with pytest.raises(IntegrityError):
            db.session.commit()    
    
def test_measurement_columns(app):

    #Tests that a measurement value only accepts floating point values and that
    #time only accepts datetime values.

    
    with app.app_context():
        measurement = _get_measurement()
        measurement.value = str(measurement.value) + "kg"
        db.session.add(measurement)
        with pytest.raises(StatementError):
            db.session.commit()
            
        db.session.rollback()
        
        measurement = _get_measurement()
        measurement.time = time.time()
        db.session.add(measurement)
        with pytest.raises(StatementError):
            db.session.commit()
    
def test_deployment_columns(app):

    #Tests that all columns in the deployment table are mandatory. Also tests
    #that start and end only accept datetime values.

    
    with app.app_context():
        # Tests for nullable
        deployment = _get_deployment()
        deployment.start = None
        db.session.add(deployment)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        deployment = _get_deployment()
        deployment.end = None
        db.session.add(deployment)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        deployment = _get_deployment()
        deployment.name = None
        db.session.add(deployment)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()
            
        # Tests for column type
        deployment = _get_deployment()
        deployment.start = time.time()
        db.session.add(deployment)
        with pytest.raises(StatementError):
            db.session.commit()
        
        db.session.rollback()
        
        deployment = _get_deployment()
        deployment.end = time.time()
        db.session.add(deployment)
        with pytest.raises(StatementError):
            db.session.commit()
    
        db.session.rollback()
"""