from picamera import PiCamera
from subprocess import Popen, PIPE
import threading
from time import sleep
import os
import fcntl
import cv2
import select
import shutil
import time

import multiprocessing as mp


from mug_glass_detector.track_boxes import track_boxes, alert

iframe = 0

camera = PiCamera()

# Yolo v3 is a full convolutional model. It does not care the size of input image, as long as h and w are multiplication of 32

#camera.resolution = (160,160)
#camera.resolution = (416, 416)
#camera.resolution = (544, 544)
camera.resolution = (608, 608)
#camera.resolution = (608, 288)


camera.capture('frame.jpg')
sleep(0.1)

# spawn darknet process
yolo_proc = Popen(["./darknet",
                   "detect",
                   "./cfg/yolov3-tiny.cfg",
                   "./yolov3-tiny.weights",
                   "-thresh", "0.1"],
                  stdin=PIPE, stdout=PIPE)

fcntl.fcntl(yolo_proc.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)


# oerview of tracking boxes
global tracked_boxes
tracked_boxes = []
# process
p1 = None

stdout_buf = ""
while True:
    try:
        select.select([yolo_proc.stdout], [], [])
        stdout = yolo_proc.stdout.read()
        stdout_buf += stdout
        if 'Enter Image Path' in stdout_buf:
            try:
                im = cv2.imread('predictions.png')
                print(im.shape)
                cv2.imshow('yolov3-tiny', im)
                key = cv2.waitKey(5)
            except Exception as e:
                print("Error:", e)
            camera.capture('frame.jpg')
            yolo_proc.stdin.write('frame.jpg\n')
            stdout_buf = ""
        if "Predicted" in stdout.strip():
            # init first parallel process on first frame
            if p1 == None:
                print('get %s' % stdout)

                # start a new process for tracking
                p1 = mp.Process(target=tracked_boxes, args=(
                    str(stdout), camera.resolution))
                p1.start()

            # join process to main code
            else:
                # finish process, before starting a new process
                p1.join()

                # check tracking summary
                alert()

                print('get %s' % stdout)

                # start a seperate process for tracking
                p1 = mp.Process(target=tracked_boxes, args=(
                    str(stdout), camera.resolution))
                p1.start()

    except Exception as e:
        print("Error:", e)
