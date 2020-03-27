import math


# input_string
# samples:
# <Enter Image Path: \nget frame.jpg: Predicted in 0.789 seconds. \nBox 0: class <glass/mug>: prob 16%: (x,y)=(0.123,0.123): (w,h)=(0.123,0.123)\n>
#
# Resolve all boxes from string
def get_boxes(input_string, frame_res):
    detected_boxes = []

    for n in input_string.split('\n'):
        if 'Box ' in n:
            data = n.split(':')

            if len(data) != 5:
                print("Prediction returened invalid output: ", n)
                print("Expected 4 'colon' seperators, found: ", (len(data) - 1))
                quit()

            # <Box 0: class <glass/mug>: prob 16%: (x,y)=(0.123,0.123): (w,h)=(0.123,0.123)>
            box = {}

            box['label'] = data[1][8:]

            # resolve relative coordinates
            box['x'], box['y'] = data[3].split('=')[1].split(',')

            # resolve frame center coordinates
            box['x'] = float(box['x']) * frame_res[0]
            box['y'] = float(box['y']) * frame_res[1]

            # ignore new objects that are located close to already tracking objects, with same label
            if detected_boxes:
                for tracking_box in detected_boxes:
                    if box['label'] == tracking_box['label'] and distance_less_then_threshold(box['x'], box['y'], tracking_box['x'], tracking_box['y']):
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
    for box in track_boxes:
        if box['present_for_n_frames'] == 3:
            print('')
            print('')
            print('SHAME, SHAME, SHAME')
            print('')
            print('')


# track boxes based on location and maintaining location
def track_boxes(input_string, frame_res, tracked_boxes):
    detected_boxes = get_boxes(input_string, frame_res)
    print('TEST - Printing box information: ')
    print(detected_boxes)

    # boxes detected
    if detected_boxes:
        # no tracked boxes
        if not tracked_boxes:
            for d_box in detected_boxes:
                d_box['gone_for_n_frames'] = 0
                d_box['present_for_n_frames'] = 1
                track_boxes.append(d_box)
        # tracked boxes
        else:
            remove_boxes = []
            for t_idx, t_box in enumerate(track_boxes):
                match_found = False
                box_index = None

                for d_idx, d_box in detected_boxes:
                    # update info on tracked objects still in the frame
                    if not match_found and t_box['label'] == d_box['label'] and distance_less_then_threshold(t_box['x'], t_box['y'], d_box['x'], d_box['y']):
                        match_found = True
                        box_index = d_idx
                        t_box['gone_for_n_frames'] = 0
                        t_box['present_for_n_frames'] += 1

                # remove matching objects from detect list
                if match_found:
                    detected_boxes.pop(box_index)
                # count down tracked objects not detected
                else:
                    t_box['gone_for_n_frames'] -= 1
                    if t_box['gone_for_n_frames'] <= -2:
                        remove_boxes.append(t_idx)

            # remove tracked objects gone for 3 consecutive frames
            for idx in reversed(remove_boxes):
                tracked_boxes.pop(idx)

            # start tracking new detected boxes
            for d_box in detected_boxes:
                d_box['gone_for_n_frames'] = 0
                d_box['present_for_n_frames'] = 1
                track_boxes.append(d_box)

    # no boxes detected
    else:
        if tracked_boxes:
            remove_boxes = []
            for t_idx, box in tracked_boxes:
                # remove if counter_threshold is about to reach -2
                if box['gone_for_n_frames'] == -1:
                    remove_boxes.append(t_idx)
                # count number of frames tracked object has been gone for
                else:
                    box['gone_for_n_frames'] -= 1

            for idx in reversed(remove_boxes):
                tracked_boxes.pop(idx)
