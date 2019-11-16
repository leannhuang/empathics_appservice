import urllib.request
import json

def send_request_to_ml(row):
    smile = row.face_smile
    gender = row.gender
    anger = row.face_anger
    comtempt = row.face_contempt
    disgust = row.face_disgust
    fear = row.face_fear
    happiness = row.face_happiness
    neutral = row.face_neutral
    sadness = row.face_surprise
    surprise = row.face_surprise
    score_val = row.score_val
    score_std = row.score_std
    score_min = row.score_min
    score_max = row.score_max
    score_avg = row.score_avg
    data =  {

            "Inputs": {

                    "input1":
                    {
                        "ColumnNames": ["smile", "gender", "anger", "contempt", "disgust", "fear", "happiness", "neutral", "sadness", "surprise", "score_val", "score_std", "score_min", "score_max", "score_avg"],
                        #"Values": [ [ "0", "male", "0", "0", "0", "0", "1", "0", "0", "0", "0", "0", "0", "0", "0" ] ]
                        "Values": [ [ smile, gender, anger, comtempt, disgust, fear, happiness, neutral, sadness, surprise, score_val, score_std, score_min, score_max, score_avg ] ]
                    },        },
                    "GlobalParameters": {
                    }
            }

    body = str.encode(json.dumps(data))

    url = 'https://uswestcentral.services.azureml.net/workspaces/a347e2732701478c95c29c402a096563/services/e98ad950446b45c5afe46124fa5b70f9/execute?api-version=2.0&details=true'
    api_key = 'ueCSUAF94ecqtvDpO6uJhTEcRLTiMYEcxYSegAXmxTI00a29EGJudfQcZ66ZQilRhHDz3RM1FP8apJlA8LbI2g==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        neutral_probability = result["Results"]["output1"][ "value"]["Values"][0]
        negative_probability = result["Results"]["output1"][ "value"]["Values"][1]
        positive_probability = result["Results"]["output1"][ "value"]["Values"][2]
        label = result["Results"]["output1"][ "value"]["Values"][3]
        print(result)
        return label

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read()))
