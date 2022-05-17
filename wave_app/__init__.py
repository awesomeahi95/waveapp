### imports for flask application ###
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

### intializing app and database ###
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

 
from wave_app import views
from wave_app import models