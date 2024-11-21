import os
from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# Base URL of the API
API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000')  # Adjust if your API server runs on a different address or port

# HTML Templates
index_template = """
<!doctype html>
<html lang="en">
<head>
    <title>Item Client</title>
</head>
<body>
    <h1>Item Client</h1>
    <h2>Create a New Item</h2>
    <form action="/create" method="post">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required>
        <label for="description">Description:</label>
        <input type="text" id="description" name="description">
        <button type="submit">Create Item</button>
    </form>
    
    <h2>Get an Item by ID</h2>
    <form action="/get" method="post">
        <label for="item_id">Item ID:</label>
        <input type="number" id="item_id" name="item_id" required>
        <button type="submit">Get Item</button>
    </form>
    
    <h3>{{ message }}</h3>
</body>
</html>
"""

# Route for index page
@app.route('/')
def index():
    return render_template_string(index_template, message="")

# Route to create a new item
@app.route('/create', methods=['POST'])
def create_item():
    name = request.form.get('name')
    description = request.form.get('description')

    # Make a POST request to the API to create an item
    response = requests.post(f"{API_URL}/items", json={'name': name, 'description': description})
    
    if response.status_code == 201:
        item = response.json()
        message = f"Item created successfully: ID {item['id']}, Name: {item['name']}, Description: {item['description']}"
    else:
        message = f"Failed to create item: {response.json().get('error', 'Unknown error')}"
    
    return render_template_string(index_template, message=message)

# Route to get an item by ID
@app.route('/get', methods=['POST'])
def get_item():
    item_id = request.form.get('item_id')

    # Make a GET request to the API to retrieve the item
    response = requests.get(f"{API_URL}/items/{item_id}")
    
    if response.status_code == 200:
        item = response.json()
        message = f"Item retrieved: ID {item['id']}, Name: {item['name']}, Description: {item['description']}, Source: {item['source']}"
    else:
        message = f"Item not found or error occurred: {response.json().get('error', 'Unknown error')}"
    
    return render_template_string(index_template, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
