



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
            box['%'] = data[2][7:]

            # resolve relative coordinates
            box['x'], box['y'] = data[3].split('=')[1].split(',')
            box['w'], box['h'] = data[4].split('=')[1].split(',')

            # resolve frame coordinates
            box['x'] = box['x'] * frame_res[0]
            box['y'] = box['y'] * frame_res[1]
            box['w'] = box['w'] * frame_res[0]
            box['h'] = box['h'] * frame_res[1]

            detected_boxes.append(box)

    return detected_boxes



# track boxes based on location and repeated appearance
def track_boxes(input_string, frame_res):

    tracked_boxes = {
        'center_coordinates' : [],
        'label' : [],
        'counter' : [],
        'ticks' : []
        }

    detected_boxes = get_boxes(input_string, frame_res)
    print('TEST - Printing box information: ')
    print(detected_boxes)

    # detected boxes
    if detected_boxes:
        # there are boxes we are tracking already
        if tracked_boxes['center_coordinates']:
            pass
        # new boxes we have not tracked yet
        else:
            pass
    # no new boxes
    else: 

    

