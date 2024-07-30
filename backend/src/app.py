from flask import Flask, request, jsonify
from flask_cors import CORS
from board import *

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    return jsonify(data)

@app.route('/api/move', methods=['POST'])
def move():
    return
if __name__ == '__main__':
    app.run(host="localhost", port=3000, debug=True)