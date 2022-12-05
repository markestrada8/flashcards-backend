from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from flask_marshmallow import Marshmallow
# Implement CORS
from flask_cors import CORS
import os


# Set up Flask app and DB path
app = Flask(__name__)
# Implement CORS
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Configure user table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), unique=False)

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('user_name', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Configure card table - cards per topic, topics per user
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    topic = db.Column(db.String(1000), unique=False)
    front = db.Column(db.String(1000), unique=False)
    back = db.Column(db.String(100), unique=False)
    card_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, topic, front, back, card_user_id):
        self.name = name
        self.topic = topic
        self.front = front
        self.back = back
        self.card_user_id = card_user_id


class CardSchema(ma.Schema):
    class Meta:
        fields = ('name', 'topic', 'front',
                  'back', 'card_user_id')


card_schema = CardSchema()
cards_schema = CardSchema(many=True)


# Add card
@app.route("/card/<user_id>", methods=["POST"])
def add_card(user_id):
    name = request.json['name']
    topic = request.json['topic']
    front = request.json['front']
    back = request.json['back']
    card_user_id = user_id

    new_card = Card(
        name, topic, front, back, card_user_id)

    db.session.add(new_card)
    db.session.commit()

    return card_schema.jsonify(new_card)


# Get all cards
@app.route("/cards", methods=["GET"])
def get_cards():
    all_cards = Card.query.all()
    result = cards_schema.dump(all_cards)
    return jsonify(result)


# Get user cards
@app.route("/cards/<user_id>", methods=["GET"])
def get_user_cards(user_id):
    id = int(user_id)
    user_cards = db.session.query(Card).filter(
        Card.card_user_id == id)
    result = cards_schema.dump(user_cards)
    return jsonify(result)


# Add user
@ app.route("/user", methods=["POST"])
def add_user():
    user_name = request.json['user_name']
    password = request.json['password']

    new_user = User(user_name, password)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)


@app.route("/users", methods=["GET"])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    for user in all_users:
        print(user.id)
    return jsonify(result)


if __name__ == '__main__':
    # Check if database file exists, if not, create it
    if not os.path.exists(os.path.join(basedir, 'app.sqlite')):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
