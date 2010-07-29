#!/usr/bin/python

IS_SMOOTHING = False

import sys, os
from time import time

from wiimote import Wiimote
from gait import GaitAnalyzer

def skipped():
    print "SKIPPED!"
    os.system("osascript -e 'tell application \"iTunes\"' -e 'next track' -e 'end tell' &> /dev/null")
    # os.system("say skipped")
    
def step_frequency_changed(new_frequency):
    print "Step frequency is now %d SPM." % new_frequency

last_pressed = 0
DOUBLECLICK_THRESHOLD = 0.5
def button_pressed():
    global last_pressed
    # skip on doubleclick
    if time() - last_pressed < DOUBLECLICK_THRESHOLD:
        skipped()
    
    last_pressed = time()


if __name__ == '__main__':
    wiimote = Wiimote(button_callback=button_pressed)
    wiimote.pair()
    gait_analyzer = GaitAnalyzer(step_frequency_observer=step_frequency_changed, skip_observer=skipped)

    count = 0
    SMOOTHING_WINDOW = 2
    # array of SMOOTHING_WINDOW*2 + 1 values.
    values = []
    while True:
        if IS_SMOOTHING:
            values.append(wiimote.read_accelerometer())
            # print values
            if len(values) == SMOOTHING_WINDOW * 2 + 1:
                # smooth the values and extract x, y, z
                x = sum([x for x,y,z in values]) / len(values)
                y = sum([y for x,y,z in values]) / len(values)
                z = sum([z for x,y,z in values]) / len(values)
                # add the smoothed value
                gait_analyzer.add_point(x,y,z)
                # remove the first value
                del values[0]
        else:
            x,y,z = wiimote.read_accelerometer()
            gait_analyzer.add_point(x,y,z)

        count += 1
        if count == 1000:
            print "Dumping 1000 frames into CSV"
            # dump the data into a CSV
            f = open('/Users/boris/dump.csv', 'w')
            f.writelines(gait_analyzer.lines_for_csv())
            f.close()
    
        if count % 100 is 0:
            print "Current step frequency: %d" % (hasattr(gait_analyzer, 'step_frequency') and gait_analyzer.step_frequency)
            # print "Last timedeltas: %s" % gait_analyzer.time_deltas[-3:]