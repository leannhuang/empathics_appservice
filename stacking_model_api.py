import urllib.request
import json

def send_request_to_ml(rows):
    for row in rows:
        smile = row[4]
        anger = row[5]
        comtempt = row[6]
        disgust = row[7]
        fear = row[8]
        happiness = row[9]
        neutral = row[10]
        sadness = row[11]
        surprise = row[12]
        score_val = row[13]
        score_std = row[14]
        score_min = row[15]
        score_max = row[16]
        score_avg = row[17]
    data =  {

            "Inputs": {

                    "input1":
                    {
                        "ColumnNames": ["smile", "gender", "anger", "contempt", "disgust", "fear", "happiness", "neutral", "sadness", "surprise", "score_val", "score_std", "score_min", "score_max", "score_avg"],
                        #"Values": [ [ "0", "male", "0", "0", "0", "0", "1", "0", "0", "0", "0", "0", "0", "0", "0" ] ]
                        "Values": [ [ str(smile), "male", str(anger), str(comtempt), str(disgust), str(fear), str(happiness), str(neutral), str(sadness), str(surprise), str(score_val), str(score_std), str(score_min), str(score_max), str(score_avg) ] ]
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
        api_result = json.loads(result)
        neutral_probability  = api_result["Results"]["output1"]["value"]["Values"][0][0]
        negative_probability  = api_result["Results"]["output1"]["value"]["Values"][0][1]
        positive_probability  = api_result["Results"]["output1"]["value"]["Values"][0][2]
        label  = api_result["Results"]["output1"]["value"]["Values"][0][3]
        return str(label)

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read()))
