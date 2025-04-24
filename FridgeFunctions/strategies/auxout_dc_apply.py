import time
import numpy as np
from FridgeFunctions.FridgeFunctions.strategies.base import ApplyStrategy

class AuxOutDCApply(ApplyStrategy):
    """ For applying signals from auxouts 1-4 on the Zurich Instruments MFLI """

    def __init__(self):
        self.auxout = None
        self.ramp_pause = 0.05      # Default ramp pause of 50ms
        self.ramp_increment = 0.05  # Default ramp increment of 50mV

    def setup(self, instrument, channel_idx: int, ramp_pause=0.05, ramp_increment=0.05, init_offset=0.0):
        
        self.auxout = instrument.auxouts[channel_idx]
        if ramp_pause is not None:
            self.ramp_pause = ramp_pause
        if ramp_increment is not None:
            self.ramp_increment = ramp_increment

        self.auxout.outputselect("manual")
        self.auxout.preoffset(0.0)
        self.auxout.scale(1.0)
        self.apply(init_offset)

    def apply(self, offset_target):
        """
        Takes at least 11 steps or increments of ramp_increment (defaults to 50mV), whichever results
        in more steps. The ramp_pause (defaults to 50ms) is the time between each step.
        """

        offset_init = self.auxout.value()
        if self.ramp_pause > 0:
            diff = abs(offset_init - offset_target)
            n_steps = int(max(np.ceil(diff/self.ramp_increment), 11))
            vals = np.linspace(offset_init, offset_target, n_steps)
            for v in vals:
                self.auxout.offset(v)
                time.sleep(self.ramp_pause)
        else:
            self.auxout.offset(offset_target)
    
    def reset(self):
        self.apply(0)
        self.auxout.on(False)
