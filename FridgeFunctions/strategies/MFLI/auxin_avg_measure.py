import numpy as np
from FridgeFunctions.FridgeFunctions.strategies.base import MeasureStrategy

class AuxInAvgMeasure(MeasureStrategy):
    """ For measuring time-averaged signals into the Zurich Instruments MFLI Aux Input """

    def __init__(self):
        self.auxin = None

    def setup(self, instrument, averaging=0):

        channel_idx = 0  # There is only one auxin on the MFLI
        self.auxin = instrument.auxins[channel_idx]
        self.auxin.averaging(averaging)
        self.auxin.sample.subscribe()
    
    def measure(self, session, poll_time):

        poll_result = session.poll(poll_time, timeout=1)
        if poll_result and self.auxin.sample in poll_result.keys():
            samples = poll_result[self.auxin.sample]["auxin0"]
            V_in_avg = np.mean(samples)
        else:
            V_in_avg = np.nan
        return V_in_avg

    def reset(self):
        self.auxin.sample.unsubscribe()
