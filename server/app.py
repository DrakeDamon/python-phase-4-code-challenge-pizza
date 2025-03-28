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


# Home resource
class Home(Resource):
    def get(self):
        return {"message": "Pizza Restaurant API"}

# Restaurant resources
class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict(only=('id', 'name', 'address')) 
                       for restaurant in Restaurant.query.all()]
        
        response = make_response(
            restaurants,
            200
        )
        
        return response

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        
        if not restaurant:
            response = make_response(
                {"error": "Restaurant not found"},
                404
            )
            return response
        
        response_dict = restaurant.to_dict()
        
        response = make_response(
            response_dict,
            200
        )
        
        return response
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        
        if not restaurant:
            response = make_response(
                {"error": "Restaurant not found"},
                404
            )
            return response
        
        db.session.delete(restaurant)
        db.session.commit()
        
        response = make_response(
            "",
            204
        )
        
        return response

# Pizza resources
class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict(only=('id', 'name', 'ingredients')) 
                  for pizza in Pizza.query.all()]
        
        response = make_response(
            pizzas,
            200
        )
        
        return response

# RestaurantPizza resources
class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            
            restaurant = Restaurant.query.get(data.get('restaurant_id'))
            pizza = Pizza.query.get(data.get('pizza_id'))
            
            if not restaurant:
                response = make_response(
                    {"errors": ["Restaurant not found"]},
                    404
                )
                return response
            
            if not pizza:
                response = make_response(
                    {"errors": ["Pizza not found"]},
                    404
                )
                return response
            
            new_restaurant_pizza = RestaurantPizza(
                price=data.get('price'),
                restaurant_id=data.get('restaurant_id'),
                pizza_id=data.get('pizza_id')
            )
            
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            
            response_dict = new_restaurant_pizza.to_dict()
            
            response = make_response(
                response_dict,
                201
            )
            
            return response
            
        except ValueError as e:
            response = make_response(
                {"errors": [str(e)]},
                400  # Using 400 for validation errors as per tests
            )
            return response
        except Exception as e:
            response = make_response(
                {"errors": [str(e)]},
                400
            )
            return response


# Register resources with API endpoints
api.add_resource(Home, '/')
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)