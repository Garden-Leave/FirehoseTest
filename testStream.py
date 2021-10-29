import requests
import json
import socket

global temperature
global airPressure
global co2PPM
global humidity
global battery

###
# The API key should be added once the Application has been created in the Partner Dashboard.
###

apiKey = 'B7DADDF33A344D9B9C5DD39D2A3C4B9F'

###
# The following code is used to know the IP address of the machine used locally on which the server will be running.
###
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IP_ADRRESS = s.getsockname()[0]
s.close()
url = 'http://' + str(IP_ADRRESS) + '/'

###
# Starting the Firehose stream. Please change the url to dnaspaces.eu for customers hosted in the EU region.
###
s = requests.Session()
s.headers = {'X-API-Key': apiKey}
r = s.get(
    'https://partners.dnaspaces.io/api/partners/v1/firehose/events', stream=True)

###
# This piece of code decodes each event as it comes from the Firehose stream. Please change the event type or device mac address as needed.
# Once the telemetry information is available, the information is posted to the web server in JSON format.
###

for line in r.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        event = json.loads(decoded_line)
        eventType = event['eventType']
        if eventType == "IOT_TELEMETRY":
            deviceMacAddress = event['iotTelemetry']['deviceInfo']['deviceMacAddress']
            if deviceMacAddress == 'e2:66:43:1b:cc:07':
                try:
                    temperature = event['iotTelemetry']['temperature']['temperatureInCelsius']
                    payload = {'temperature': str(temperature)}
                    r = requests.post(url, json=payload)
                except:
                    continue
            elif deviceMacAddress == 'cd:c5:34:a6:92:e6':
                try:
                    airPressure = event['iotTelemetry']['airPressure']['pressure']
                    payload = {'airPressure': str(airPressure)}
                    r = requests.post(url, json=payload)
                except:
                    continue
            elif deviceMacAddress == '68:27:19:3b:cd:4a':
                try:
                    co2PPM = event['iotTelemetry']['carbonEmissions']['co2Ppm']
                    payload = {'co2PPM': str(co2PPM)}
                    r = requests.post(url, json=payload)
                except:
                    continue
            elif deviceMacAddress == 'cd:c5:34:a6:92:e6':
                try:
                    humidity = event['iotTelemetry']['humidity']['humidityInPercentage']
                    payload = {'humidity': str(humidity)}
                    r = requests.post(url, json=payload)
                except:
                    continue
            elif deviceMacAddress == 'f8:20:d5:9d:91:ad':
                try:
                    battery = event['iotTelemetry']['battery']['value']
                    payload = {'battery': str(battery)}
                    r = requests.post(url, json=payload)
                except:
                    continue

