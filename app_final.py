from flask import Flask,render_template, request,session,redirect,url_for,jsonify
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
aduuid = '4c5b8a1392ea4f779eb51b723d26a8c2'
apuuid = 'd3c9e1f22b3a4f619c269bb8ae56b614'
altuuid = '2f234454cf6d4a0fadf2f4911ba9ffa6'

app = Flask('ble_ws',template_folder='.')
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = 'jordan1992'
USERNAME = 'sw'
PASSWORD = 'sw'
uuid_list = ['fda50693a4e24fb1afcfc6eb07647825','4c5b8a1392ea4f779eb51b723d26a8c2']
minor_list = [20103]
major_list = [22613]


stream_thread = None
stop_event = threading.Event()


def data_stream():
    while True:
        socketio.emit('sensor_update', {
            'temperature': '23.5',
            'humidity': '60%',
            'battery': '82%',
        })
        time.sleep(2)


def stream_and_emit():
    global uuid_list
    global major_list
    global minor_list
    global stop_event
    minor_set = set()
    best_rssi = []
    print('emit func running')
    headers = {'X-API-Key': apiKey_eu}
    while not stop_event.is_set():
        with requests.get(api_url_eu, stream=True, verify=False,headers=headers) as resp:
            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if stop_event.is_set():  # ⛔ 如果设置了停止，退出循环
                        print("[stream_and_emit] Stop requested, exiting thread.")
                        break
                    if line:  # 排除空的 chunk
                        decoded_line = line.decode('utf-8')
                        event = json.loads(decoded_line)
                        eventType = event['eventType']
                        if eventType == "IOT_TELEMETRY":
                            # print(event)
                            ble_info = {}
                            info1 = {}
                            try:  # 判断BLE类型
                                ibeacon_flag = event['iotTelemetry']['iBeacon']
                            except KeyError as e:
                                # print(f"ibeacon field not existing: {e}")
                                ble_info['brand'] = 'IoT event but not iBeacon'
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}")
                            except Exception:
                                print("Unknown exception occurred")
                            else:
                                # print(event)
                                uuid = event['iotTelemetry']['iBeacon']['uuid']
                                if  uuid in uuid_list:
                                    # major 20103  minor  21968
                                    # print(event)
                                    major = event['iotTelemetry']['iBeacon']['major']
                                    minor = event['iotTelemetry']['iBeacon']['minor']
                                    rssi = event['iotTelemetry']['maxDetectedRssi']
                                    # if major == 999 or major == 888:
                                    #     # print(type(major))
                                    #     print(major,minor)
                                    info1['x'] = event['iotTelemetry']['detectedPosition']['xPos']
                                    info1['y'] = event['iotTelemetry']['detectedPosition']['yPos']
                                    info1['location_id'] = event['iotTelemetry']['detectedPosition']['locationId']
                                    info1['floor_number'] = event['iotTelemetry']['location']['floorNumber']
                                    info1['uuid'] = 'phone'
                                    info1['mac'] = event['iotTelemetry']['iBeacon']['beaconMacAddress']
                                    info1['major'] = str(major)
                                    info1['minor'] = str(minor)
                                    minor_set.add(minor)
                                    best_rssi.append(rssi)
                                    # print(f'number of beacons found: {len(minor_set)}')
                                    # print(f'best rssi {max(best_rssi)}')
                                    # print(f'avg rssi {round((sum(best_rssi) / len(best_rssi)),1)}')

                                    ts1 = float(event['iotTelemetry']['detectedPosition'][
                                                    'lastLocatedTime']) / 1000
                                    ts2 = datetime.utcfromtimestamp(ts1)
                                    delta = timedelta(hours=4)
                                    last_time = ts2 + delta
                                    info1['last_seen'] = str(last_time)
                                    info1['max_rssi'] = rssi
                                    # if  major in [888,999,20103] and minor in [22613,999]:
                                    if major in major_list and minor in minor_list:
                                        print(event)
                                        try:
                                            # print(info1)
                                            socketio.emit('location_update',info1)
                                        except TypeError as e:
                                            print(e)
                                    else:
                                        pass
                                else:
                                    pass
                                # else:
                                #     ble_info['brand'] = 'iBeacon device but not Sensetime'
                                # print('''sensetime ble tag found, uuid: {} mac: {} major: {} minor: {}'''
                                #       .format(ble_info['ibeacon_uuid'], ble_info['ibeacon_mac'],
                                #               ble_info['ibeacon_major'], ble_info['ibeacon_minor']))
                            finally:
                                pass
                        else:
                            pass
            else:
                print('cisco request failed')
                    # yield f"Error: {resp.status_code}"
    print("[stream_and_emit] Stop requested, exiting thread.")

def start_streaming_thread():
    global stream_thread
    if stream_thread is None or not stream_thread.is_alive():
        stop_event.clear()  # 允许线程运行
        stream_thread = threading.Thread(target=stream_and_emit, daemon=True)
        stream_thread.start()
        print("Streaming thread started")

def stop_streaming_thread():
    stop_event.set()  # 请求线程停止
    print("Streaming thread stop requested")



@app.route('/update', methods=['POST'])
def update():
    global uuid_list
    global major_list
    global minor_list
    try:
        data = request.get_json(force=True)
        uuid_raw = data.get('uuid', '')
        major_raw = data.get('major', '')
        minor_raw = data.get('minor', '')
        # 转换为列表（去除空项、去除前后空格）
        uuid_list = [item.strip() for item in uuid_raw.split(',') if item.strip()]
        major_list = [int(item.strip()) for item in major_raw.split(',') if item.strip()]
        minor_list = [int(item.strip() )for item in minor_raw.split(',') if item.strip()]
        print(uuid_list)
        print(major_list)
        print(minor_list)
    except Exception as e:
        print("Error in /update:", str(e))

    return '6'

@socketio.on('connect')
def on_connect():
    print('Client connected')


@app.route('/login', methods=['GET', 'POST'],endpoint='login')
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="用户名或密码错误")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/start')
def start_stream():
    start_streaming_thread()
    return jsonify({'status': 'started'})

@app.route('/stop')
def stop_stream():
    stop_streaming_thread()
    return jsonify({'status': 'stopped'})


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('ws_web.html')


if __name__ == '__main__':
    # threading.Thread(target=stream_and_emit,daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5004,allow_unsafe_werkzeug=True)
