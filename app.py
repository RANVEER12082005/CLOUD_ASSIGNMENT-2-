from flask import Flask, request, jsonify, send_file
from cloudant.client import Cloudant
from cloudant.error import CloudantException

app = Flask(__name__)

apikey = "7m1wlU7OkIzgfp1zC2VcFT4V-9USVX-ZuPqOGV33agh2"
url = "https://cddb771f-2b82-49f5-b073-b0ab178d326f-bluemix.cloudantnosqldb.appdomain.cloud"
username = "cddb771f-2b82-49f5-b073-b0ab178d326f-bluemix"
db_name = "review_db"

# Connect to Cloudant
client = Cloudant.iam(username, apikey, url=url, connect=True)

# Create or connect to database
try:
    db = client[db_name]
    print(f"Connected to existing database: {db_name}")
except KeyError:
    # Database doesn't exist, create it
    db = client.create_database(db_name)
    print(f"Created new database: {db_name}")
except Exception as e:
    print(f"Error connecting to Cloudant: {e}")
    raise

# Serve static HTML directly from current folder
@app.route('/')
def index():
    return send_file("index.html")

@app.route('/create', methods=['POST'])
def create_record():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        feedback = data.get('feedback')

        if not name or not email or not feedback:
            return jsonify({"error": "Missing name, email, or feedback"}), 400

        document = {
            "name": name,
            "email": email,
            "feedback": feedback
        }
        
        # Create document in Cloudant
        result = db.create_document(document)
        print(f"Document created: {result}")
        
        return jsonify({"message": "Record created successfully!"}), 201
    except Exception as e:
        print("Error creating record:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/get_records', methods=['GET'])
def get_records():
    try:
        records = []
        for doc in db:
            # Skip design documents
            if not doc.get('_id', '').startswith('_design'):
                records.append({
                    "name": doc.get("name"),
                    "email": doc.get("email"),
                    "feedback": doc.get("feedback")
                })
        return jsonify(records), 200
    except Exception as e:
        print("Error fetching records:", e)
        return jsonify({"error": "Failed to fetch records"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_info = db.info()
        return jsonify({
            "status": "healthy",
            "database": db_name,
            "doc_count": db_info.get('doc_count', 0)
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print(f"Starting Flask app...")
    print(f"Database: {db_name}")
    print(f"Access the app at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
