import datetime
from flask import Flask, request
import werkzeug
import numpy
import uuid
import json
import soundfile as sf
import random
import os
import numpy as np
import tensorflow
from tensorflow.keras.models import Sequential
from python_speech_features import mfcc
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
    again = request.json['again']
    # upadte if record exists
    table_name = 'transaction_table'
    data = {'session_id':session_id, 'seq':seq, 'text_senti_score':text_senti_score}
    connection = get_connection()
    if again == '1':
        condition = {'session_id': session_id, 'seq': seq}
        connection = update_data(table_name, data, condition, connection)
    elif again == '0':
        connection = insert_data(table_name, data, connection)
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
    r_data = {'session_id':session_id, 'seq':seq }
    rows, number_rows = read_data(table_name, r_data, connection)
    emotion_label = send_request_to_ml(rows)
    features_data = {'result':emotion_label}
    update_data(table_name, features_data, condition, connection)
    close_connection(connection)
    return emotion_label


@app.route('/post_audio', methods = ['POST'])
def handle_audio():
    api_result = json.loads(request.form.get('data'))
    seq  = api_result["seq"]
    device_id  = api_result["device_id"]
    session_id  = api_result["session_id"]
    audiofile = request.files['audio']
    filename = werkzeug.utils.secure_filename(audiofile.filename)
    audiofile.save(filename)
    if filename is not None:
        signal,rate = sf.read(filename)
        wav_length = len(signal)/rate  #second
        window_length = 1
        # for index in range(sample_per_wav): # take ten windows in an audio file
        window_seed = random.uniform(0,abs(wav_length-window_length))
        window_range = (window_seed,window_seed+window_length)
        window_signal = signal[int(window_range[0]*rate):int(window_range[1]*rate)]

        mfcc_feat = mfcc(window_signal)
        mfcc_feat_scale = mfcc_feat / np.linalg.norm(mfcc_feat)
        mfcc_feat_scale = mfcc_feat_scale[np.newaxis,:]
        print(mfcc_feat_scale.shape)
                # result_array=(mfcc_feat-np.min(mfcc_feat))/np.ptp(mfcc_feat)

        model = tensorflow.keras.models.load_model('./model')
        predictions = model.predict(mfcc_feat_scale)
        print(predictions)
        into_sad_prob = predictions[0][0]
        into_angry_prob = predictions[0][1]
        into_happy_prob= predictions[0][2]
        into_neutral_prob = predictions[0][3]
        table_name = 'transaction_table'
        data = {'session_id':session_id, 'seq':seq, 'into_sad_prob': str(into_sad_prob), 'into_angry_prob': str(into_angry_prob), 'into_happy_prob': str(into_happy_prob), 'into_neutral_prob':str(into_neutral_prob)}
        r_data = {'session_id':session_id, 'seq':seq}
        connection = get_connection()
        row, number_rows = read_data(table_name, r_data, connection)
        if number_rows == 0:
            connection = insert_data(table_name, data, connection)
        else:
            condition = {'session_id': session_id, 'seq': seq}
            connection = update_data(table_name, data, condition, connection)
        return str(1)
    else:
        return str(0)
    # table_name = 'transaction_table'
    # data = {'session_id':session_id, 'seq':seq, 'into_sad_prob':text_senti_score, 'into_angry_prob':into_angry_prob, 'into_happy_prob':into_happy_prob, 'into_neutral_prob':into_neutral_prob}
    # r_data = {'session_id':session_id, 'seq':seq}
    # connection = get_connection()
    # row, number_rows = read_data(table_name, r_data, connection)
    # if number_rows == 0:
    #     connection = insert_data(table_name, data, connection)
    # else:
    #     condition = {'session_id': session_id, 'seq': seq}
    #     connection = update_data(table_name, data, condition, connection)
    # close_connection(connection)


@app.route('/post_pic', methods = ['GET','POST'])
def handle_request():
    api_result = json.loads(request.form.get('data'))
    seq  = api_result["seq"]
    device_id  = api_result["device_id"]
    session_id  = api_result["session_id"]
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

    json_ = None
    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    }
    result = processRequest( json_, data, headers, params, _url )
    connection = get_connection()
    if result == []:
        date_time = datetime.datetime.now()
        data = {'date':date_time, 'session_id':session_id, 'seq':seq, 'device_id':device_id, 'face_smile':0, 'face_anger':0, 'face_contempt':0, 'face_disgust':0, 'face_fear':0, 'face_happiness':0, 'face_neutral':0, 'face_sadness':0, 'face_surprise':0}
        table_name = 'transaction_table'
        condition = {'session_id': session_id, 'seq': seq}
        connection = update_data(table_name, data, condition, connection)
        close_connection(connection)
        return str(4)
    elif result is None:
        date_time = datetime.datetime.now()
        data = {'date':date_time, 'session_id':session_id, 'seq':seq, 'device_id':device_id, 'face_smile':0, 'face_anger':0, 'face_contempt':0, 'face_disgust':0, 'face_fear':0, 'face_happiness':0, 'face_neutral':0, 'face_sadness':0, 'face_surprise':0}
        table_name = 'transaction_table'
        condition = {'session_id': session_id, 'seq': seq}
        connection = update_data(table_name, data, condition, connection)
        close_connection(connection)
        return str(5)
    elif result[0]['faceAttributes'] is None:
        date_time = datetime.datetime.now()
        data = {'date':date_time, 'session_id':session_id, 'seq':seq, 'device_id':device_id, 'face_smile':0, 'face_anger':0, 'face_contempt':0, 'face_disgust':0, 'face_fear':0, 'face_happiness':0, 'face_neutral':0, 'face_sadness':0, 'face_surprise':0}
        table_name = 'transaction_table'
        condition = {'session_id': session_id, 'seq': seq}
        connection = update_data(table_name, data, condition, connection)
        close_connection(connection)
        return str(6)

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
    condition = {'session_id': session_id, 'seq': seq}
    connection = update_data(table_name, data, condition, connection)
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
    json_ = None
    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    }
    result = processRequest( json_, data, headers, params, _url )
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
