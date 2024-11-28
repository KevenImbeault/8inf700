import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis
import json
from sqlalchemy.exc import SQLAlchemyError
from prometheus_flask_exporter import PrometheusMetrics

# Load environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

# Initialize Flask app
app = Flask(__name__)
PrometheusMetrics(app)

# Configure PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

# Define a SQLAlchemy model for data
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}

# Ensure the table is created
with app.app_context():
    db.create_all()

# POST endpoint to create a new item
@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    name = data.get("name")
    description = data.get("description", "")
    
    # Create a new item and add it to the PostgreSQL database
    new_item = Item(name=name, description=description)
    
    try:
        db.session.add(new_item)
        db.session.commit()
        # Cache the new item in Redis
        redis_client.set(f'item:{new_item.id}', json.dumps(new_item.to_dict()))
        return jsonify(new_item.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET endpoint to retrieve an item by ID
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    # Check if the item is in the Redis cache
    cached_item = redis_client.get(f'item:{item_id}')
    if cached_item:
        item_data = json.loads(cached_item)
        item_data['source'] = 'cache'
        return jsonify(item_data)
    
    # If not in cache, query the PostgreSQL database
    item = Item.query.get(item_id)
    if item:
        item_data = item.to_dict()
        item_data['source'] = 'database'
        # Cache the item in Redis for future requests
        redis_client.set(f'item:{item_id}', json.dumps(item_data))
        return jsonify(item_data)
    else:
        return jsonify({"error": "Item not found"}), 404

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
