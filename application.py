import datetime
from flask import Flask, request
import werkzeug
import numpy
import uuid
import json
from CRUD_m import insert_data
from CRUD_m import create_data
from CRUD_m import read_data
from CRUD_m import update_data
from CRUD_m import close_connection
from CRUD_m import get_connection
from CRUD_m import calculate_features
from process_image import processRequest
from stacking_model_api import send_request_to_ml

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

@app.route('/health_check', methods = ['GET'])
def health_check():
    return 'server is running'

@app.route('/get_session_id', methods = ['GET'])
def get_guid():
    return uuid.uuid4().hex

@app.route('/post_senti_score', methods = ['POST'])
def handle_senti_score_request():
    session_id = request.json['session_id']
    seq = request.json['seq']
    text_senti_score = request.json['sentiment_score']
    # upadte if record exists
    table_name = 'transaction_table'
    data = {'session_id':session_id, 'seq':seq, 'text_senti_score':text_senti_score}
    r_data = {'session_id':session_id, 'seq':seq}
    connection = get_connection()
    row, number_rows = read_data(table_name, r_data, connection)
    if number_rows == 0:
        connection = insert_data(table_name, data, connection)
    else:
        condition = {'session_id': session_id, 'seq': seq}
        connection = update_data(table_name, data, condition, connection)
    close_connection(connection)
    return str(1)

@app.route('/post_ml', methods = ['POST'])
def handle_ml():
    session_id = request.json['session_id']
    seq = request.json['seq']
    table_name = 'transaction_table'
    connection = get_connection()
    text_senti_avg, text_senti_std, text_senti_min, text_senti_max = calculate_features(table_name, session_id, seq, connection)
    condition =  {'session_id': session_id, 'seq': seq}
    features_data = {'text_senti_avg': text_senti_avg, 'text_senti_std': text_senti_std, 'text_senti_min':text_senti_min, 'text_senti_max':text_senti_max}
    update_data(table_name, features_data, condition, connection)
    data = {'session_id':session_id, 'seq':seq }
    rows, number_rows = read_data(table_name, data, connection)
    emotion_label = send_request_to_ml(rows)
    features_data = {'result':emotion_label}
    update_data(table_name, features_data, condition, connection)
    close_connection(connection)
    return emotion_label


@app.route('/post_audio', methods = ['POST'])
def handle_audio():
    audioefile = request.files['audio']
    filename = werkzeug.utils.secure_filename(audiofile.filename)
    audioefile.save(filename)
    session_id = request.json['session_id']
    seq = request.json['seq']
    connection = get_connection()
    table_name = 'transaction_table'
    text_senti_avg, text_senti_std, text_senti_min, text_senti_max = calculate_features(table_name, session_id, seq, connection)
    condition =  {'session_id': session_id, 'seq': seq}
    features_data = {'text_senti_avg': text_senti_avg, 'text_senti_std': text_senti_std, 'text_senti_min':text_senti_min, 'text_senti_max':text_senti_max}
    update_data(table_name, features_data, condition, connection)
    data = {'session_id':session_id, 'seq':seq }
    rows, number_rows = read_data(table_name, data, connection)
    emotion_label = send_request_to_ml(rows)
    close_connection(connection)
    return emotion_label

@app.route('/post_pic', methods = ['GET','POST'])
def handle_request():
    section_id = request.args.get('section_id')
    seq = request.args.get('seq')
    device_id = request.args.get('device_id')
    # session_id = 'aa80d283431542f5a16adcdac91365ex'
    # seq = '1'
    # device_id = 'vuzix_us_1116'
    imagefile = request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
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
    connection = get_connection()
    if result == []:
        date_time = datetime.datetime.now()
        data = {'date':date_time, 'session_id':session_id, 'seq':seq, 'device_id':device_id, 'face_smile':0, 'face_anger':0, 'face_contempt':0, 'face_disgust':0, 'face_fear':0, 'face_happiness':0, 'face_neutral':0, 'face_sadness':0, 'face_surprise':0}
        table_name = 'transaction_table'
        r_data = {'session_id':session_id, 'seq':seq}
        row, number_rows = read_data(table_name, r_data, connection)
        if number_rows == 0:
            connection = insert_data(table_name, data, connection)
        else:
            condition = {'session_id': session_id, 'seq': seq}
            connection = update_data(table_name, data, condition, connection)
        close_connection(connection)
        return str(4)
    elif result is None:
        date_time = datetime.datetime.now()
        data = {'date':date_time, 'session_id':session_id, 'seq':seq, 'device_id':device_id, 'face_smile':0, 'face_anger':0, 'face_contempt':0, 'face_disgust':0, 'face_fear':0, 'face_happiness':0, 'face_neutral':0, 'face_sadness':0, 'face_surprise':0}
        table_name = 'transaction_table'
        r_data = {'session_id':session_id, 'seq':seq}
        row, number_rows = read_data(table_name, r_data, connection)
        if number_rows == 0:
            connection = insert_data(table_name, data, connection)
        else:
            condition = {'session_id': session_id, 'seq': seq}
            connection = update_data(table_name, data, condition, connection)
        close_connection(connection)
        return str(5)

    firstface_dic = result[0]
    faceAttributes_dic = firstface_dic['faceAttributes']
    smile = faceAttributes_dic['smile']
    #gender = faceAttributes_dic['gender']
    anger = faceAttributes_dic['emotion']['anger']
    contempt = faceAttributes_dic['emotion']['contempt']
    disgust = faceAttributes_dic['emotion']['disgust']
    fear = faceAttributes_dic['emotion']['fear']
    happiness = faceAttributes_dic['emotion']['happiness']
    neutral = faceAttributes_dic['emotion']['neutral']
    sadness = faceAttributes_dic['emotion']['sadness']
    surprise = faceAttributes_dic['emotion']['surprise']
    connection = get_connection()
    date_time = datetime.datetime.now()
    data = {'date':date_time, 'session_id':session_id, 'seq':seq, 'device_id':device_id, 'face_smile':smile, 'face_anger':anger, 'face_contempt':contempt, 'face_disgust':disgust, 'face_fear':fear, 'face_happiness':happiness, 'face_neutral':neutral, 'face_sadness':sadness, 'face_surprise':surprise}
    table_name = 'transaction_table'
    connection = insert_data(table_name, data, connection, connection)
    close_connection(connection)
    return str(1)

@app.route('/post_pic_1', methods = ['GET','POST'])
def handle_request_post_pic_1():
    # data = request.form.get('data')
    api_result = json.loads(request.form.get('data'))
    seq  = api_result["seq"]
    device_id  = api_result["device_id"]
    session_id  = api_result["session_id"]
    imagefile = request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
    imagefile.save(filename)
    return seq


@app.route('/post_pic_test', methods = ['POST'])
def handle_request_test():
    imagefile = request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
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
    if result == []:
        return str(4) # no face
    elif result is None:
        return str(5) # no picture
    firstface_dic = result[0]
    faceAttributes_dic = firstface_dic['faceAttributes']
    gender = faceAttributes_dic['gender']
    smile = faceAttributes_dic['smile']
    anger = faceAttributes_dic['emotion']['anger']
    contempt = faceAttributes_dic['emotion']['contempt']
    disgust = faceAttributes_dic['emotion']['disgust']
    fear = faceAttributes_dic['emotion']['fear']
    happiness = faceAttributes_dic['emotion']['happiness']
    neutral = faceAttributes_dic['emotion']['neutral']
    sadness = faceAttributes_dic['emotion']['sadness']
    surprise = faceAttributes_dic['emotion']['surprise']
    neg_emotion_list = [anger, contempt, disgust, fear, sadness, surprise]
    if max(neg_emotion_list) > 0.01:
        return str(1) # negative
    elif smile > 0.8:
        return str(2) # positive
    else:
        return str(0) # neutral
