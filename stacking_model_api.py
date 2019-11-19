import urllib.request
import json

def send_request_to_ml(row):
    smile = row[0]
    gender = row[1]
    anger = row[2]
    comtempt = row[3]
    disgust = row[4]
    fear = row[5]
    happiness = row[6]
    neutral = row[7]
    sadness = row[8]
    surprise = row[9]
    score_val = row[10]
    score_std = row[11]
    score_min = row[12]
    score_max = row[13]
    score_avg = row[14]
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
