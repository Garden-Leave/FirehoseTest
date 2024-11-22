from flask import  Flask,render_template,session,Response
import requests,json

app = Flask('read_and_display')

apiKey = '12D7272397E44873BF36A60DB4C0DF33'
apiKey_eu = '300207A2FA4D459789D4737FB73BFE49'
api_url = 'https://partners.dnaspaces.io/api/partners/v1/firehose/events'


@app.route('/iot',endpoint='iot')
def main():
    return Response(stream(),content_type='plain/text')


def stream():
    session = requests.Session()
    # session.headers = {'X-API-Key': apiKey}
    session.headers = {'X-API-Key': apiKey_eu}
    with session.get(api_url, stream=True) as response:
        if response.status_code == 200:
            # 逐块读取响应内容并流式输出
            for line in response.iter_lines():
                if line:  # 排除空的 chunk
                    decoded_line = line.decode('utf-8')
                    event = json.loads(decoded_line)
                    eventType = event['eventType']
                    if eventType == "IOT_TELEMETRY":
                        # print(event)
                        try:
                            ble_info = {}
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
                                      .format(ble_info['ibeacon_uuid'], ble_info['ibeacon_mac'],
                                              ble_info['ibeacon_major'], ble_info['ibeacon_minor']))
                            yield ble_info
                        except KeyError as e:
                            print(f"Missing key in event data: {e}")
                            continue  # Skip this event and continue
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                            continue  # Skip this event and continue
                        except Exception:
                            continue
        else:
            yield f"Error: {response.status_code}"
