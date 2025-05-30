import time
import numpy as np
from ..base import ApplyStrategy

class SigOutDCApply(ApplyStrategy):
    """ For applying DC signals from the Zurich Instruments MFLI signal output """

    def __init__(self):
        self.sigout = None
        self.ramp_pause = 0.05      # Default ramp pause of 50ms
        self.ramp_increment = 0.05  # Default ramp increment of 50mV

    def setup(self, instrument, ramp_pause=0.05, ramp_increment=0.05, init_offset=0.0, **kwargs):

        channel_idx = 0  # There is only one sigout on the MFLI
        self.sigout = instrument.sigouts[channel_idx]
        self.ramp_pause = ramp_pause
        self.ramp_increment = ramp_increment

        [self.sigout.enables[i].value(False) for i in range(4)]  # Disable all AC signals
        self.sigout.on(True)
        self.apply(init_offset)
        self.sigout.add(kwargs.get("add", False))
        self.sigout.diff(kwargs.get("diff", False))
        self.sigout.imp50(kwargs.get("imp50", False))
        if "range" in kwargs:
            self.sigout.range(kwargs["range"])
        else:
            self.sigout.autorange(True)

    def apply(self, offset_target):
        """
        Takes at least 11 steps or increments of ramp_increment (defaults to 50mV), whichever results
        in more steps. The ramp_pause (defaults to 50ms) is the time between each step.
        """
        offset_init = self.sigout.offset()
        if self.ramp_pause > 0:
            diff = abs(offset_init - offset_target)
            n_steps = int(max(np.ceil(diff/self.ramp_increment), 11))
            vals = np.linspace(offset_init, offset_target, n_steps)
            for v in vals:
                self.sigout.offset(v)
                time.sleep(self.ramp_pause)
        else:
            self.sigout.offset(offset_target)
        self.sigout.autorange(True)
    
    def reset(self):
        self.apply(0)  # Reset to 0V
        self.sigout.on(False)
