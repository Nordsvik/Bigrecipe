# PWP Summer 2021
# Bigrecipe
# Group information
* Viktor Nordström viktor.nordstrom@gmail.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

# Dependencies
flask, flask-restful, flask-sqlalchemy, SQLAlchemy
Full environment package list in requirements.txt
#How to setup/install the client
Install with pip using setup.py like the sample project
#How to configure and run the client
models.py includes flask commands, here's what you need to get going:
First setup environment with
"export FLASK_APP=bigrecipe", "set FLASK_APP=bigrecipe" on Windows
"export FLASK_ENV=development", "set FLASK_ENV=development" on Windows,
development environment just to be sure

"flask init-db" to initialize database
"flask testgen", then "flask assocgen" to set up some initial data
finally "flask run" to run server.
Basically the same as in the sample project.
Access the client through http://127.0.0.1:5000/admin/
