from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Factory function to create a new MongoDB client
def create_db_client(uri='mongodb://localhost:27017'):
    return MongoClient(uri)

# Factory function to get database
def get_db(client=None):
    if client is None:
        client = create_db_client()
    return client['restdb']

# Factory function to get collection
def get_collection(db=None):
    if db is None:
        db = get_db()
    return db['stars']

@app.route('/stars', methods=['POST'])
def create_star():
    db = get_db()
    collection = get_collection(db)
    data = request.json
    result = collection.insert_one(data)
    return jsonify({'_id': str(result.inserted_id)}), 201

@app.route('/stars', methods=['GET'])
def get_stars():
    db = get_db()
    collection = get_collection(db)
    items = list(collection.find())
    for item in items:
        item['_id'] = str(item['_id'])
    return jsonify(items)

@app.route('/star/<id>', methods=['GET'])
def get_star(id):
    try:
        db = get_db()
        collection = get_collection(db)
        item = collection.find_one({ '_id': ObjectId(id)})
        if item:
            item['_id'] = str(item['_id'])
            return jsonify(item)
        return jsonify({'error': 'Invalid ID format'}), 400
    except Exception as e:
        return jsonify({'error': 'Error while fetching star', 'message': e}), 400

@app.route('/star/<id>', methods=['PUT'])
def update_star(id):
    try:
        db = get_db()
        collection = get_collection(db)
        data = request.json
        
        result = collection.update_one({ '_id': ObjectId(id)}, { '$set': data })
        if result.matched_count:
            return jsonify({'message': 'Item updated successfully'})
        return jsonify({'error': 'Item not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Error while updating star', 'message': str(e)}), 400
    
@app.route('/star/<id>', methods=['DELETE'])
def delete_star(id):
    try:
        db = get_db()
        collection = get_collection(db)
        result = collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count:
            return jsonify({'message': 'Item deleted successfully'}), 200
        return jsonify({'error': 'Star not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Error while deleting star', 'message': e})
    
if __name__ == '__main__':
    app.run(debug=True)