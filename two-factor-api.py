import urllib.request
# If you are using Python 3+, import urllib instead of urllib2

import json


data =  {

        "Inputs": {

                "input1":
                {
                    "ColumnNames": ["smile", "gender", "anger", "contempt", "disgust", "fear", "happiness", "neutral", "sadness", "surprise", "score_val", "score_std", "score_min", "score_max", "score_avg"],
                    "Values": [ [ "0", "male", "0", "0", "0", "0", "1", "0", "0", "0", "0", "0", "0", "0", "0" ] ]
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

    # If you are using Python 3+, replace urllib2 with urllib.request in the above code:
    # req = urllib.request.Request(url, body, headers)
    # response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())

    print(json.loads(error.read()))
