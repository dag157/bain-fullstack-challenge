from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack

import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def timeline():

    test_api_call = requests.get('https://api.openweathermap.org/data/2.5/weather?lat=44.34&lon=10.99&appid=e3b155955e28f330270ad5fab940d12c')
    test_api_call_content = test_api_call.content

    return render_template('index.html', error=test_api_call_content)