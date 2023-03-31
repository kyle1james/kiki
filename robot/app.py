import RPi.GPIO as GPIO
from flask import Flask, render_template, Response
import subprocess
import picamera
import io
import time
import cv2
import os

app = Flask(__name__)

# TODO Setup fan controls
img_cnt = 0
# PIR MOTION SENSOR
PIR_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)


# Helpers
def gen():
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        camera.start_preview()
        while True:
            frame = get_frame(camera)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        
def generate_pir_data():
    while True:
        pir_state = GPIO.input(PIR_PIN)
        yield f"data: {pir_state}\n\n"
        time.sleep(0.1)

def get_frame(camera):
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', use_video_port=True)
    frame = stream.getvalue()
    stream.seek(0)
    stream.truncate()
    return frame

def set_servo_pos(pos):
    # setup PWM
    pwm = GPIO.PWM(servo_pin, freq)
    pwm.start(0)
    duty = duty_min + (pos/180)*(duty_max - duty_min)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3) # wait for servo to reach position


# Route for the video stream
@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the capture button
@app.route('/capture')
def capture():
    # Capture a frame from the video stream
    frame = np.empty((480, 640, 3), dtype=np.uint8)
    camera.capture(frame, 'bgr', use_video_port=True)

    # Process the captured image using your Python script
    # Replace this code with your own image processing script
    processed_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('static/processed_image.jpg', processed_image)

    # Display the processed image on a separate page
    return render_template('capture.html', filename='processed_image.jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
