#!/usr/bin/python
# 
# This program drives a user test. There are three conditions:
#   1. Phone case (skip using wiimote button, simulating phone)
#   2. Headphone case (skip using headphone button)
#   3. Skip case (skip by skipping while running)
#
# problem in case 2 of intercepting headphone clicks: need to monitor current iTunes track... :|
#   1. poll iTunes (slow)
#   2. record track change time manually
# 
# ok so human operated: enter triggers a skip. enter again triggers a "skip successful" 
# (this may not be precise enough...)
#
# if not precise enough, need a way to intercept bluetooth signals
import os
from time import time


skips = []
try:
    while True:
        i = raw_input("Initiate skip [enter]: ")
        os.system('say skip')
        start = time()
        i = raw_input("Skip completed [enter]: ")
        end = time()
    
        duration = end - start
        print "Skip took %.4f seconds" % duration
        skips.append(duration)
except KeyboardInterrupt:
    print '\nSkip durations: ' + ", ".join([str(s) for s in skips])