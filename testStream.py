import requests
import json
import socket

global temperature
global airPressure
global co2PPM
global humidity
global battery


apiKey = '12D7272397E44873BF36A60DB4C0DF33'
apiKey_eu = '300207A2FA4D459789D4737FB73BFE49'

###
# The following code is used to know the IP address of the machine used locally on which the server will be running.
###
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("8.8.8.8", 80))
# IP_ADRRESS = s.getsockname()[0]
# s.close()

url = 'http://127.0.0.1:5004'

###
# Starting the Firehose stream. Please change the url to dnaspaces.eu for customers hosted in the EU region.
###
session = requests.Session()
# session.headers = {'X-API-Key': apiKey}
session.headers = {'X-API-Key': apiKey_eu}
r = session.get(
    'https://partners.dnaspaces.io/api/partners/v1/firehose/events', stream=True)

###
# This piece of code decodes each event as it comes from the Firehose stream. Please change the event type or device mac address as needed.
# Once the telemetry information is available, the information is posted to the web server in JSON format.
###

uuid = '0588B8C58EFC4B86B66EB1968E3ADC8A'


for line in r.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        event = json.loads(decoded_line)
        eventType = event['eventType']
        print(event)
        if eventType == "IOT_TELEMETRY":
            # print(event)
            try:
                ble_info ={}
                ble_info['device_mac'] = event['iotTelemetry']['deviceInfo']['deviceMacAddress']
                ble_info['ibeacon_uuid'] = event['iotTelemetry']['iBeacon']['uuid']
                ble_info['ibeacon_mac'] = event['iotTelemetry']['iBeacon']['beacon_mac_address']
                ble_info['ibeacon_major'] = event['iotTelemetry']['iBeacon']['major']
                ble_info['ibeacon_minor'] = event['iotTelemetry']['iBeacon']['minor']
                ble_info['ibeacon_last_action'] = event['iotTelemetry']['LastUserAction']['type']
                ble_info['ibeacon_battory'] = event['iotTelemetry']['Battery']['value']
                ble_info['ibeacon_x'] = event['iotTelemetry']['DevicePosition']['x_pos']
                ble_info['ibeacon_y'] = event['iotTelemetry']['DevicePosition']['y_pos']
                ble_info['ibeacon_map_id'] = event['iotTelemetry']['DevicePosition']['map_id']
                ble_info['ibeacon_location_id'] = event['iotTelemetry']['DevicePosition']['location_id']
                ble_info['ibeacon_last_seen'] = event['iotTelemetry']['DevicePosition']['last_located_time']

                if ble_info['ibeacon_uuid'] == 'FDA50693-A4E2-4FB1-AFCF-C6EB07647825':
                    ble_info['brand'] = 'Sensetime'
                    print('''sensetime ble tag found, uuid: {} mac: {} major: {} minor: {}'''
                    .format(ble_info['ibeacon_uuid'],ble_info['ibeacon_mac'],ble_info['ibeacon_major'],ble_info['ibeacon_minor']))
                    payload = {'ble_deivce_info'}
            except:
                continue


            #
            # if deviceMacAddress == 'e2:66:43:1b:cc:07':
            #     try:
            #         temperature = event['iotTelemetry']['temperature']['temperatureInCelsius']
            #         payload = {'temperature': str(temperature)}
            #         r = requests.post(url, json=payload)
            #     except:
            #         continue  # 有异常直接跳过  继续读下一行
            # elif deviceMacAddress == 'cd:c5:34:a6:92:e6':
            #     try:
            #         airPressure = event['iotTelemetry']['airPressure']['pressure']
            #         payload = {'airPressure': str(airPressure)}
            #         r = requests.post(url, json=payload)
            #     except:
            #         continue
            # elif deviceMacAddress == '68:27:19:3b:cd:4a':
            #     try:
            #         co2PPM = event['iotTelemetry']['carbonEmissions']['co2Ppm']
            #         payload = {'co2PPM': str(co2PPM)}
            #         r = requests.post(url, json=payload)
            #     except:
            #         continue
            # elif deviceMacAddress == 'cd:c5:34:a6:92:e6':
            #     try:
            #         humidity = event['iotTelemetry']['humidity']['humidityInPercentage']
            #         payload = {'humidity': str(humidity)}
            #         r = requests.post(url, json=payload)
            #     except:
            #         continue
            # elif deviceMacAddress == 'f8:20:d5:9d:91:ad':
            #     try:
            #         battery = event['iotTelemetry']['battery']['value']
            #         payload = {'battery': str(battery)}
            #         r = requests.post(url, json=payload)
            #     except:
            #         continue

