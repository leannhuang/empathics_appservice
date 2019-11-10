import datetime
from flask import Flask, request
import werkzeug
import numpy
from CRUD_m import create_data
from CRUD_m import read_data
from CRUD_m import close_connection
from CRUD_m import get_connection
from process_image import processRequest

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


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


@app.route('/post_pic', methods = ['GET', 'POST'])
def handle_request():
    imagefile = request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
    print("\nReceived image File name : " + imagefile.filename)
    imagefile.save(filename)
    with open(filename, 'rb' ) as f:
        data = f.read()
    _url = 'https://westus2.api.cognitive.microsoft.com/face/v1.0/detect'
    _key = 'bc027dc227484433a77d7b613807d230' #Here you have to paste your primary key
    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _key
    headers['Content-Type'] = 'application/octet-stream'

    json = None
    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    }

    result = processRequest( json, data, headers, params, _url )
    print(result)
    return result
