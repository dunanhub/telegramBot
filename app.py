# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import json

# app = Flask(__name__)
# CORS(app, resources={r"/appointments/*": {"origins": "*"}})

# JSON_FILE = 'data.json'

# def load_data():
#     try:
#         with open(JSON_FILE, 'r', encoding='utf-8') as file:
#             return json.load(file)
#     except FileNotFoundError:
#         data = {"appointments": []}
#         save_data(data)
#         return data

# def save_data(data):
#     with open(JSON_FILE, 'w', encoding='utf-8') as file:
#         json.dump(data, file, ensure_ascii=False, indent=4)

# @app.route('/appointments', methods=['GET'])
# def get_appointments():
#     data = load_data()
#     return jsonify(data)

# @app.route('/appointments', methods=['POST'])
# def add_appointment():
#     data = load_data()
#     new_appointment = request.json
#     data['appointments'].append(new_appointment)
#     save_data(data)
#     return jsonify({"message": "Appointment added successfully"}), 201

# @app.route('/appointments/<int:index>', methods=['DELETE'])
# def delete_appointment(index):
#     data = load_data()
#     if 0 <= index < len(data['appointments']):
#         removed = data['appointments'].pop(index)
#         save_data(data)
#         return jsonify({"message": "Запись успешно удалена", "deleted": removed}), 200
#     else:
#         return jsonify({"error": "Индекс не найден"}), 404

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)




import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Позволяет запросы CORS для всех доменов на всех путях
CORS(app, resources={r"/*": {"origins": "*"}})

JSON_FILE = 'data.json'

def load_data():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        data = {"count": 0, "appointments": []}
        save_data(data)
        return data

def save_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/appointments', methods=['GET'])
def get_appointments():
    data = load_data()
    return jsonify(data)

@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = load_data()
    new_appointment = request.json
    data['appointments'].append(new_appointment)
    data['count'] += 1
    save_data(data)
    return jsonify({"message": "Appointment added successfully", "count": data['count']}), 201

@app.route('/appointments/<int:index>', methods=['DELETE'])
def delete_appointment(index):
    data = load_data()
    if 0 <= index < len(data['appointments']):
        removed = data['appointments'].pop(index)
        data['count'] -= 1
        save_data(data)
        return jsonify({"message": "Запись успешно удалена", "deleted": removed}), 200
    else:
        return jsonify({"error": "Индекс не найден"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
