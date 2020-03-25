
tracked_boxes = {
    'center_coordinates' : [],
    'label' : [],
    'counter' : [],
    'ticks' : []
}


# input_string
# samples:
# <Enter Image Path: \nget frame.jpg: Predicted in 0.789 seconds. \nBox 0: class <glass/mug>: prob 16%: (x,y)=(0.123,0.123): (w,h)=(0.123,0.123)\n>
#
# Resolve all boxes from string
def get_boxes(input_string):
    all_boxes = []

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

            box['x'], box['y'] = data[3].split('=')[1].split(',')
            box['w'], box['h'] = data[4].split('=')[1].split(',')

            all_boxes.append(box)

    return all_boxes

# track boxes based on location and repeated appearance
def track_boxes(input_string):
    new_boxes = get_boxes(input_string)

    