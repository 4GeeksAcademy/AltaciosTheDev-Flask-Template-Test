from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() #creates instance of the SQLalchemy class, use to interact with the database throught the app.

class User(db.Model): #inherits drom a db.Model. 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
 
    def __repr__(self): # returns object representation as a string. 
        return '<User %r>' % self.username

    def serialize(self): #returns dictionary containing info of the user. 
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Drink(db.Model):
    __tablename__ = "drink"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)  
    price = db.Column(db.Float, unique=False, nullable=False) 

    def __init__(self, name,price):
        self.name = name
        self.price = price 

    def __repr__(self): # returns object representation as a string. 
        return f'<Drink {self.name}>'

    def serialize(self): #returns dictionary containing info of the user. 
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
            # do not serialize the password, its a security breach
        }