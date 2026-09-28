import os
import time
import threading

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template, request

from camera import CameraStream
from serial_comm import CarSerial

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


SERIAL_PORT = os.getenv('SERIAL_PORT', '/dev/ttyUSB0')
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
FRAME_WIDTH = int(os.getenv('FRAME_WIDTH', '320'))
FRAME_HEIGHT = int(os.getenv('FRAME_HEIGHT', '240'))
MODEL_PATH = os.getenv('YOLO_MODEL', 'yolov8n.pt')
TARGET_CLASS = os.getenv('TARGET_CLASS', 'teddy bear')
DETECT_EVERY_N_FRAMES = int(os.getenv('DETECT_EVERY_N_FRAMES', '5'))

app = Flask(__name__)

car = CarSerial(port=SERIAL_PORT, baudrate=9600, timeout=1.0)
serial_ready = car.connect()

camera = CameraStream(camera_index=CAMERA_INDEX, width=FRAME_WIDTH, height=FRAME_HEIGHT)
camera_ready = camera.open()

model = None
if YOLO is not None:
    try:
        model = YOLO(MODEL_PATH)
        print(f'YOLO model loaded: {MODEL_PATH}')
    except Exception as err:
        print(f'YOLO model not loaded: {err}')
else:
    print('Ultralytics is not installed. Video stream will run without detection.')

state_lock = threading.Lock()
auto_mode = False
target_found = False
last_command = 'S'
last_serial_time = 0.0
frame_count = 0

patrol_steps = [
    ('F', 2.2),
    ('S', 0.4),
    ('L', 0.9),
    ('S', 0.3),
    ('F', 2.2),
    ('S', 0.4),
    ('R', 1.8),
    ('S', 0.3),
]
patrol_index = 0
patrol_step_start = time.time()


def set_state(**kwargs):
    global auto_mode, target_found, last_command
    with state_lock:
        if 'auto_mode' in kwargs:
            auto_mode = kwargs['auto_mode']
        if 'target_found' in kwargs:
            target_found = kwargs['target_found']
        if 'last_command' in kwargs:
            last_command = kwargs['last_command']


def get_state():
    with state_lock:
        return {
            'auto_mode': auto_mode,
            'target_found': target_found,
            'last_command': last_command,
            'serial_ready': car.is_ready(),
            'camera_ready': camera_ready,
            'model_ready': model is not None,
        }


def send_to_car(cmd, min_interval=0.2):
    global serial_ready, last_serial_time
    now = time.time()
    if now - last_serial_time < min_interval and cmd == get_state()['last_command']:
        return True
    if not car.is_ready():
        serial_ready = car.connect()
    if not car.is_ready():
        return False
    ok = car.send_command(cmd)
    if ok:
        last_serial_time = now
        set_state(last_command=cmd)
    return ok


def reset_patrol():
    global patrol_index, patrol_step_start
    patrol_index = 0
    patrol_step_start = time.time()


def current_patrol_command():
    global patrol_index, patrol_step_start
    now = time.time()
    cmd, duration = patrol_steps[patrol_index]
    if now - patrol_step_start >= duration:
        patrol_index = (patrol_index + 1) % len(patrol_steps)
        patrol_step_start = now
        cmd, duration = patrol_steps[patrol_index]
    return cmd


def detect_target(frame):
    if model is None:
        return False, frame
    try:
        results = model.predict(frame, imgsz=320, verbose=False)
    except Exception as err:
        print(f'Detection error: {err}')
        return False, frame

    result = results[0]
    found = False
    if result.boxes is not None and result.boxes.cls is not None:
        for cls_id in result.boxes.cls.tolist():
            name = model.names[int(cls_id)]
            if name == TARGET_CLASS:
                found = True
                break
    annotated = result.plot()
    return found, annotated


def draw_status(frame, found):
    status = get_state()
    mode_text = 'AUTO' if status['auto_mode'] else 'MANUAL'
    target_text = 'TARGET FOUND' if found or status['target_found'] else 'SEARCHING'
    cv2.putText(frame, f'Mode: {mode_text}', (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    cv2.putText(frame, target_text, (10, 52),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                (0, 0, 255) if found or status['target_found'] else (0, 255, 255), 2)
    return frame


def generate_frames():
    global frame_count
    last_annotated = None

    while True:
        frame = camera.read()
        if frame is None:
            frame = np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), 255, dtype=np.uint8)
            cv2.putText(frame, 'Camera not ready', (20, FRAME_HEIGHT // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            time.sleep(0.1)
        else:
            frame_count += 1
            status = get_state()

            if status['auto_mode'] and not status['target_found']:
                cmd = current_patrol_command()
                send_to_car(cmd)

            found_now = False
            if status['auto_mode'] and frame_count % DETECT_EVERY_N_FRAMES == 0:
                found_now, annotated = detect_target(frame)
                if found_now:
                    set_state(target_found=True)
                    send_to_car('S')
                last_annotated = annotated

            if last_annotated is not None and status['auto_mode']:
                frame = last_annotated.copy()
            frame = draw_status(frame, found_now)

        ok, buffer = cv2.imencode('.jpg', frame)
        if not ok:
            continue
        jpg = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/control', methods=['POST'])
def control():
    data = request.get_json(silent=True) or {}
    cmd = str(data.get('cmd', '')).strip().upper()
    cmd_map = {
        'FORWARD': 'F',
        'BACKWARD': 'B',
        'LEFT': 'L',
        'RIGHT': 'R',
        'STOP': 'S',
    }
    if cmd not in cmd_map:
        return jsonify({'ok': False, 'msg': 'invalid command', **get_state()}), 400

    set_state(auto_mode=False, target_found=False)
    send_to_car('M')
    ok = send_to_car(cmd_map[cmd])
    return jsonify({'ok': ok, 'msg': cmd, **get_state()})


@app.route('/mode', methods=['POST'])
def mode():
    data = request.get_json(silent=True) or {}
    enable_auto = bool(data.get('auto', False))

    if enable_auto:
        reset_patrol()
        set_state(auto_mode=True, target_found=False)
        ok = send_to_car('A')
    else:
        set_state(auto_mode=False, target_found=False)
        ok = send_to_car('M')
        send_to_car('S')
    return jsonify({'ok': ok, **get_state()})


@app.route('/status')
def status():
    return jsonify(get_state())


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        send_to_car('S')
        camera.release()
        car.close()
