# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO
from move_servo import GoRight, GoLeft, rotate_servo

# GPIO variables
pwm_output_pin = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(pwm_output_pin, GPIO.OUT)

# MG996R Frequency: 50Hz
p = GPIO.PWM(pwm_output_pin, 50)
print(p)
p.start(0)
print("Starting Servo")

# PiCamera variables
resolution = [320, 240]
warmuptime = 2.5
fps = 16
minarea = 5000
maxarea = 15000
x_center = resolution[0]/2
y_center = resolution[1]/2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(resolution)
camera.framerate = fps
rawCapture = PiRGBArray(camera, size=tuple(resolution))

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(warmuptime)
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0
deltathresh = 10

face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    frame = f.array
    timestamp = datetime.datetime.now()
    text = "Unoccupied"

    # resize the frame, convert it to grayscale, and blur it
    #frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the average frame is None, initialize it
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, deltathresh, 255,
                           cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)


    # variables for determining the biggest face
    biggestFaceIndex = 0
    index = 0
    max_area = 0
    faces= []
    biggestFace = []
        
    # loop over the contours that have parts moving
    for c in cnts:
        
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < minarea or cv2.contourArea(c) > maxarea:
            continue
        
        ## face detection in case each contour has multiple faces
        gray = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )
        faces = face_cascade.detectMultiScale( gray )
        print("detected faces: ")
        num_faces = len(faces)
        
        for ( x, y, w, h ) in faces:
            if w * h > max_area:
                print("Setting biggest face")
                max_area = w * h
                biggestFaceIndex = index
                biggestFace = faces[biggestFaceIndex]
            index + 1
    # draw the text and timestamp on the frame
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, "Tracking a face".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)
    
    if len(biggestFace) != 0:
        (biggestFace_x, biggestFace_y, biggestFace_w, biggestFace_h) = biggestFace
        cv2.rectangle( frame, ( biggestFace_x, biggestFace_y ), ( biggestFace_x + biggestFace_w , biggestFace_y  + biggestFace_h), ( 200, 255, 0 ), 2 )
        cv2.putText( frame, "Target" , ( biggestFace_x , biggestFace_y  ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )
        biggestFace_x = biggestFace_x + biggestFace_w//2
        rotate_servo(biggestFace_x, x_center, p)
    
    # display the security feed
    cv2.imshow("Watching you :3 uwu", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
