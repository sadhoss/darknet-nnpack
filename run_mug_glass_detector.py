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


import track_boxes

iframe = 0

camera = PiCamera()

# Yolo v3 is a full convolutional model. It does not care the size of input image, as long as h and w are multiplication of 32

#camera.resolution = (160,160)
camera.resolution = (416, 416)
camera_res = [416, 416]
#camera.resolution = (544, 544)
#camera.resolution = (608, 608)
#camera.resolution = (608, 288)


camera.capture('frame.jpg')
sleep(0.1)

# spawn darknet process
yolo_proc = Popen(["./darknet",
                   "detector",
                   "test",
                   "ddd_yolov3_tiny/ddd.data",
                   "ddd_yolov3_tiny/yolov3-tiny-ddd.cfg",
                   "ddd_yolov3_tiny/yolov3-tiny-ddd_best.weights",
                   "-thresh","0.1"],
                  stdin=PIPE, stdout=PIPE)

fcntl.fcntl(yolo_proc.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)


#track_boxes.init_tracked_boxes_var()

manager = mp.Manager()
tracked_boxes = manager.list()
# [{'x' : -1, 'y' : -1, 'label' : '-1', 'gone_for_n_frames' : 3, 'present_for_n_frames' : -1}]

stdout_buf = ''
p1 = None

while True:
    try:
        select.select([yolo_proc.stdout], [], [])
        stdout = yolo_proc.stdout.read()
        stdout_buf += stdout
        if 'Enter Image Path' in stdout_buf:
            try:
                im = cv2.imread('predictions.png')
                #print(im.shape)
                cv2.imshow('yolov3-tiny', im)
                key = cv2.waitKey(5)
            except Exception as e:
                print("Error:", e)
            camera.capture('frame.jpg')
            yolo_proc.stdin.write('frame.jpg\n')
            stdout_buf = ""
            
        #if len(stdout.strip()) > 0:
            print('get %s' % stdout)
            #temp_str = str(stdout)
            # init first parallel process on first frame
            if p1 == None:
                # start a new process for tracking
                p1 = mp.Process(target=track_boxes.track_boxes, args=(stdout, tracked_boxes))
                p1.start()

            # join process to main code
            else:
                # finish process, before starting a new process
                p1.join()
                
                print("")
                # check tracking summary
                track_boxes.alert(tracked_boxes)

                # start new tracking process
                p1 = mp.Process(target=track_boxes.track_boxes, args=(stdout, tracked_boxes))
                p1.start()

    except Exception as e:
        print("Error:", e)
