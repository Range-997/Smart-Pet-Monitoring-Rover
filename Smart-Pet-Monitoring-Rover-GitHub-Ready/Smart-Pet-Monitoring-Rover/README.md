# Smart Pet Monitoring Rover

Final year project code for a small indoor monitoring rover. The rover uses a Raspberry Pi 4B for the web page, video stream and YOLOv8n target detection, and an Arduino Uno for motor control and obstacle sensor response.

## Main functions

- Browser-based manual control: forward, backward, left, right and stop
- Live USB camera stream through Flask and OpenCV
- Automatic patrol mode
- YOLOv8n target detection using the pretrained COCO model
- Web status update when the teddy bear target is found
- Stop command sent to Arduino when the target is detected
- Basic obstacle response using HC-SR04 and two IR sensors

## Hardware used

- Raspberry Pi 4B
- Arduino Uno
- USB camera
- L298N motor driver
- HC-SR04 ultrasonic sensor
- Two IR obstacle sensors
- DC gear motors and rover chassis
- 7.4 V motor battery pack
- Separate 5 V battery pack for Raspberry Pi

## Pin assignment

| Module | Connection |
|---|---|
| L298N ENA | Arduino D5 |
| L298N ENB | Arduino D6 |
| L298N IN1 | Arduino D8 |
| L298N IN2 | Arduino D9 |
| L298N IN3 | Arduino D10 |
| L298N IN4 | Arduino D11 |
| HC-SR04 TRIG | Arduino D12 |
| HC-SR04 ECHO | Arduino D13 |
| Left IR OUT | Arduino A0 |
| Right IR OUT | Arduino A1 |
| Arduino USB | Raspberry Pi USB port |
| USB camera | Raspberry Pi USB port |

## Raspberry Pi setup

```bash
cd ~/Smart-Pet-Monitoring-Rover/raspberry_pi_code
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open the web page from a browser on the same network:

```text
http://<raspberry-pi-ip>:5000
```

The code uses `/dev/ttyUSB0` by default for Arduino serial communication. If your Arduino appears as `/dev/ttyACM0`, run:

```bash
SERIAL_PORT=/dev/ttyACM0 python3 app.py
```

If the camera is not detected as camera `0`, run for example:

```bash
CAMERA_INDEX=1 python3 app.py
```

## Arduino setup

Open this file in Arduino IDE and upload it to Arduino Uno:

```text
arduino_code/rover_control/rover_control.ino
```

The baud rate is 9600. The serial command protocol is:

| Command | Meaning |
|---|---|
| F | Forward |
| B | Backward |
| L | Left turn |
| R | Right turn |
| S | Stop |
| A | Auto mode |
| M | Manual mode |

## Notes

The YOLO model file `yolov8n.pt` is not included in this repository. Ultralytics will download it automatically when the program is first run, or it can be copied manually into the Raspberry Pi project folder.

This is a prototype-level project for controlled indoor testing. It does not implement SLAM, long-term autonomous navigation, real pet behaviour recognition, or complete security protection.
