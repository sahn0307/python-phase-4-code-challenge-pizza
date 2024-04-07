#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
class Restaurants(Resource):
    def get(self):
        try:
            restaurants = [restaurant.to_dict() for restaurant in Restaurant.query]
            return restaurants, 200
        except Exception as e:
            return {"message": str(e)}, 404
        
api.add_resource(Restaurants, "/restaurants")

class RestaurantsById(Resource):
    def get(self, id):
        try:
            if restaurant := db.session.get(Restaurant, id):
                return restaurant.to_dict(only=("id", "name", "address", "restaurant_pizzas")), 200
            else:
                return {"error": "Restaurant not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 400

    def delete(self, id):
        try:
            if restaurant := db.session.get(Restaurant, id):
                db.session.delete(restaurant)
                db.session.commit()
                return {"message": ""}, 204
            else:
                return {"error": "Restaurant not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 400
api.add_resource(RestaurantsById, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        try:
            pizzas = [pizza.to_dict(only=("id", "ingredients", "name")) for pizza in Pizza.query]
            return pizzas, 200
        except Exception as e:
            return {"message": str(e)}, 400
        
api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.json
            new_pizza = RestaurantPizza(**data)
            db.session.add(new_pizza)
            db.session.commit()
    
            return new_pizza.to_dict(rules=()), 201
        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
