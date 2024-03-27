"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os #provides way to interact with operating system 
from flask import Flask, request, jsonify #imports necessary info to build the web application in python 
from flask_migrate import Migrate         #flask extension that handles database migrations for Flask applications using Alembic. Database operations are provided as command line under flash db command.
from flask_swagger import swagger         #provides method that inspects the Flask app for endpoints that contain YAML docstrings. Used for creating API doc unsing swagger.
from flask_cors import CORS               #extension for handling CORS. Allows us to control which origins are allowed to request, which HTTP methods are allowed, and what headers can be sent along with the requests.
from utils import APIException, generate_sitemap  #generates an index of all the endpoints of the application. 
from admin import setup_admin             
from models import db, User, Drink, Order #db connection to sqlalchemy, could be changed for any other name.

#Create Flask App
app = Flask(__name__)                   #creates a flask application instance
app.url_map.strict_slashes = False      #configures app to ignore trailing slashes in route URLs.

#Configure database 
db_url = os.getenv("DATABASE_URL")      #retrieves env variable DATABASE_URL that contains the specifics of the postgresql database, user, pass, and db to connecto to.
if db_url is not None:                  #code runs only if DATABASE_URL != None
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://") #configures the databasse URI to use postgresql
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db" #if db_url == None, condigures the database to use sqlite with a test.db file database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#psql -h localhost -U gitpod example
#psql: This is the command to start the PostgreSQL interactive terminal program.
#-h localhost: This option specifies the hostname of the PostgreSQL server to connect to. 
#-U gitpod: This option specifies the username to use when connecting to the PostgreSQL server. 
#example: This is the name of the database to connect to. By default in Postgres it would be the database of with the same name as the user.

#Database migration 
#when working with RDBMS its common to make changes to the structure of your database schema over time. Migration tools help manage these changes.
MIGRATE = Migrate(app, db) #create instance of Migrate class asigns it to MIGRATE. This initializes the Flask-Migrate extension with the Flask application and SQLAlchemy, enabling database migrations for the application. Basically allows successful migration from app to the db.

#Initialize database
db.init_app(app)     #This method initializes the SQLAlchemy extension with the Flask application. It tells SQLAlchemy which Flask application it should be working with.
CORS(app)            #Enables CORS support for the Flask app, allowing it to handle requests from different origins.
setup_admin(app)     #Configures the Flask-Admin interface for the Flask app

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code #Defines an error handler for instances of APIException, returning JSON-formatted error responses.

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app) #Defines a route / that returns a sitemap of all endpoints in the application.

@app.route('/user', methods=['GET'])
def handle_hello():

    users = User.query.all() #SELECT * from users AND returns python objects, we can only jsonify dictionaries 

    return jsonify([user.serialize() for user in users]), 200 #[functionCalled for element in iterable]

@app.route('/drink', methods=['POST', "GET"])
def add_drink():
    
    if request.method == "GET":
        drinks = Drink.query.all()
        return jsonify([drink.serialize() for drink in drinks]),200

    body = request.json
    #receive from body of request
    name = body.get("name")
    price = body.get("price")

    if name != None and price != None: #if properties not None, create new instance of Class Drink(which is a row in the table)
        new_drink = Drink(name=name, price=price) #constructor 
        db.session.add(new_drink) #RAM
        db.session.commit() #ID, al guardar en base de datos, se asigna ID automatico 
        return jsonify(new_drink.serialize()), 200
    return jsonify({"msg": "Error missing keys"}), 400

@app.route('/drink/<int:id>', methods=['DELETE', "PUT"])
def handle_drink(id):
    search = Drink.query.filter_by(id=id).one_or_none() #si encuentra lo devuelve y si no devuelve None

    if request.method == "PUT":
        if search != None:
            body = request.json
            new_name = body.get("name",None)
            new_price = body.get("price", None)
            if new_name != None:
                search.name = new_name
            if new_price != None:
                search.price = new_price
            db.session.commit()
            return jsonify(search.serialize()), 200
        
        return jsonify({"msg": "drink not found"}), 404
    else:
        if search != None:            
            db.session.delete(search)
            db.session.commit()
            return jsonify({"msg": "ey lo lograste, borraste exitoso"}),200

        else:
            return jsonify({"msg": "drink not found"}),404

    return jsonify({"msg": "something happended"}),500

@app.route("/orders", methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.serialize() for order in orders]), 200

@app.route("/orders", methods=['POST'])
def add_order():
    body = request.json
    order_name = body.get("name")
    new_order = Order(order_name) #objeto solo con nombre que viene del body
    drinks_ids = body.get("drinks") #ids que vienen

    for drink_id in drinks_ids:
        # se busca cada id en tabla de Drinks para ver si se encuentra
        search_drink = Drink.query.filter_by(id = drink_id).one_or_none()
        #si se encuentra, se append TODA info de drink a new_order.drinks
        if search_drink != None:
            new_order.drinks.append(search_drink)
            #aqui ya tiene info completa de cada drink 

        # si no se encuentra drink en tabla de Drinks, se regresa ERROR.
        else:
            return jsonify({"msg": "drink not found"}),404
        
    db.session.add(new_order) #por la clase de la variable se sabe a que tabla ingresar
    db.session.commit()
        
    return jsonify(new_order.serialize()), 201 

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
