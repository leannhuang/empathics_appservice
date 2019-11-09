import datetime
from flask import Flask, request
from CRUD_m import create_data
from CRUD_m import read_data
from CRUD_m import close_connection
from CRUD_m import get_connection

app = Flask(__name__)

@app.route("/paddle_count", methods = ['POST'])
def paddle_count():
    patient_id = request.json['patient_id']
    device_id = request.json['device_id']
    connection = get_connection()
    date_time = datetime.datetime.now()
    data = {'patient_id':patient_id, 'device_id':device_id, 'medium_count':1, 'time':date_time}
    table_name = 'pedal'
    create_data(table_name, data, connection)
    close_connection(connection)
    return str(1)


@app.route("/register_device", methods = ['POST'])
def register_device():
    patient_id = request.json['patient_id']
    device_id = request.json['device_id']
    date_time = datetime.datetime.now()
    connection = get_connection()
    table_name = 'dp_pair'

    data = {'device_id':device_id}
    row = read_data(table_name, data)
    #scenario 2: No such device_id
    if row is None:
        return str(2)
    #scenario 1: Successful
    elif row.patient_id is None:
        return str(1)
        data =  {'patient_id': patient_id}
        condition = {'device_id': device_id}
        update_data(table_name, data, condition)
    #scenario 2: duplicated id
    else:
        return str(0)

@app.route("/return_device", methods = ['POST'])
def return_device():
    patient_id = request.json['patient_id']
    device_id = request.json['device_id']
    date_time = datetime.datetime.now()
    table_name = 'dp_pair'
    row = read_data(table_name, data)
    # device has been returned
    if row.patient_id is None:
        return str(0)
    else:
        data =  {'patient_id': None}
        condition = {'device_id': device_id}
        update_data(table_name, data, condition)

@app.route('/health_check', methods = ['GET'])
def health_check():
    return 'server is running'
