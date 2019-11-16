import datetime
from flask import Flask, request
import werkzeug
import numpy
import uuid
from CRUD_m import create_data
from CRUD_m import read_data
from CRUD_m import close_connection
from CRUD_m import get_connection
from CRUD_m import calculate_features
from process_image import processRequest
from stacking-model-api import send_request_to_ml

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

@app.route('/health_check', methods = ['GET'])
def health_check():
    return 'server is running'

@app.route('/get_session_id', methods = ['GET'])
def get_guid():
    return uuid.uuid4().hex

@app.route('/post_senti_socre', methods = ['POST'])
def handle_senti_socre_request():
    section_id = request.json['section_id']
    seq = request.json['seq']
    sentiment_score = request.json['sentiment_score']
    # upadte if record exists
    table_name = 'transaction_table'
    row = read_data(table_name, data)
    if row is None:
        create_data(table_name, data, connection)
    else:
        data =  {'section_id': section_id, 'seq': seq}
        condition = {'section_id': section_id, 'seq': seq}
        update_data(table_name, data, condition)
    close_connection(connection)
    return str(1)

@app.route('/post_ml', methods = ['POST'])
def handle_ml():
    section_id = request.json['section_id']
    seq = request.json['seq']
    table_name = 'transaction_table'
    calculate_features(section_id, seq)
    features_data =  {'section_id': section_id, 'seq': seq}
    condition = {'text_senti_avg': text_senti_avg, 'text_senti_std': text_senti_std, 'text_senti_min':text_senti_min, 'text_senti_max':text_senti_max}
    update_data(table_name, features_data, condition)
    data = {'section_id':section_id, 'seq':seq }
    row = read_data(table_name, data)
    emotion_label = send_request_to_ml(row)
    close_connection(connection)
    return emotion_label


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

@app.route('/post_pic', methods = ['GET','POST'])
def handle_request():
    #section_id = request.args.get('section_id')
    #seq = request.args.get('seq')
    #device_id = request.args.get('device_id')
    section_id = 'aa80d283431542f5a16adcdac91365ee'
    seq = 1
    device_id = 'vuzix_us_1116'
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
        return 'no face'
    elif result is None:
        return 'no picture'
    firstface_dic = result[0]
    faceAttributes_dic = firstface_dic['faceAttributes']
    smile = faceAttributes_dic['smile']
    gender = faceAttributes_dic['gender']
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
    data = {'date':date_time, 'session_id':section_id, 'seq':section_id, 'device_id':device_id, 'gender':gender, 'face_smile':smile, 'face_anger':anger, 'face_contempt':contempt, 'face_disgust':disgust, 'face_fear':fear, 'face_happiness':happiness, 'face_neutral':neutral, 'face_sadness':sadness, 'face_surprise':surprise}
    table_name = 'transaction_table'
    create_data(table_name, data, connection)
    close_connection(connection)
