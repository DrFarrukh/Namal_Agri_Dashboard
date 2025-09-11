from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

JSON_FILE = "sensor_data.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
