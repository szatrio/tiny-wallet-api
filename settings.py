from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'db_tiny_wallet',
    'host': 'localhost',
    'port': 27017
}

CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
secret = "Satrio utomo"

db = MongoEngine(app)