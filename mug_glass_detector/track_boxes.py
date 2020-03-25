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


def distance_less_then_threshold(x1,y1, x2, y2, threshold=50):
    dist = math.hypot(x2 - x1, y2 - y2)

    if dist < threshold:
        return True
    else:
        return False


# track boxes based on location and maintaining location
def track_boxes(input_string, frame_res):

    tracked_boxes = []
    #{
    #'center_xy' : [],
    #'label' : [],
    #'gone_for_n_frames': [],
    #'present_for_n_frames' : []
    #}

    detected_boxes = get_boxes(input_string, frame_res)
    print('TEST - Printing box information: ')
    print(detected_boxes)

    # boxes detected 
    if detected_boxes:
        # no tracked boxes
        if not tracked_boxes:
            for box in detected_boxes:
                box['gone_for_n_frames'] = 0
                box['present_for_n_frames'] = 1
                track_boxes.append(box)
        # tracked boxes
        else:
            for box in track_boxes:
                match_found = False
                box_index = None

                for box_idx in range(len(detected_boxes)):
                    new_box = detected_boxes[box_idx]
                    if not match_found and box['label'] == new_box['label'] and distance_less_then_threshold(box['x'], box['y'], new_box['x'], new_box['y']):
                        match_found = True
                        box_index = box_idx
                        box['gone_for_n_frames'] = 0
                        box['present_for_n_frames'] += 1
                
                if match_found:
                    detected_boxes.pop(box_index)
                else:
                    box['gone_for_n_frames'] -= 1
            
            # new boxes not currently tracked
            for box in detected_boxes:
                box['gone_for_n_frames'] = 0
                box['present_for_n_frames'] = 1
                track_boxes.append(box)

    # no boxes detected
    else: 
        if tracked_boxes:
            for box_idx in range(len(tracked_boxes)):
                # remove if counter_threshold reaches -2
                if tracked_boxes[box_idx]['gone_for_n_frames'] == -2:
                    tracked_boxes.pop(box_idx)

    

