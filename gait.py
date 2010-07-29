from time import time

# what minimum value constitutes a peak
PEAK_THRESHOLD = 55
# minimum distance between two peaks
MIN_TIME_DELTA_THRESHOLD = 0.2
# what +/- range of values constitutes the same frequency (in steps per minute)
STEP_FREQUENCY_THRESHOLD = 0.2
# what +/- range of time values constitutes a skip
SKIP_THRESHOLD = 0.1
# minimum time between skips
MIN_SKIP_TIME_THRESHOLD = 2
# number of time deltas to use to compute pace
MAX_DELTAS = 5
# what amount of stride is the skip?
SKIP_STRIDE = 0.7

class GaitAnalyzer:
    """Analyzes gait based on accelerometer data"""
    
    def __init__(self, step_frequency_observer, skip_observer):
        """Initializer registers callbacks
        
        Gait observer fires whenever the step frequency changes.
        Skip observer fires whenever a skip is detected."""
        # accelerometer data
        self.data = []
        # peaks in the readings
        self.peaks = []
        # 't' deltas between the peaks
        self.time_deltas = []
        
        # register observers
        self.step_frequency_observer = step_frequency_observer
        self.skip_observer = skip_observer
        
        self.start_time = time()
        
        self.last_skip_time = 0
    
    def add_point(self, x, y, z):
        """Add an accelerometer data point"""
        self.data.append({'x': x, 'y': y, 'z': z, 't': time() - self.start_time})
        self.find_new_peaks()
        self.compute_step_frequency()
        self.detect_skips()
        
    def find_new_peaks(self, axis='y'):
        """Look for peaks in the last few frames. Also update the time deltas list"""
        # if there's not enough data, don't do anything
        if len(self.data) < 3:
            return
        
        pre, peak, post = self.data[-3:]
        # compute the slope of the left side and the right side
        left_slope  = (peak[axis] - pre[axis]) / (peak['t'] - pre['t'])
        right_slope = (post[axis] - peak[axis]) / (post['t'] - peak['t'])
        
        if left_slope < 0 and right_slope > 0:
            # found a peak. is it significant?
            # print "Potential peak: %d." % peak[axis]
            if peak[axis] < PEAK_THRESHOLD:
                print "Found a peak at t = %d, %s = %d" % (peak['t'], axis, peak[axis])
                if self.peaks:
                    delta = peak['t'] - self.peaks[-1]['t']
                    # check that it's sufficiently far from the previous peak
                    if delta > MIN_TIME_DELTA_THRESHOLD:
                        self.time_deltas.append(delta)
                        self.peaks.append(peak)
                    
                else:
                    self.peaks.append(peak)
        
    def compute_step_frequency(self):
        """Compute the step frequency based on the mode across time deltas"""
        if not self.time_deltas:
            return
        
        # go through all time deltas and check for proximity
        # create a value:count dictionary
        frequencies = {self.time_deltas[0]: 0}
        # frequencies = dict(zip(self.time_deltas, [0]*len(self.time_deltas)))
        
        for delta in self.time_deltas[-MAX_DELTAS:]:
            
            is_close = False
            # go through the frequency count table
            for freq in frequencies:
                # check if this time delta is close to something in the table
                if abs(freq - delta) < STEP_FREQUENCY_THRESHOLD:
                    # if it is, increment the count
                    frequencies[freq] += 1
                    is_close = True
                    break
            
            if not is_close:
                # otherwise, insert the delta into the dictionary with a 1 count.
                frequencies[delta] = 1
        
        # now we have a built frequency table, so the mode is the one with 
        # the largest count
        items = frequencies.items()
        items.sort(lambda a,b: cmp(b[1], a[1]))
        mode = items[0][0]
        
        # convert to steps per minute
        step_frequency = int(60/mode)
        if hasattr(self, 'step_frequency') and step_frequency is not self.step_frequency:
            self.step_frequency_observer(step_frequency)
            
        self.step_frequency = step_frequency
        self.mode_time_between_peaks = mode
        
    def detect_skips(self):
        """Check for unexpected spikes at roughly double frequency"""
        # get the mode time between peaks
        if not hasattr(self, 'mode_time_between_peaks'):
            return
            
        # compare the last time between peaks to the mode.
        if abs(self.time_deltas[-1] - self.mode_time_between_peaks*SKIP_STRIDE) < SKIP_THRESHOLD:
            # print "Mode time between peaks is %d" % self.mode_time_between_peaks
            # only fire the skip observer if enough time has passed since the last skip.
            now = time()
            if (now - self.last_skip_time) > MIN_SKIP_TIME_THRESHOLD:
                # do skipped!
                self.last_skip_time = now
                self.skip_observer()
                # remove the skip so it doesn't incur further skips
                # and affect the pacing
                del self.time_deltas[-1]
        
    def lines_for_csv(self):
        if not self.data:
            return
        
        lines = []
        # create header line
        lines.append(",".join(self.data[0].keys()) + '\n')
        # create value lines
        for d in self.data:
            lines.append(','.join([str(v) for v in d.values()]) + '\n')
            
        return lines
