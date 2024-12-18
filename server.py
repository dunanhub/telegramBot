# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import json

# app = Flask(__name__)
# CORS(app, resources={r"/appointments/*": {"origins": "*"}})  # Разрешить все источники

# JSON_FILE = 'data.json'  # Путь к JSON файлу

# # Загрузка данных из JSON
# def load_data():
#     try:
#         with open(JSON_FILE, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         # В случае, если файл не найден, создаем начальную структуру данных
#         return {"count": 0, "appointments": []}

# # Сохранение данных в JSON
# def save_data(data):
#     with open(JSON_FILE, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

# def append_to_json(file_path, data):
#     try:
#         # Пытаемся открыть существующий файл для добавления данных
#         with open(file_path, 'r+', encoding='utf-8') as file:
#             file_data = json.load(file)
#             file_data.append(data)  # добавляем новые данные в список
#             file.seek(0)  # переходим в начало файла
#             json.dump(file_data, file, ensure_ascii=False, indent=4)
#     except FileNotFoundError:
#         # Если файл не существует, создаем новый
#         with open(file_path, 'w', encoding='utf-8') as file:
#             json.dump([data], file, ensure_ascii=False, indent=4)

# # Эндпоинт для получения всех записей
# @app.route('/appointments', methods=['GET'])
# def get_appointments():
#     data = load_data()
#     return jsonify(data)

# @app.route('/appointments', methods=['POST'])
# def add_appointment():
#     data = load_data()  # Загружаем существующие данные
#     new_appointment = request.json  # Получаем новую запись от клиента
#     data['appointments'].append(new_appointment)  # Добавляем в основной список записей
#     data['count'] += 1  # Увеличиваем счетчик записей

#     # Сохраняем данные в основном файле data.json
#     save_data(data)

#     # Добавляем запись в отдельный файл для истории
#     append_to_json('new_appointments.json', new_appointment)

#     # Возвращаем сообщение об успехе и текущий счетчик записей
#     return jsonify({"message": "Запись успешно добавлена", "count": data['count']}), 201

# # Эндпоинт для удаления записи
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
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

@app.route('/appointments', methods=['GET'])
def get_appointments():
    data = load_data()
    return jsonify(data)

@app.route('/counts', methods=['GET'])
def get_counts():
    try:
        with open('database.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return jsonify(data)  # Возвращает всё содержимое файла database.json
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = load_data()
    new_appointment = request.json
    data['appointments'].append(new_appointment)
    data['count'] += 1
    save_data(data)
    return jsonify({"message": "Запись успешно добавлена", "count": data['count']}), 201

@app.route('/appointments/<int:index>', methods=['DELETE'])
def delete_appointment(index):
    data = load_data()
    if 0 <= index < len(data['appointments']):
        removed = data['appointments'].pop(index)
        save_data(data)
        return jsonify({"message": "Запись успешно удалена", "deleted": removed}), 200
    else:
        return jsonify({"error": "Индекс не найден"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
