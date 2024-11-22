import requests, sys
from flask import Flask, request, jsonify, render_template
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')
from web_server.Web_API_Wrappers import get_data, update_data

app = Flask(__name__)

WEB_SERVER_BASE_URL = 'http://web_server.sergei/'

@app.route('/')
def index():
    
    query = 'SELECT id FROM plants'
    
    response = get_data(query, True)
    plants = response.json()
    return render_template('index.html', plants=plants)

@app.route('/get_plant/<int:plant_id>', methods=['GET'])
def get_plant(plant_id):
    params = {
        'query': f'SELECT * FROM plants WHERE id = {plant_id}',
        'dictionary': True
    }
    response = requests.get(f'{WEB_SERVER_BASE_URL}/get', params=params)
    plant = response.json()
    return jsonify(plant)

@app.route('/update_plant', methods=['POST'])
def update_plant():
    data = request.json
    update_query = f"""
        UPDATE plants
        SET IP = '{data['IP']}', MAC = '{data['MAC']}', port = {data['port']}, location = '{data['location']}',
            notify_today = {data['notify_today']}, error_flag = {data['error_flag']}, power = '{data['power']}',
            last_measurment = '{data['last_measurment']}', next_measurment = '{data['next_measurment']}',
            main_group_id = {data['main_group_id']}, if_home_group_id = {data['if_home_group_id']},
            admin_id = {data['admin_id']}, min_measure = {data['min_measure']}
        WHERE id = {data['id']}
    """
    params = {
        'query': update_query
    }
    response = requests.get(f'{WEB_SERVER_BASE_URL}/update', params=params)
    return jsonify({"message": "Plant updated successfully"})

if __name__ == '__main__':
    app.run(debug=True)
