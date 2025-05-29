# --------------------------------
# WIP
# Calcualating poll_time from n_shots is not working yet.
# --------------------------------

import time
import logging
import numpy as np
from ..base import MeasureStrategy

class SigInAvgMeasure(MeasureStrategy):
    """
    For measuring time-averaged signals into the Zurich Instruments MFLI Sig Input.

    This takes data from the MFLI scope. The averaging is done in the MFLI, and the final
    wave data is returned as a numpy array. For the time domain, a futher averaging is done
    to give a single value. For the frequency domain, the data is left as is for spectral
    analysis.
    """
    
    def __init__(self):
        self.sigin = None
        self.scope_channel_idx = None
        self.scope = None
        self.mode = None  # "avg" or "waveform"
    
    def setup(self, instrument, mode="avg", **kwargs):
        
        self.sigin = instrument.sigins[0]  # There is only one sigin on the MFLI (when both are used, it is for a differential measurement)
        self.scope = instrument.scopes[0]  # There is only one scope on the MFLI
        self.mode = mode.lower()

        self.sigin.float(kwargs.get("float", False))
        self.sigin.ac(kwargs.get("ac", False))
        self.sigin.imp50(kwargs.get("imp50", False))
        self.sigin.diff(kwargs.get("diff", False))
        self.sigin.scaling(kwargs.get("scaling", 1.0))
        if "range" in kwargs:
            self.sigin.range(kwargs["range"])
        else:
            self.sigin.autorange(True)

        # Setup the scope
        self.scope_channel_idx = kwargs.get("scope_channel_idx", 0)
        self.scope.channels[self.scope_channel_idx].inputselect("sigin0")
        self.scope.time(kwargs.get("scope_sampling_rate", 1))  # time, confusingly, defines the sampling rate. See MFLI docs for details
        self.scope.length(kwargs.get("scope_length", 2**14))
        self.scope.wave.subscribe()

    def measure(self, session, poll_time=None, n_shots=None, **kwargs):
        """ Note: averaging should be enabled in the MFLI GUI, this is not done here. """

        # Only one of poll_time or n_shots should be specified
        if poll_time is not None and n_shots is not None:
            raise ValueError("Specify either poll_time or n_shots, not both.")
        elif poll_time is None and n_shots is None:
            raise ValueError("Specify either poll_time or n_shots.")
        
        # Calculate poll_time if n_shots is provided
        if poll_time is not None:
            pass
        elif n_shots is not None and n_shots == 1:
            self.scope.single(True)  # Single shot mode
            # poll_time = 1 * self.scope.length() * self.scope.time()
        else:
            pass
            # poll_time = (n_shots+1) * self.scope.time() / self.scope.length()  # Take one extra shot to ensure no data gets cut off

        logging.debug(f"Polling for {poll_time} seconds.")

        # Ensure sigin is ranged correctly
        # self.scope.enable(True)
        # logging.debug("Autoranging sigin...")
        # time.sleep(0.1)
        # self.sigin.autorange(True)
        # self.scope.enable(False)

        # Then record the data and allow the MFLI to do the averaging
        self.scope.enable(True)

        if "range" in kwargs:
            logging.debug("Ranging sigin...")
            self.sigin.range(kwargs["range"])
        else:
            logging.debug("Autoranging sigin...")
            time.sleep(poll_time)
            self.sigin.autorange(True)

        time.sleep(0.1)
        logging.debug("Collecting data...")
        poll_result = session.poll(poll_time, timeout=1)
        # time.sleep(poll_time)  # Collect data
        self.scope.enable(False)

        # # Collect final wave data *** CHECK FORMAT OF WAVE DATA ***
        # print()
        # print(type(poll_result[self.scope.wave]))
        # print()
        # print(len(poll_result[self.scope.wave]))
        # print()
        # print(poll_result[self.scope.wave][-1])
        # print()
        # print(type(poll_result[self.scope.wave][-1]['wave']))
        # print()
        # print(len(poll_result[self.scope.wave][-1]['wave']))
        # print()
        # print(self.scope_channel_idx)
        # print()
        # print(poll_result[self.scope.wave][-1]['channelscaling'][self.scope_channel_idx])

        # Do further averaging if in "avg" mode
        if self.mode == 'avg':
            avg_over_shot = []
            if poll_result and self.scope.wave in poll_result.keys():
                logging.debug(f"No. of waveforms recorded: {len(poll_result[self.scope.wave])}")
                for shot in poll_result[self.scope.wave]:
                    avg_over_shot.append(np.mean(shot["wave"]) * shot["channelscaling"][0])
                avg_over_all_shots = np.mean(avg_over_shot)
                logging.debug(f"Average Hall voltage over {len(poll_result[self.scope.wave])} shots: {avg_over_all_shots}")
                return avg_over_all_shots
            else:
                logging.info("Error retrieving wave data from MFLI scope.")
                return np.nan
        
        # Return raw wave data if in "waveform" mode
        elif self.mode == "waveform":
            if poll_result and self.scope.wave in poll_result.keys():
                logging.debug(f"No. of waveforms recorded: {len(poll_result[self.scope.wave])}")
                raw_wave_data = poll_result[self.scope.wave][-1]['wave']
                scaling = poll_result[self.scope.wave][-1]['channelscaling'][self.scope_channel_idx]
                wave_data = raw_wave_data * scaling  # Apply the scaling factor to the raw data
                return wave_data.reshape(-1)  # To a 1d array
            else:
                logging.info("Error retrieving wave data from MFLI scope.")
                return np.nan
        
    def reset(self):
        self.scope.wave.unsubscribe()
