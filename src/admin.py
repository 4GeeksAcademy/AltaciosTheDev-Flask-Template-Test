import os #imports the operating system, which is used to interact with the operating system environment 
from flask_admin import Admin #extension that lets add admin interfaces to flask apps.  
from models import db, User, Drink, Order # Imports the SQLAlchemy database instance (db) and database models. These models represent tables in the database.
from flask_admin.contrib.sqla import ModelView #modelview is a class provided by flask_admin specifically for SQLALchemty based models. Provides generic views that can be used to display and interact with SQLAlchemy model data in the FlaskAdmin interface.

#defining the setup_admin function
def setup_admin(app): #func that takes a Flask application instance (app) as an argument. It configures and sets up the Flask-Admin interface within the Flask application.
#setting up the flask-admin 
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')#: Sets the Flask application's secret key. The secret key is used to securely sign session cookies and other security-related features in Flask.
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'#Sets the Flask-Admin interface theme to 'cerulean'. This controls the appearance of the admin interface.
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')#Initializes the Flask-Admin extension with the Flask application instance (app).

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Drink, db.session))
    admin.add_view(ModelView(Order, db.session))