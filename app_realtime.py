from flask import  Flask,render_template,session,Response
import requests,json

app = Flask('read_and_display')

apiKey = '12D7272397E44873BF36A60DB4C0DF33'
apiKey_eu = '300207A2FA4D459789D4737FB73BFE49'
api_url_io = 'https://partners.dnaspaces.io/api/partners/v1/firehose/events'
api_url_eu = 'https://partners.dnaspaces.eu/api/partners/v1/firehose/events'
test_api_url = 'http://127.0.0.1:5002/stream_out'


@app.route('/',endpoint='iot')
def main():
    # return Response(stream(),mimetype="text/event-stream")
    return Response(stream(), content_type='application/json')


def stream():
    # session.headers = {'X-API-Key': apiKey}
    headers = {'X-API-Key': apiKey_eu}

    # with session.get(test_api_url, stream=True) as response:
    with requests.get(api_url_eu, stream=True,headers=headers) as response:
        if response.status_code == 200:
            # 逐块读取响应内容并流式输出
            for line in response.iter_lines():
                if line:  # 排除空的 chunk
                    decoded_line = line.decode('utf-8')
                    # print(decoded_line)
                    event = json.loads(decoded_line)
                    # print(event)
                    eventType = event['eventType']
                    print(eventType)
                    if eventType == "IOT_TELEMETRY":
                        # print(event)
                        ble_info = {}
                        ble_info['device_mac'] = event['iotTelemetry']['deviceInfo']['deviceMacAddress']
                        ble_info['ibeacon_location_x'] = event['iotTelemetry']['detectedPosition']['xPos']
                        ble_info['ibeacon_location_y'] = event['iotTelemetry']['detectedPosition']['yPos']
                        try: #判断BLE类型  是否ibeacon
                            ibeacon_flag= event['iotTelemetry']['iBeacon']
                        except KeyError as e:
                            print(f"ibeacon filed not existing: {e}")
                            ble_info['brand']='BLE device but not iBeacon'
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                        except Exception:
                            print("Unknown exception occurred")
                        else:
                            print(event)
                            if event['iotTelemetry']['iBeacon']['uuid'] == "fda50693-a4e2-4fb1-afcf-c6eb07647825":
                                ble_info['ibeacon_uuid'] = event['iotTelemetry']['iBeacon']['uuid']
                                ble_info['ibeacon_mac'] = event['iotTelemetry']['iBeacon']['beaconMacAddress']
                                ble_info['ibeacon_major'] = event['iotTelemetry']['iBeacon']['major']
                                ble_info['ibeacon_minor'] = event['iotTelemetry']['iBeacon']['minor']
                                ble_info['brand'] = 'Sensetime Beacon'
                            else:
                                ble_info['brand'] = 'iBeacon device but other brand'
                            # print('''sensetime ble tag found, uuid: {} mac: {} major: {} minor: {}'''
                            #       .format(ble_info['ibeacon_uuid'], ble_info['ibeacon_mac'],
                            #               ble_info['ibeacon_major'], ble_info['ibeacon_minor']))
                        finally:
                            yield json.dumps(ble_info).encode('utf-8') + b'\n\n'
                        # ble_info['ibeacon_last_action'] = event['iotTelemetry']['last_user_action']['type']
                        # # ble_info['ibeacon_last_action'] = 'dummy'
                        # ble_info['ibeacon_battory'] = event['iotTelemetry']['battery']['value']

                        # # ble_info['ibeacon_map_id'] = event['iotTelemetry']['DevicePosition']['map_id']
                        # ble_info['ibeacon_location_id'] = event['iotTelemetry']['DevicePosition']['location_id']
                        # ble_info['ibeacon_last_seen'] = event['iotTelemetry']['DevicePosition']['last_located_time']

                        # # 假设只有FDA50693-A4E2-4FB1-AFCF-C6EB07647825这个uuid是Sensetime
                        # if ble_info['ibeacon_uuid'] == 'FDA50693-A4E2-4FB1-AFCF-C6EB07647825':
                        #     ble_info['brand'] = 'Sensetime'
                        #     print('''sensetime ble tag found, uuid: {} mac: {} major: {} minor: {}'''
                        #           .format(ble_info['ibeacon_uuid'], ble_info['ibeacon_mac'],
                        #                   ble_info['ibeacon_major'], ble_info['ibeacon_minor']))

                        # 不encode的话还是string 需要转化为字节流bytes
                        # resp = json.dumps(ble_info).encode('utf-8')
                        # yield resp + b'\n'
                    else:
                        # yield json.dumps(event).encode('utf-8') + b'\n\n'
                        yield "Non-IoT event, Will not Parse\n\n"# 非IOT 什么也不输出
        else:
            print('request failed not 200')
            yield f"Error: {response.status_code}"


if __name__ == '__main__':
    # stream()
    app.run(port=5012)