from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack, jsonify, send_file

import json

import requests
import os
import csv

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

    for place in weatherDataJson:
        place_name = place['place']
        place_id = place['place_id']
        time = ''
        timeend = ''
        if 'historicalDataDate' in place:
            time = place['historicalDataDate']
            timeend = place['historicalDataDateEnd']
        place_resp = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key=AIzaSyDdDSkPxQJETsjJGeQ8NkzTF31t-xw6BzU')
        place_resp_content = place_resp.content
        res = json.loads(place_resp_content, strict=False)

        longitude = res['result']['geometry']['location']['lng']
        latitude = res['result']['geometry']['location']['lat']

        weather_resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=e3b155955e28f330270ad5fab940d12c')
        weather_resp_content = weather_resp.content

        weather_res = json.loads(weather_resp_content, strict=False)

        if time != '' and timeend != '':
            daterange = compute_date_range(time, timeend)
            historical_weather_res = []
            for date in daterange:
                historical_weather_resp = requests.get(f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={date}&appid=72f82116224a0c24dd6370778714533d')
                historical_weather_resp_content = historical_weather_resp.content
                historical_weather_res.append(json.loads(historical_weather_resp_content, strict=False))
            # historical_weather_res
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

        
        weather_stats_to_return.append(weather_object)

    return jsonify(weather_stats_to_return)

@app.route('/download', methods=['GET'])
def excel():

    weather_stats_to_return = []
    weatherData = request.args.get('weatherData')
    weatherDataJson = json.loads(weatherData)

    for place in weatherDataJson:
        place_name = place['place']
        place_id = place['place_id']
        time = ''
        timeend = ''
        if 'historicalDataDate' in place:
            time = place['historicalDataDate']
            timeend = place['historicalDataDateEnd']
        place_resp = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key=AIzaSyDdDSkPxQJETsjJGeQ8NkzTF31t-xw6BzU')
        place_resp_content = place_resp.content
        res = json.loads(place_resp_content, strict=False)

        longitude = res['result']['geometry']['location']['lng']
        latitude = res['result']['geometry']['location']['lat']

        weather_resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=e3b155955e28f330270ad5fab940d12c')
        weather_resp_content = weather_resp.content

        weather_res = json.loads(weather_resp_content, strict=False)

        if time != '' and timeend != '':
            daterange = compute_date_range(time, timeend)
            historical_weather_res = []
            for date in daterange:
                historical_weather_resp = requests.get(f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={date}&appid=72f82116224a0c24dd6370778714533d')
                historical_weather_resp_content = historical_weather_resp.content
                historical_weather_res.append(json.loads(historical_weather_resp_content, strict=False))
            # historical_weather_res
        else:
            historical_weather_res = []
        
        weather_object = {
            'place_name': place_name,
            'currentWeather': weather_res,
            'longitude': longitude,
            'latitude': latitude,
            'place_id': place_id,
            'historical_data': historical_weather_res
        }

        weather_stats_to_return.append(weather_object)


    header = ['place_name', 'currentWeather', 'longitude', 'latitude', 'place_id', 'historical_data']
    with open('weatherdata.xlsx', 'w') as output:
        w = csv.DictWriter(output, header)
        w.writeheader()
        for weather_stats in weather_stats_to_return:
            w.writerow(weather_stats)

    print('sending file')
    path = os.getcwd()
    print(path)
    result = send_file(f'{path}/test.xlsx', attachment_filename="test.xlsx", as_attachment=True)

    print('deleting file')
    return result


def compute_date_range(startTime, endTime):
    ranges = []
    startTime = int(startTime)
    endTime = int(endTime)
    ranges.append(str(startTime))

    counter = startTime
    while counter < endTime:
        counter += 86400
        if counter < endTime:
            ranges.append(str(counter))
    
    ranges.append(str(endTime))

    return ranges
