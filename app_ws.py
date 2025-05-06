from flask import Flask
from flask_socketio import SocketIO
import time
import json
import threading
import requests
from  datetime import datetime,timedelta

#在flask里使用websocket来发送事件,前端动态更新数据，不使用http stream


api_url_eu = 'https://partners.dnaspaces.eu/api/partners/v1/firehose/events'
apiKey_eu = '300207A2FA4D459789D4737FB73BFE49'
stuuid = 'fda50693a4e24fb1afcfc6eb07647825'

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


def data_stream():
    while True:
        socketio.emit('sensor_update', {
            'temperature': '23.5',
            'humidity': '60%',
            'battery': '82%',
        })
        time.sleep(2)


def stream_and_emit():
    headers = {'X-API-Key': apiKey_eu}
    with requests.get(api_url_eu, stream=True, verify=False,headers=headers) as resp:
        if resp.status_code == 200:
            for line in resp.iter_lines():
                if line:  # 排除空的 chunk
                    decoded_line = line.decode('utf-8')
                    event = json.loads(decoded_line)
                    eventType = event['eventType']
                    if eventType == "IOT_TELEMETRY":
                        # print(event)
                        ble_info = {}
                        info1 = {}
                        try:  # 判断BLE类型  是否ibeacon
                            ibeacon_flag = event['iotTelemetry']['iBeacon']
                        except KeyError as e:
                            print(f"ibeacon field not existing: {e}")
                            ble_info['brand'] = 'IoT event but not iBeacon'
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                        except Exception:
                            print("Unknown exception occurred")
                        else:
                            # print(event)
                            if event['iotTelemetry']['iBeacon']['uuid'] == stuuid:
                                # major 20103  minor  21968
                                major = event['iotTelemetry']['iBeacon']['major']
                                minor = event['iotTelemetry']['iBeacon']['minor']
                                # print(major,minor)
                                info1['x'] = event['iotTelemetry']['detectedPosition']['xPos']
                                info1['y'] = event['iotTelemetry']['detectedPosition']['yPos']
                                info1['uuid'] = stuuid
                                info1['mac'] = event['iotTelemetry']['iBeacon']['beaconMacAddress']
                                info1['major'] = str(major)
                                info1['minor'] = str(minor)
                                ts1 = float(event['iotTelemetry']['detectedPosition'][
                                                'lastLocatedTime']) / 1000
                                ts2 = datetime.utcfromtimestamp(ts1)
                                delta = timedelta(hours=4)
                                last_time = ts2 + delta
                                info1['last_seen'] = str(last_time)
                                info1['rssi'] = event['iotTelemetry']['maxDetectedRssi']
                                # if  major == '20103' and ['minor'] in ['22613','23415']:
                                if major == 20103:
                                    try:
                                        print(info1)
                                        yield json.dumps(info1).encode('utf-8') + b'\n\n'
                                    except TypeError as e:
                                        print(e)
                                else:
                                    yield " "
                            else:
                                yield ""
                            # else:
                            #     ble_info['brand'] = 'iBeacon device but not Sensetime'
                            # print('''sensetime ble tag found, uuid: {} mac: {} major: {} minor: {}'''
                            #       .format(ble_info['ibeacon_uuid'], ble_info['ibeacon_mac'],
                            #               ble_info['ibeacon_major'], ble_info['ibeacon_minor']))
                        finally:
                            pass
                    else:
                        yield " "  # 非IOT 什么也不输出
            else:
                print('cisco request failed')
                yield f"Error: {resp.status_code}"


@app.route('/')
def index():
    return "WebSocket backend is running"


@socketio.on('connect')
def on_connect():
    print('Client connected')



if __name__ == '__main__':
    threading.Thread(target=data_stream).start()
    socketio.run(app, host='0.0.0.0', port=5004)
