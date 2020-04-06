import math
import copy

'''
global tracked_boxes

def init_tracked_boxes_var():
    global tracked_boxes
    tracked_boxes = []
'''


# input_string
# samples:
# <Enter Image Path: \nget frame.jpg: Predicted in 0.789 seconds. \nBox 0: class <glass/mug>: prob 16%: (x,y)=(0.123,0.123): (w,h)=(0.123,0.123)\n>
#
# Resolve all boxes from string
def get_boxes(input_string, tracking_boxes):
    frame_res = [416, 416]
    detected_boxes = []

    for n in input_string.split('\n'):
        if 'Box ' in n:
            data = n.split(':')

            if len(data) != 5:
                print("Prediction returened invalid output: ", n)
                print("Expected 4 'colon' seperators, found: ", (len(data) - 1))
                return detected_boxes

            # <Box 0: class <glass/mug>: prob 16%: (x,y)=(0.123,0.123): (w,h)=(0.123,0.123)>
            box = {}

            box['label'] = data[1].strip().split(' ')[1]

            # resolve relative coordinates
            box['x'], box['y'] = data[3].split('=')[1].strip("()").split(',')

            # resolve frame center coordinates
            box['x'] = float(box['x']) * frame_res[0]
            box['y'] = float(box['y']) * frame_res[1]

            # ignore new objects that are located close to already tracking objects, with same label
            if detected_boxes:
                for t_box in tracking_boxes:
                     if box['label'] == t_box['label'] and distance_less_then_threshold(box['x'], box['y'], t_box['x'], t_box['y']):
                        continue

            detected_boxes.append(box)

    return detected_boxes


# check wether distacne between points are less than threshold
def distance_less_then_threshold(x1, y1, x2, y2, threshold=50):
    dist = math.hypot(x2 - x1, y2 - y2)

    if dist < threshold:
        return True
    else:
        return False


# print alert if boxes maintain location
def alert(tracked_boxes):
    #global tracked_boxes
    
    print('ALERT TRACKED_BOXES: ', list(tracked_boxes))
    for idx, box in enumerate(tracked_boxes):
        if box['present_for_n_frames'] >= 3:
            print('')
            print('')
            print('SHAME, SHAME, SHAME')
            print('')
            print('')


# track boxes based on location and persistent location
def track_boxes(input_string, tracked_boxes):
    #global tracked_boxes
    detected_boxes = get_boxes(input_string, tracked_boxes)

    # boxes detected
    if detected_boxes:
        print('detected_boxes: ', detected_boxes)
        # no tracked boxes
        if not tracked_boxes:
            print("init tracked boxes?")
            for d_box in detected_boxes:
                d_box['gone_for_n_frames'] = 0
                d_box['present_for_n_frames'] = 1
                tracked_boxes.append(d_box)
        # tracked boxes
        else:
            remove_boxes_d = []
            tmp_t_boxes_2 = []

            for t_idx, t_box in enumerate(tracked_boxes):
                match_found = False
                
                for d_idx, d_box in enumerate(detected_boxes):
                    # update info on tracked objects still in the frame
                    if not match_found and t_box['label'] == d_box['label'] and distance_less_then_threshold(t_box['x'], t_box['y'], d_box['x'], d_box['y']):
                        match_found = True
                        remove_boxes_d.append(d_idx)
                        
                        box = {}
                        box['label'] = t_box['label']
                        box['x'] = t_box['x']
                        box['y'] = t_box['y']
                        box['gone_for_n_frames'] = 0
                        box['present_for_n_frames'] = t_box['present_for_n_frames'] + 1
                        
                        tmp_t_boxes_2.append(box)
                        

                if not match_found:
                    if t_box['gone_for_n_frames'] > -1:
                        box = {}
                        box['label'] = t_box['label']
                        box['x'] = t_box['x']
                        box['y'] = t_box['y']
                        box['gone_for_n_frames'] =  t_box['gone_for_n_frames'] - 1
                        box['present_for_n_frames'] = t_box['present_for_n_frames']
                        
                        tmp_t_boxes_2.append(box)
                        
            
            for i in range(len(tracked_boxes) - 1, -1, -1):
                tracked_boxes.pop(i)
                
            for tmp_box in tmp_t_boxes_2:
                tracked_boxes.append(tmp_box)

            # start tracking new detected boxes
            for d_idx, d_box in enumerate(detected_boxes):
                if not d_idx in remove_boxes_d:
                    d_box['gone_for_n_frames'] = 0
                    d_box['present_for_n_frames'] = 1
                    tracked_boxes.append(d_box)

    # no boxes detected
    else:
        if tracked_boxes:
            tmp_t_boxes_2 = []
            for t_idx, t_box in enumerate(tracked_boxes):
                # remove if counter_threshold is about to reach -2
                if t_box['gone_for_n_frames'] > -1:
                    box = {}
                    box['label'] = t_box['label']
                    box['x'] = t_box['x']
                    box['y'] = t_box['y']
                    box['gone_for_n_frames'] =  t_box['gone_for_n_frames'] - 1
                    box['present_for_n_frames'] = t_box['present_for_n_frames']
                    
                    tmp_t_boxes_2.append(box)
                    
            for i in range(len(tracked_boxes) - 1, -1, -1):
                tracked_boxes.pop(i)
                
            for tmp_box in tmp_t_boxes_2:
                tracked_boxes.append(tmp_box)
