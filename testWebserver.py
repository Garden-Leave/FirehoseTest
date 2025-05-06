import json
from flask import Flask, request

# 全局变量 + html网页每5s自动刷新的方式
app = Flask('auto_refresh')

###
# Defining the default value of the telemetry variable until they are overwritten by incoming information.
###

temperature = 'unknown'
airPressure = 'unknown'
co2PPM = 'unknown'
humidity = 'unknown'
battery = 'unknown'


@app.route('/', methods=['GET', 'POST'])
# default routing (whenever someone navigates to / run main page); accepts both GET and POST methods
def main_page():
    global temperature
    global airPressure
    global co2PPM
    global humidity
    global battery

    if request.method == 'GET':
        temperature = str(temperature)
        return '''
        <html>
         <meta http-equiv="refresh" content="5" />
            <head>
                <title>Sample Firehose Application Test</title>
            </head>
            <body style="color: white; font-family: Futura; text-align: center; background-color:green">
                <div style="display: inline-block; width: 100%; white-space: nowrap;">
                    <h1 style="float: left; padding-left: 10px; font-size: 30px"> Hope this sample app helps you understand the Cisco DNA Spaces Firehose API </h1>
                    <table border="1"  width="100%">
                        <tr><!-- Headings -->
                            <th>Temperature</th>
                            <th>Air Pressure</th>
                            <th>CO2 PPM</th>
                            <th>Humidity</th>
                            <th>Battery</th>
                        </tr>
                        <tr>
                            <td align="center">'''+temperature+'''</td>
                            <td align="center">'''+airPressure+'''</td>
                            <td align="center">'''+co2PPM+'''</td>
                            <td align="center">'''+humidity+'''</td>
                            <td align="center">'''+battery+'''</td>
                        </tr>
                    </table>
                </div>
            </body>
        </html>'''
    # if its a post request, strip the data of the number of people and update the people variable with it
    elif request.method == 'POST':
        data = request.data
        data = data.decode("utf-8")
        data = json.loads(data)
        print (data)
        result = update_data(data)
        return result


def update_data(data):
    global temperature
    global airPressure
    global co2PPM
    global humidity
    global battery
    try:
        temperature = data['temperature']
    except:
        pass
    try:
        airPressure = data['airPressure']
    except:
        pass
    try:
        co2PPM = data['co2PPM']
    except:
        pass
    try:
        humidity = data['humidity']
    except:
        pass
    try:
        battery = data['battery']
    except:
        pass
    return "Success"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5004"), debug=True)
