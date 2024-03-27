from flask_sqlalchemy import SQLAlchemy #module within Flask that provides integration with SQLAlchemy and simplifies database integrations. 
#SQLAlchemy is the amin class provided by flask_sqlalchemy. 

db = SQLAlchemy() #creates instance of the SQLalchemy class, use to interact with the database throught the app.

class User(db.Model): #from db.Model inherits all the functionality and features provided by SQLAlchemy's Model class, allowing it to represent a table in the database.
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
    
association_table_orders = db.Table(
    "association_table_order",
    db.metadata,
    db.Column("order", db.ForeignKey("order.id")),
    db.Column("drink", db.ForeignKey("drink.id"))
)
    
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=True)

    drinks = db.relationship(Drink, secondary=association_table_orders) #para cada bebida va tener una orden automatico con backref 

    def __init__(self,name):
        self.name = name

    def get_total(self):
        total = 0
        for drink in self.drinks:
            total = total + drink.price
        return total

    def serialize(self):
        return{
            "id": self.id,
            "drinks": [drink.serialize() for drink in self.drinks],
            "total": self.get_total() 
        }

    