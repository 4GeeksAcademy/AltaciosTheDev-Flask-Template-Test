"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Drink, Order
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

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
