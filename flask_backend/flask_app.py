from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack, jsonify

import json

import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def timeline():
    return render_template('index.html')

@app.route('/places', methods=['GET'])
def places():

    city = request.args.get('city')

    resp = requests.get(f'https://maps.googleapis.com/maps/api/place/autocomplete/json?input={city}&types=geocode&key=AIzaSyDdDSkPxQJETsjJGeQ8NkzTF31t-xw6BzU')
    resp_content = resp.content

    res = json.loads(resp_content, strict=False)

    return jsonify(res)

@app.route('/weather', methods=['GET'])
def weather():

    weather_stats_to_return = []
    weatherData = request.args.get('weatherData')
    weatherDataJson = json.loads(weatherData)

    print(weatherData)

    for place in weatherDataJson:
        place_name = place['place']
        place_id = place['place_id']
        time = ''
        if 'historicalDataDate' in place:
            time = place['historicalDataDate']
        place_resp = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key=AIzaSyDdDSkPxQJETsjJGeQ8NkzTF31t-xw6BzU')
        place_resp_content = place_resp.content
        res = json.loads(place_resp_content, strict=False)

        longitude = res['result']['geometry']['location']['lng']
        latitude = res['result']['geometry']['location']['lat']

        weather_resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=e3b155955e28f330270ad5fab940d12c')
        weather_resp_content = weather_resp.content

        weather_res = json.loads(weather_resp_content, strict=False)

        if time != '':
            historical_weather_res = []
            # historical_weather_resp = requests.get(f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={time}&appid=72f82116224a0c24dd6370778714533d')
            # historical_weather_resp_content = historical_weather_resp.content

            # historical_weather_res = json.loads(historical_weather_resp_content, strict=False)
        else:
            historical_weather_res = []
        
        weather_object = {
            'currentWeather': weather_res,
            'longitude': longitude,
            'latitude': latitude,
            'place_name': place_name,
            'place_id': place_id,
            'historical_data': historical_weather_res
        }

        print(weather_object)
        
        weather_stats_to_return.append(weather_object)

    return jsonify(weather_stats_to_return)