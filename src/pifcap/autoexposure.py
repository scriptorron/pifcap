"""
automatic exposure time optimization
"""

import numpy as np

settings = {'name': 'automatic exposure', 'type': 'group', 'children': [
    {
        'name': 'target exposure', 'type': 'int', 'value': 80, 'limits': [1, 100], 'suffix': ' %',
        'tip': 'exposure target in % of full-scale',
    },
    {
        'name': 'allowed overexposed pixel', 'type': 'float', 'value': 0.1, 'limits': [0, 100], 'suffix': ' %',
        'tip': '% of pixels allowed to be overexposed (for instance defective pixel)',
    },
    {
        'name': 'number of iterations', 'type': 'int', 'value': 15, 'limits': [0, 100], 'suffix': ' frames',
        'tip': 'number of optimization iterations',
    },
    {
        'name': 'learning rate', 'type': 'float', 'value': 1.0, 'limits': [0.1, 1.9],
    },
    {
        'name': 'saturation rate', 'type': 'float', 'value': 8.0, 'limits': [1, 64],
    },
]}

class AutoExposure():
    def __init__(self, Settings):
        self.Settings = Settings
        self.init_optimize()

    def init_optimize(self):
        #print("DBG: init_optimize")
        self.iteration = 0

    def do_optimize(self, array, ExposureTime, n_bits, MinExposureTime, MaxExposureTime):
        """optimize exposure time

        @param array: image array
        @param ExposureTime: exposure time used to capture array
        @param n_bits: number of bits used in array
        @param MinExposureTime: minimum allowed exposure time
        @param MaxExposureTime: maximum allowed exposure time
        @return: (finished, new exposure time)
        """
        finished = True
        newExposureTime = ExposureTime
        if self.iteration < self.Settings.get('automatic exposure', 'number of iterations'):
            self.iteration += 1
            finished = False
            currentExposure = np.percentile(
                array,
                100 - self.Settings.get('automatic exposure', 'allowed overexposed pixel')
            )
            targetExposure = self.Settings.get('automatic exposure', 'target exposure') / 100 * (2 ** n_bits)
            #print(f'DBG: in do_optimize: {currentExposure=}, {targetExposure=}')
            if currentExposure < targetExposure:
                if ExposureTime <= 0:
                    newExposureTime = 0.01
                elif currentExposure <= 0:
                    # underexposed and saturated
                    newExposureTime = ExposureTime * self.Settings.get('automatic exposure', 'saturation rate')
                else:
                    newExposureTime = (ExposureTime +
                                       self.Settings.get('automatic exposure', 'learning rate') *
                                       (ExposureTime * targetExposure / currentExposure - ExposureTime)
                                       )
            else:
                n_saturated = (array >= ((2 ** n_bits) - 1)).sum()
                #print(f'DBG: in do_optimize: {n_saturated=}, {self.Settings.get("automatic exposure", "allowed overexposed pixel") / 100 * array.size}')
                if n_saturated > self.Settings.get('automatic exposure', 'allowed overexposed pixel') / 100 * array.size:
                    # overexposed and saturated
                    newExposureTime = ExposureTime / self.Settings.get('automatic exposure', 'saturation rate')
                else:
                    newExposureTime = (ExposureTime +
                                       self.Settings.get('automatic exposure', 'learning rate') *
                                       (ExposureTime * targetExposure / currentExposure - ExposureTime)
                                       )
        #print(f'DBG: in do_optimize: {ExposureTime=}, {newExposureTime=}')
        return finished, min(max(newExposureTime, MinExposureTime), MaxExposureTime)





