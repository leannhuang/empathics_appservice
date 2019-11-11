import os
from flask import Flask, request, redirect, url_for
import werkzeug

def test_upload():
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.app_context():
        client = app.test_client()
        file = open('./test_file.jpg', 'rb')
        resp = client.get(
            'http://empathics.azurewebsites.net/health_check',
            content_type='multipart/form-data',
            data={
                'file': (file, 'test_file.jpg'),
            },
        )
        print(resp)



test_upload()
