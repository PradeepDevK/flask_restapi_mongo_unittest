import unittest
import mongomock
from app import app, get_db, get_collection
class FlaskAppTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Import the app module to make sure it's in the test context
        import app
        cls.app = app.app  # Ensure the Flask app instance is assigned
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

        # Set up mongomock client
        cls.mongo_client = mongomock.MongoClient()
        cls.db = cls.mongo_client['testdb']
        cls.collection = cls.db['stars']

        # Override the get_collection function to use the mongomock collection
        def get_test_collection(db=None):
            return cls.collection

        # Import the app module and override the function
        import app
        app.get_collection = get_test_collection

    def setUp(self):
        # Clear the collection before each test
        self.collection.delete_many({})

    def test_create_star(self):
        response = self.client.post('/stars', json={'name': 'Sirius', 'distance': 10.96})
        self.assertEqual(response.status_code, 201)
        self.assertIn('_id', response.json)

    def test_get_stars(self):
        self.collection.insert_one({'name': 'Sirius', 'distance': 10.96})
        response = self.client.get('/stars')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)

    def test_get_star(self):
        result = self.collection.insert_one({'name': 'Sirius', 'distance': 10.96})
        star_id = result.inserted_id
        response = self.client.get(f'/star/{star_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Sirius')

    def test_update_star(self):
        result = self.collection.insert_one({'name': 'Sirius', 'distance': 1})
        star_id = result.inserted_id
        print(f"Inserted star ID: {star_id}")

        response = self.client.put(f'/star/{star_id}', json={})
        print(f"Response status code: {response.status_code}")
        print(f"Response JSON: {response.json}")

        self.assertEqual(response.status_code, 200)

        updated_star = self.collection.find_one({'_id': result.inserted_id})
        print(f"Updated star: {updated_star}")

        self.assertEqual(updated_star['distance'], 20.0)

    def test_delete_star(self):
        result = self.collection.insert_one({'name': 'Sirius', 'distance': 10.96})
        star_id = str(result.inserted_id)
        response = self.client.delete(f'/star/{star_id}')
        self.assertEqual(response.status_code, 200)
        deleted_star = self.collection.find_one({'_id': result.inserted_id})
        self.assertIsNone(deleted_star)

if __name__ == '__main__':
    unittest.main()
